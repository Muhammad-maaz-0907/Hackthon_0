# WhatsApp Auto-Reply Agent - 24/7 Automated Responses

import os
import time
import logging
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/whatsapp_auto_reply.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'whatsapp_session')
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'auto_reply_config.json')

# Polling interval in seconds
POLL_INTERVAL = 5  # Check every 5 seconds for faster response

# Ensure directories exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Track replied messages (to avoid duplicate replies)
replied_messages = set()


class AutoReplyConfig:
    """Manage auto-reply configuration."""
    
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        default_config = {
            "enabled": True,
            "business_hours_only": False,
            "business_hours": {"start": 9, "end": 17},  # 9 AM - 5 PM
            "delay_seconds": 3,  # Delay before replying (looks more natural)
            "max_replies_per_chat_per_hour": 5,
            "exclude_groups": True,
            "keywords": {
                "hello": "Hello! 👋 Thanks for reaching out. This is an automated response. I'll get back to you soon!",
                "hi": "Hi there! 👋 Thanks for your message. I'll respond as soon as possible!",
                "hey": "Hey! 👋 Got your message. I'll reply shortly!",
                "urgent": "⚡ I see this is urgent. I'll prioritize your message and respond ASAP!",
                "help": "🆘 I received your help request. Someone will assist you shortly!",
                "pricing": "💰 Thanks for your interest in pricing. I'll send you detailed information soon!",
                "invoice": "📄 Invoice request received. I'll process this and get back to you!",
                "payment": "💳 Payment inquiry noted. I'll respond with details shortly!",
                "default": "Thanks for your message! 🙏 This is an automated reply. I'll respond properly soon!"
            },
            "custom_responses": {
                "hours": "🕐 Our business hours are 9 AM - 5 PM. I'll respond during business hours!",
                "out_of_office": "📴 I'm currently away. I'll respond when I'm back online!",
                "busy": "⏳ I'm currently busy but will respond as soon as possible!"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **config}
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config=None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Config saved to: {self.config_file}")
    
    def is_business_hours(self):
        """Check if current time is within business hours."""
        if not self.config["business_hours_only"]:
            return True
        
        current_hour = datetime.now().hour
        start = self.config["business_hours"]["start"]
        end = self.config["business_hours"]["end"]
        
        return start <= current_hour < end


class WhatsAppAutoReplier:
    """WhatsApp Auto-Reply Agent."""
    
    def __init__(self):
        self.config = AutoReplyConfig(CONFIG_FILE)
        self.reply_counts = {}  # Track replies per chat per hour
        self.last_reset = datetime.now()
    
    def reset_reply_counts(self):
        """Reset reply counts every hour."""
        now = datetime.now()
        if (now - self.last_reset).total_seconds() > 3600:
            self.reply_counts = {}
            self.last_reset = now
            logger.info("Reset hourly reply counts")
    
    def can_reply(self, chat_name):
        """Check if we can reply to this chat (rate limiting)."""
        if chat_name not in self.reply_counts:
            self.reply_counts[chat_name] = 0
        
        max_replies = self.config.config["max_replies_per_chat_per_hour"]
        return self.reply_counts[chat_name] < max_replies
    
    def increment_reply_count(self, chat_name):
        """Increment reply count for a chat."""
        if chat_name not in self.reply_counts:
            self.reply_counts[chat_name] = 0
        self.reply_counts[chat_name] += 1
    
    def get_response(self, message_text):
        """Get appropriate auto-reply based on message content."""
        message_lower = message_text.lower()
        
        # Check for keyword matches
        keywords = self.config.config["keywords"]
        for keyword, response in keywords.items():
            if keyword in message_lower and keyword != "default":
                logger.info(f"Matched keyword: {keyword}")
                return response
        
        # Return default response
        return keywords.get("default", "Thanks for your message!")
    
    def is_group_chat(self, chat_name):
        """Check if chat is a group."""
        # WhatsApp group chats often have special characters or multiple names
        return self.config.config["exclude_groups"] and (
            ',' in chat_name or 
            'group' in chat_name.lower() or
            chat_name.count(' ') > 3
        )
    
    def send_reply(self, page, chat_name, message_text):
        """Send auto-reply to a chat."""
        try:
            # Check if we should reply
            if not self.config.config["enabled"]:
                logger.info("Auto-reply disabled in config")
                return False
            
            # Check business hours
            if not self.config.is_business_hours():
                logger.info("Outside business hours - skipping reply")
                return False
            
            # Check if group chat
            if self.is_group_chat(chat_name):
                logger.info(f"Skipping group chat: {chat_name}")
                return False
            
            # Check rate limit
            if not self.can_reply(chat_name):
                logger.warning(f"Rate limit reached for: {chat_name}")
                return False
            
            # Get response
            response = self.get_response(message_text)
            
            # Delay before replying (looks more natural)
            delay = self.config.config["delay_seconds"]
            logger.info(f"Waiting {delay} seconds before reply...")
            time.sleep(delay)
            
            # Click on the chat to open it
            logger.info(f"Opening chat: {chat_name}")
            
            # Find and click the chat
            chat_selector = f'span[title="{chat_name}"]'
            chat_elem = page.query_selector(chat_selector)
            
            if not chat_elem:
                # Try alternative selector
                chat_elem = page.query_selector(f'div[aria-label*="{chat_name}"]')
            
            if chat_elem:
                chat_elem.click()
                page.wait_for_timeout(1000)
                
                # Find message input box
                input_box = page.query_selector('div[contenteditable="true"][data-tab="10"]')
                
                if input_box:
                    # Clear input box
                    input_box.click()
                    page.wait_for_timeout(500)
                    
                    # Type the response
                    input_box.type(response)
                    page.wait_for_timeout(500)
                    
                    # Press Enter to send
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(1000)
                    
                    # Update reply count
                    self.increment_reply_count(chat_name)
                    
                    # Log the reply
                    self.log_reply(chat_name, message_text, response)
                    
                    logger.info(f"✅ Replied to {chat_name}: {response[:50]}...")
                    print(f"\n[Auto-Reply] To: @{chat_name} | Message: {response[:60]}...")
                    
                    return True
                else:
                    logger.warning("Could not find message input box")
            else:
                logger.warning(f"Could not find chat: {chat_name}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending reply: {e}")
            return False
    
    def log_reply(self, chat_name, original_message, reply):
        """Log auto-reply to JSON file."""
        log_file = os.path.join(LOGS_DIR, 'whatsapp_replies.json')
        
        # Load existing logs
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        
        # Add new entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'chat_name': chat_name,
            'original_message': original_message[:200],
            'reply': reply[:200],
            'status': 'sent'
        }
        logs.append(entry)
        
        # Keep only last 500 entries
        logs = logs[-500:]
        
        # Save logs
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
    
    def check_and_reply(self, page):
        """Check for new messages and auto-reply."""
        try:
            # Wait for chat list to load
            page.wait_for_selector('div[role="row"]', timeout=10000)
            page.wait_for_timeout(2000)
            
            # Find all chat rows
            chat_rows = page.query_selector_all('div[role="row"]')
            
            logger.info(f"Found {len(chat_rows)} chats")
            
            for row in chat_rows[:15]:  # Check top 15 chats
                try:
                    # Get chat name
                    chat_name_elem = row.query_selector('span[title]')
                    if not chat_name_elem:
                        continue
                    chat_name = chat_name_elem.get_attribute('title')
                    
                    if not chat_name or chat_name.strip() == '':
                        continue
                    
                    # Get message preview
                    message_text = None
                    all_spans = row.query_selector_all('span')
                    if all_spans and len(all_spans) > 0:
                        for span in reversed(all_spans):
                            text = span.inner_text()
                            if text and len(text.strip()) > 0 and len(text.strip()) < 200:
                                message_text = text.strip()
                                break
                    
                    if not message_text or message_text.strip() == '':
                        aria_elem = row.query_selector('span[aria-label]')
                        if aria_elem:
                            message_text = aria_elem.get_attribute('aria-label')
                    
                    if not message_text or message_text.strip() == '':
                        continue
                    
                    # Check if already replied
                    msg_key = f"{chat_name}:{message_text[:50]}"
                    if msg_key in replied_messages:
                        continue
                    
                    # Check if message is recent (unread indicator would be better but this works)
                    # For now, reply to all new messages
                    
                    logger.info(f"Chat: {chat_name[:30]} | Message: {message_text[:60]}...")
                    
                    # Send auto-reply
                    if self.send_reply(page, chat_name, message_text):
                        replied_messages.add(msg_key)
                        logger.info(f"[AUTO-REPLY] Sent to: {chat_name}")
                    
                except Exception as e:
                    logger.debug(f"Error processing chat row: {e}")
                    continue
            
            # Reset hourly counts
            self.reset_reply_counts()
            
        except Exception as e:
            logger.error(f"Error checking WhatsApp: {e}")
    
    def run(self):
        """Main auto-reply loop."""
        logger.info("WhatsApp Auto-Reply Agent starting...")
        print("=" * 60)
        print("WhatsApp Auto-Reply Agent - 24/7")
        print("=" * 60)
        print(f"Status: {'Enabled' if self.config.config['enabled'] else 'Disabled'}")
        print(f"Business Hours Only: {self.config.config['business_hours_only']}")
        print(f"Delay: {self.config.config['delay_seconds']} seconds")
        print(f"Max Replies/Hour/Chat: {self.config.config['max_replies_per_chat_per_hour']}")
        print(f"Exclude Groups: {self.config.config['exclude_groups']}")
        print("=" * 60)
        print("\nStarting browser... Please log in to WhatsApp Web.\n")
        
        with sync_playwright() as p:
            # Launch browser
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                viewport={'width': 1280, 'height': 720}
            )
            page = context.pages[0]
            
            # Navigate to WhatsApp Web
            logger.info("Navigating to WhatsApp Web...")
            page.goto('https://web.whatsapp.com')
            
            print("WhatsApp Auto-Reply Agent running...")
            print("Press Ctrl+C to stop.\n")
            
            # Wait for login
            page.wait_for_timeout(10000)
            
            while True:
                try:
                    self.check_and_reply(page)
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                
                time.sleep(POLL_INTERVAL)


def main():
    """Main entry point."""
    replier = WhatsAppAutoReplier()
    replier.run()


if __name__ == '__main__':
    main()
