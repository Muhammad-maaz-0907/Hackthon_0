# Operations Skill - Gold Tier
# Handle Gmail, WhatsApp tasks and inbound requests

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Handle both module import and direct execution
try:
    from .agent_skill_base import AgentSkill, AgentSkillResponse
except ImportError:
    from agent_skill_base import AgentSkill, AgentSkillResponse

# Import MCP servers
try:
    from ..MCP.gmail_mcp import GmailMCPServer
    from ..MCP.whatsapp_mcp import WhatsAppMCPServer
except ImportError:
    from MCP.gmail_mcp import GmailMCPServer
    from MCP.whatsapp_mcp import WhatsAppMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
NEEDS_ACTION_DIR = os.path.join(os.path.dirname(__file__), '..', 'Needs_Action')
INBOUND_LOG = os.path.join(DATA_DIR, 'inbound_requests.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)


class OperationsSkill(AgentSkill):
    """
    Operations skill for handling inbound communications and tasks.
    
    Capabilities:
    - Process Gmail tasks and responses
    - Handle WhatsApp messages
    - Process inbound requests
    - Auto-categorize and prioritize tasks
    """
    
    def __init__(self):
        super().__init__("operations_skill", tier="gold")
        
        # Initialize MCP servers
        self.gmail = GmailMCPServer()
        self.whatsapp = WhatsAppMCPServer()
        
        # Priority keywords
        self.priority_keywords = {
            'urgent': ['urgent', 'asap', 'emergency', 'critical', 'immediate'],
            'high': ['important', 'priority', 'deadline', 'soon'],
            'normal': ['request', 'question', 'info', 'help']
        }
        
        # Auto-response templates
        self.auto_responses = {
            'acknowledgment': "Thank you for your message. We've received your request and will respond within 24 hours.",
            'out_of_office': "Thank you for contacting us. We're currently out of office and will respond when we return.",
            'meeting_request': "Thank you for your meeting request. Please use our calendar link to schedule: [CALENDAR_LINK]"
        }
    
    def validate(self, context: Dict) -> tuple:
        """Validate operations context."""
        action = context.get('action')
        valid_actions = [
            'process_gmail', 'process_whatsapp', 'process_inbound',
            'get_unread', 'send_response', 'categorize', 'prioritize'
        ]
        
        if not action:
            return False, "Missing required field: 'action'"
        
        if action not in valid_actions:
            return False, f"Invalid action. Must be one of: {valid_actions}"
        
        return True, None
    
    def execute(self, context: Dict) -> Dict:
        """
        Execute operations skill.
        
        Context:
            - action: process_gmail | process_whatsapp | process_inbound | get_unread | send_response | categorize | prioritize
            - email_address: (optional) Specific email to process
            - phone_number: (optional) Specific phone to message
            - message: (optional) Response message
            - template: (optional) Response template name
        """
        action = context.get('action')
        
        if action == 'process_gmail':
            return self._process_gmail(context)
        elif action == 'process_whatsapp':
            return self._process_whatsapp(context)
        elif action == 'process_inbound':
            return self._process_inbound(context)
        elif action == 'get_unread':
            return self._get_unread(context)
        elif action == 'send_response':
            return self._send_response(context)
        elif action == 'categorize':
            return self._categorize(context)
        elif action == 'prioritize':
            return self._prioritize(context)
        else:
            return AgentSkillResponse.error(f"Unknown action: {action}", self.skill_name)
    
    def _process_gmail(self, context: Dict) -> Dict:
        """Process Gmail unread emails."""
        max_results = context.get('max_results', 10)
        auto_respond = context.get('auto_respond', False)
        
        # Connect to Gmail
        connect_result = self.gmail.connect()
        if connect_result.get('status') == 'error':
            return AgentSkillResponse.error(
                "Failed to connect to Gmail",
                self.skill_name,
                {"gmail_error": connect_result.get('error')}
            )
        
        # Get unread emails
        result = self.gmail.execute('read_unread', {
            "max_results": max_results
        })
        
        if result.get('status') != 'success':
            return AgentSkillResponse.error(
                "Failed to read unread emails",
                self.skill_name,
                {"gmail_error": result.get('error')}
            )
        
        emails_data = result.get('data', {})
        messages = emails_data.get('messages', [])
        
        processed = []
        for email in messages:
            # Categorize email
            category = self._categorize_content(email.get('snippet', ''))
            priority = self._determine_priority(email.get('snippet', ''))
            
            processed_email = {
                'id': email.get('id'),
                'from': email.get('from'),
                'subject': email.get('subject'),
                'snippet': email.get('snippet'),
                'category': category,
                'priority': priority,
                'processed_at': datetime.now().isoformat()
            }
            
            # Auto-respond if enabled
            if auto_respond and category == 'inquiry':
                response = self._send_auto_response(
                    email.get('from'),
                    email.get('subject'),
                    'acknowledgment'
                )
                processed_email['auto_response'] = response
            
            processed.append(processed_email)
            
            # Log inbound request
            self._log_inbound_request('email', processed_email)
        
        logger.info(f"Processed {len(processed)} Gmail messages")
        
        return AgentSkillResponse.success({
            "source": "gmail",
            "processed_count": len(processed),
            "messages": processed
        }, self.skill_name)
    
    def _process_whatsapp(self, context: Dict) -> Dict:
        """Process WhatsApp messages."""
        limit = context.get('limit', 10)
        
        # Get WhatsApp messages
        result = self.whatsapp.execute('read_messages', {
            "limit": limit
        })
        
        if result.get('status') != 'success':
            return AgentSkillResponse.error(
                "Failed to read WhatsApp messages",
                self.skill_name,
                {"whatsapp_error": result.get('error')}
            )
        
        messages_data = result.get('data', {})
        messages = messages_data.get('messages', [])
        
        processed = []
        for msg in messages:
            # Categorize message
            category = self._categorize_content(msg.get('content', ''))
            priority = self._determine_priority(msg.get('content', ''))
            
            processed_msg = {
                'id': msg.get('id'),
                'from': msg.get('from'),
                'content': msg.get('content'),
                'timestamp': msg.get('timestamp'),
                'category': category,
                'priority': priority,
                'processed_at': datetime.now().isoformat()
            }
            
            processed.append(processed_msg)
            
            # Log inbound request
            self._log_inbound_request('whatsapp', processed_msg)
        
        logger.info(f"Processed {len(processed)} WhatsApp messages")
        
        return AgentSkillResponse.success({
            "source": "whatsapp",
            "processed_count": len(processed),
            "messages": processed
        }, self.skill_name)
    
    def _process_inbound(self, context: Dict) -> Dict:
        """Process all inbound requests."""
        # Process both Gmail and WhatsApp
        gmail_result = self._process_gmail({"max_results": 10})
        whatsapp_result = self._process_whatsapp({"limit": 10})
        
        return AgentSkillResponse.success({
            "gmail": gmail_result.get('data', {}),
            "whatsapp": whatsapp_result.get('data', {}),
            "total_processed": (
                gmail_result.get('data', {}).get('processed_count', 0) +
                whatsapp_result.get('data', {}).get('processed_count', 0)
            )
        }, self.skill_name)
    
    def _get_unread(self, context: Dict) -> Dict:
        """Get unread count from all sources."""
        # Gmail unread
        gmail_result = self.gmail.execute('read_unread', {"max_results": 1})
        gmail_count = gmail_result.get('data', {}).get('count', 0)
        
        # WhatsApp unread
        whatsapp_result = self.whatsapp.execute('read_messages', {"limit": 100})
        whatsapp_count = whatsapp_result.get('data', {}).get('count', 0)
        
        return AgentSkillResponse.success({
            "gmail_unread": gmail_count,
            "whatsapp_unread": whatsapp_count,
            "total_unread": gmail_count + whatsapp_count
        }, self.skill_name)
    
    def _send_response(self, context: Dict) -> Dict:
        """Send a response message."""
        channel = context.get('channel')
        recipient = context.get('recipient')
        message = context.get('message')
        template = context.get('template')
        
        # Get message from template if specified
        if template and template in self.auto_responses:
            message = self.auto_responses[template]
        
        if not message:
            return AgentSkillResponse.error(
                "Missing required field: 'message' or valid 'template'",
                self.skill_name
            )
        
        if not recipient:
            return AgentSkillResponse.error(
                "Missing required field: 'recipient'",
                self.skill_name
            )
        
        result = None
        
        if channel == 'email':
            result = self.gmail.execute('send_email', {
                "to": recipient,
                "subject": "Re: Your inquiry",
                "body": message
            })
        elif channel == 'whatsapp':
            result = self.whatsapp.execute('send_message', {
                "to": recipient,
                "message": message
            })
        else:
            return AgentSkillResponse.error(
                f"Unknown channel: {channel}",
                self.skill_name,
                {"valid_channels": ["email", "whatsapp"]}
            )
        
        return AgentSkillResponse.success({
            "channel": channel,
            "recipient": recipient,
            "result": result
        }, self.skill_name)
    
    def _categorize(self, context: Dict) -> Dict:
        """Categorize content."""
        content = context.get('content', '')
        source = context.get('source', 'unknown')
        
        category = self._categorize_content(content)
        
        return AgentSkillResponse.success({
            "content": content[:100],
            "category": category,
            "source": source
        }, self.skill_name)
    
    def _prioritize(self, context: Dict) -> Dict:
        """Determine priority of content."""
        content = context.get('content', '')
        
        priority = self._determine_priority(content)
        
        return AgentSkillResponse.success({
            "content": content[:100],
            "priority": priority
        }, self.skill_name)
    
    def _categorize_content(self, content: str) -> str:
        """Categorize content based on keywords."""
        content_lower = content.lower()
        
        # Category keywords
        categories = {
            'inquiry': ['question', 'ask', 'wondering', 'info', 'information'],
            'complaint': ['complaint', 'issue', 'problem', 'wrong', 'broken'],
            'praise': ['great', 'excellent', 'amazing', 'love', 'thank'],
            'request': ['request', 'need', 'want', 'please', 'could you'],
            'meeting': ['meeting', 'schedule', 'calendar', 'appointment'],
            'sales': ['buy', 'purchase', 'price', 'cost', 'quote'],
            'support': ['help', 'support', 'technical', 'error', 'bug']
        }
        
        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _determine_priority(self, content: str) -> str:
        """Determine priority based on keywords."""
        content_lower = content.lower()
        
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return priority
        
        return 'normal'
    
    def _send_auto_response(self, to: str, subject: str, template_name: str) -> Dict:
        """Send an auto-response email."""
        template = self.auto_responses.get(template_name, '')
        
        result = self.gmail.execute('send_email', {
            "to": to,
            "subject": f"Re: {subject}",
            "body": template
        })
        
        return result.get('data', {})
    
    def _log_inbound_request(self, source: str, data: Dict):
        """Log inbound request to file."""
        try:
            # Load existing logs
            logs = []
            if os.path.exists(INBOUND_LOG):
                with open(INBOUND_LOG, 'r', encoding='utf-8') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            
            # Add new entry
            entry = {
                'timestamp': datetime.now().isoformat(),
                'source': source,
                'data': data
            }
            logs.append(entry)
            
            # Keep only last 1000 entries
            logs = logs[-1000:]
            
            # Save logs
            with open(INBOUND_LOG, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
            
            logger.debug(f"Logged inbound request from {source}")
            
        except Exception as e:
            logger.error(f"Failed to log inbound request: {e}")


# Convenience function
def execute(action: str, **kwargs) -> Dict:
    """Execute operations skill."""
    skill = OperationsSkill()
    return skill._execute_with_logging({"action": action, **kwargs})


if __name__ == '__main__':
    print("Operations Skill - Gold Tier")
    print("=" * 40)
    
    skill = OperationsSkill()
    
    print("\n1. Testing get_unread:")
    result = skill._execute_with_logging({
        "action": "get_unread"
    })
    print(json.dumps(result, indent=2))
    
    print("\n2. Testing categorize:")
    result = skill._execute_with_logging({
        "action": "categorize",
        "content": "I have a question about your pricing"
    })
    print(json.dumps(result, indent=2))
    
    print("\n3. Testing prioritize:")
    result = skill._execute_with_logging({
        "action": "prioritize",
        "content": "URGENT: Need immediate help with critical issue!"
    })
    print(json.dumps(result, indent=2))
    
    print("\n4. Testing process_whatsapp:")
    result = skill._execute_with_logging({
        "action": "process_whatsapp",
        "limit": 5
    })
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 40)
