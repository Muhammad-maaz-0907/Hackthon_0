# Gmail MCP Server - Gold Tier
# Gmail API integration via MCP protocol

import os
import json
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Handle both module import and direct execution
try:
    from .mcp_server_base import MCPServerBase, MCPResponse
except ImportError:
    from mcp_server_base import MCPServerBase, MCPResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Paths
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'Integrations', 'Gmail', 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'Integrations', 'Gmail', 'token.json')


class GmailMCPServer(MCPServerBase):
    """
    MCP Server for Gmail operations.
    
    Actions:
        - send_email: Send an email
        - read_unread: Get unread emails
        - search_email: Search emails with query
    """
    
    def __init__(self):
        super().__init__("gmail_mcp", max_retries=3, retry_delay=1.0)
        self.service = None
    
    def connect(self, **kwargs) -> Dict:
        """
        Connect to Gmail API.
        
        Returns:
            Dict: Connection status
        """
        try:
            logger.info("[GmailMCP] Connecting to Gmail API...")
            
            creds = None
            if os.path.exists(TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_FILE):
                        return MCPResponse.error(
                            "credentials.json not found. Please add Gmail API credentials.",
                            "connect"
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            self.connected = True
            
            logger.info("[GmailMCP] Connected successfully")
            return MCPResponse.success({
                "service": "gmail",
                "status": "connected",
                "user": self._get_user_email()
            }, "connect")
            
        except Exception as e:
            self.connected = False
            logger.error(f"[GmailMCP] Connection failed: {e}")
            return self.handle_error(e, "connect")
    
    def _get_user_email(self) -> str:
        """Get authenticated user's email address."""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress', 'unknown')
        except Exception:
            return 'unknown'
    
    def disconnect(self) -> Dict:
        """Disconnect from Gmail API."""
        try:
            self.service = None
            self.connected = False
            logger.info("[GmailMCP] Disconnected")
            return MCPResponse.success({"status": "disconnected"}, "disconnect")
        except Exception as e:
            return self.handle_error(e, "disconnect")
    
    def _execute_action(self, action: str, payload: Dict) -> Dict:
        """
        Execute Gmail action.
        
        Args:
            action: Action name
            payload: Action parameters
            
        Returns:
            Dict: MCPResponse formatted result
        """
        if not self.connected:
            connect_result = self.connect()
            if connect_result.get('status') == 'error':
                return connect_result
        
        if action == 'send_email':
            return self._send_email(payload)
        elif action == 'read_unread':
            return self._read_unread(payload)
        elif action == 'search_email':
            return self._search_email(payload)
        else:
            return MCPResponse.error(f"Unknown action: {action}", action)
    
    def _send_email(self, payload: Dict) -> Dict:
        """
        Send an email.
        
        Payload:
            - to: Recipient email address
            - subject: Email subject
            - body: Email body text
            - cc: (optional) CC recipients
        """
        try:
            to = payload.get('to')
            subject = payload.get('subject')
            body = payload.get('body')
            cc = payload.get('cc')
            
            if not to or not subject:
                return MCPResponse.error(
                    "Missing required fields: 'to' and 'subject'",
                    "send_email"
                )
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
            message.attach(MIMEText(body, 'plain'))
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"[GmailMCP] Email sent to {to}")
            return MCPResponse.success({
                "message_id": sent_message['id'],
                "to": to,
                "subject": subject,
                "status": "sent"
            }, "send_email")
            
        except HttpError as error:
            logger.error(f"[GmailMCP] Send email error: {error}")
            return self.handle_error(error, "send_email", {
                "error_details": str(error)
            })
        except Exception as e:
            logger.error(f"[GmailMCP] Send email error: {e}")
            return self.handle_error(e, "send_email")
    
    def _read_unread(self, payload: Dict) -> Dict:
        """
        Read unread emails.
        
        Payload:
            - max_results: Maximum emails to return (default: 10)
            - label: Optional label to filter (default: INBOX)
        """
        try:
            max_results = payload.get('max_results', 10)
            label = payload.get('label', 'INBOX')
            
            results = self.service.users().messages().list(
                userId='me',
                q=f'label:{label} is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return MCPResponse.success({
                    "count": 0,
                    "messages": [],
                    "label": label
                }, "read_unread")
            
            email_list = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    email_list.append(email_data)
            
            logger.info(f"[GmailMCP] Found {len(email_list)} unread emails")
            return MCPResponse.success({
                "count": len(email_list),
                "messages": email_list,
                "label": label
            }, "read_unread")
            
        except HttpError as error:
            logger.error(f"[GmailMCP] Read unread error: {error}")
            return self.handle_error(error, "read_unread")
        except Exception as e:
            logger.error(f"[GmailMCP] Read unread error: {e}")
            return self.handle_error(e, "read_unread")
    
    def _search_email(self, payload: Dict) -> Dict:
        """
        Search emails with query.
        
        Payload:
            - query: Gmail search query
            - max_results: Maximum results (default: 10)
        """
        try:
            query = payload.get('query')
            max_results = payload.get('max_results', 10)
            
            if not query:
                return MCPResponse.error(
                    "Missing required field: 'query'",
                    "search_email"
                )
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            email_list = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    email_list.append(email_data)
            
            logger.info(f"[GmailMCP] Search '{query}' found {len(email_list)} results")
            return MCPResponse.success({
                "query": query,
                "count": len(email_list),
                "messages": email_list
            }, "search_email")
            
        except HttpError as error:
            logger.error(f"[GmailMCP] Search error: {error}")
            return self.handle_error(error, "search_email")
        except Exception as e:
            logger.error(f"[GmailMCP] Search error: {e}")
            return self.handle_error(e, "search_email")
    
    def _get_email_details(self, message_id: str) -> Optional[Dict]:
        """Get email details by message ID."""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id
            ).execute()
            
            headers = message['payload']['headers']
            from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
            
            snippet = message.get('snippet', '')
            received = datetime.fromtimestamp(int(message['internalDate']) / 1000).isoformat()
            
            return {
                'id': message_id,
                'from': from_addr,
                'subject': subject,
                'date': date,
                'received': received,
                'snippet': snippet
            }
        except Exception as e:
            logger.error(f"[GmailMCP] Error getting email details: {e}")
            return None


# Convenience function
def execute(action: str, payload: Dict) -> Dict:
    """Execute Gmail action."""
    server = GmailMCPServer()
    return server.execute(action, payload)


if __name__ == '__main__':
    print("Gmail MCP Server - Gold Tier")
    print("=" * 40)
    
    server = GmailMCPServer()
    
    print("\n1. Testing connection:")
    result = server.connect()
    print(json.dumps(result, indent=2))
    
    print("\n2. Testing health check:")
    result = server.health_check()
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 40)
