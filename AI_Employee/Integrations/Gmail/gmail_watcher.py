# Gmail Watcher - Silver Tier Integration
# Continuous polling for unread important emails

import os
import time
import logging
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Paths
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')
NEEDS_ACTION_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Needs_Action')

# Polling interval in seconds
POLL_INTERVAL = 120

# Track processed message IDs
processed_ids = set()


def get_gmail_service():
    """Authenticate and build Gmail service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def create_email_md(email_data):
    """Create markdown file for email in Needs_Action folder."""
    filename = f"email_{email_data['id']}.md"
    filepath = os.path.join(NEEDS_ACTION_DIR, filename)
    
    content = f"""---
type: email
from: {email_data['from']}
subject: {email_data['subject']}
received: {email_data['received']}
---
Snippet: {email_data['snippet']}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Created email file: {filename}")


def get_email_details(service, message_id):
    """Fetch email details from Gmail."""
    message = service.users().messages().get(userId='me', id=message_id).execute()
    
    headers = message['payload']['headers']
    from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
    
    snippet = message.get('snippet', '')
    received = datetime.fromtimestamp(int(message['internalDate']) / 1000).isoformat()
    
    return {
        'id': message_id,
        'from': from_addr,
        'subject': subject,
        'received': received,
        'snippet': snippet
    }


def check_emails():
    """Check for new unread important emails."""
    try:
        service = get_gmail_service()
        
        # Query for unread AND important emails
        results = service.users().messages().list(
            userId='me',
            q='is:unread is:important',
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            logger.info("No new unread important emails found.")
            return
        
        logger.info(f"Found {len(messages)} unread important email(s).")
        
        for message in messages:
            msg_id = message['id']
            
            # Skip already processed messages
            if msg_id in processed_ids:
                continue
            
            try:
                email_data = get_email_details(service, msg_id)
                create_email_md(email_data)
                processed_ids.add(msg_id)
                
                # Mark as read after successfully creating markdown file
                service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
    
    except FileNotFoundError:
        logger.error("credentials.json not found. Please add your Gmail API credentials.")
    except Exception as e:
        logger.error(f"Error checking emails: {e}")


def main():
    """Main polling loop."""
    logger.info("Gmail Watcher starting...")
    
    # Ensure Needs_Action directory exists
    os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
    
    while True:
        try:
            check_emails()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    print("Gmail Watcher ready")
    main()
