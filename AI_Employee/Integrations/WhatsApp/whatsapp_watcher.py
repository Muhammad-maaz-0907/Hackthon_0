# WhatsApp Watcher - Silver Tier Integration
# Continuous polling for NEW unread messages with keywords

import os
import time
import logging
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'whatsapp_session')
NEEDS_ACTION_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Needs_Action')
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')

# Polling interval in seconds
POLL_INTERVAL = 5  # Reduced for faster detection of new messages

# Keywords to watch for (add more as needed)
KEYWORDS = ['urgent', 'invoice', 'payment', 'pricing', 'help', 'hello', 'hi', 'test', 'hey']

# Track processed messages (persisted across sessions)
PROCESSED_FILE = os.path.join(LOGS_DIR, 'whatsapp_processed.json')
processed_messages = set()

# Store initial chat state to ignore old messages
initial_chat_state = {}


def load_processed_messages():
    """Load previously processed messages from file."""
    global processed_messages
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                processed_messages = set(data.get('messages', []))
                logger.info(f"Loaded {len(processed_messages)} processed messages from history")
        except Exception as e:
            logger.error(f"Error loading processed messages: {e}")
            processed_messages = set()
    else:
        processed_messages = set()
        logger.info("No previous processed messages found (first run)")


def save_processed_messages():
    """Save processed messages to file for persistence."""
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
            json.dump({'messages': list(processed_messages)}, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving processed messages: {e}")


def has_unread_indicator(row):
    """
    Check if a chat row has an unread message indicator.
    WhatsApp shows unread messages with:
    - Gray background circle with number
    - Green circle (unread single message)
    """
    try:
        # Look for unread message indicators (circles with numbers or dots)
        unread_indicators = [
            'span._ak4q',  # Unread message circle
            'span._ak4r',  # Alternative unread indicator
            'div._ak4q',   # Unread div
        ]
        
        for selector in unread_indicators:
            if row.query_selector(selector):
                return True
        
        # Check for green dot (unread single message)
        green_dot = row.query_selector('span[style*="background-color: rgb(0, 168, 128)"]')
        if green_dot:
            return True
        
        # Check if the message preview is in bold (unread messages are bold)
        message_elem = row.query_selector('span[title] + span span, span[aria-label]')
        if message_elem:
            # Unread messages often have bold styling
            style = message_elem.get_attribute('style') or ''
            if 'bold' in style.lower() or 'font-weight: 600' in style:
                return True
        
        return False
    except Exception:
        return False


def capture_initial_state(page):
    """Capture the initial state of all chats to ignore old messages."""
    global initial_chat_state
    logger.info("Capturing initial chat state (ignoring old messages)...")
    
    try:
        page.wait_for_selector('div[role="row"]', timeout=10000)
        page.wait_for_timeout(3000)  # Wait for content to fully load
        
        chat_rows = page.query_selector_all('div[role="row"]')
        
        for row in chat_rows:
            try:
                chat_name_elem = row.query_selector('span[title]')
                if not chat_name_elem:
                    continue
                
                chat_name = chat_name_elem.get_attribute('title')
                if not chat_name:
                    continue
                
                # Get current message preview
                message_text = None
                all_spans = row.query_selector_all('span')
                if all_spans:
                    for span in reversed(all_spans):
                        text = span.inner_text()
                        if text and 0 < len(text.strip()) < 200:
                            message_text = text.strip()
                            break
                
                if message_text:
                    # Store this as "old" - we'll ignore it
                    key = f"{chat_name}:{message_text[:50]}"
                    initial_chat_state[chat_name] = message_text
                    processed_messages.add(key)
                    logger.debug(f"Ignoring old message from {chat_name}: {message_text[:30]}...")
                    
            except Exception:
                continue
        
        logger.info(f"Captured initial state for {len(initial_chat_state)} chats")
        logger.info("✅ Will only detect NEW messages received after startup!\n")
        
    except Exception as e:
        logger.error(f"Error capturing initial state: {e}")


def create_whatsapp_md(chat_name, message_text):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"whatsapp_{timestamp}.md"
    filepath = os.path.join(NEEDS_ACTION_DIR, filename)
    
    content = f"""---
type: whatsapp
from: {chat_name}
time: {datetime.now().isoformat()}
---
Message: {message_text}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Created WhatsApp file: {filename}")


def check_whatsapp(page):
    """Check for NEW unread messages with keywords."""
    try:
        # Wait for chat list to load
        page.wait_for_selector('div[role="row"]', timeout=10000)
        page.wait_for_timeout(2000)

        # Find all chat rows
        chat_rows = page.query_selector_all('div[role="row"]')

        logger.info(f"Found {len(chat_rows)} chats")

        for row in chat_rows:
            try:
                # Get chat name - look for title attribute
                chat_name_elem = row.query_selector('span[title]')
                if not chat_name_elem:
                    continue
                chat_name = chat_name_elem.get_attribute('title')

                if not chat_name or chat_name.strip() == '':
                    continue

                # Get message text - look for the last span in the row (message preview)
                message_text = None

                # Try to get the message preview span
                all_spans = row.query_selector_all('span')
                if all_spans and len(all_spans) > 0:
                    # Get the last span that has meaningful content
                    for span in reversed(all_spans):
                        text = span.inner_text()
                        if text and len(text.strip()) > 0 and len(text.strip()) < 200:
                            message_text = text.strip()
                            break

                if not message_text or message_text.strip() == '':
                    # Try aria-label as fallback
                    aria_elem = row.query_selector('span[aria-label]')
                    if aria_elem:
                        message_text = aria_elem.get_attribute('aria-label')

                if not message_text or message_text.strip() == '':
                    continue

                # Check if this message was already processed (from initial state or previous)
                msg_key = f"{chat_name}:{message_text[:50]}"
                if msg_key in processed_messages:
                    continue  # Skip old/processed messages

                # Check for unread indicator (green dot, bold text, etc.)
                is_unread = has_unread_indicator(row)
                
                # Only process if it's unread OR if it's a new message (not in initial state)
                chat_was_in_initial = chat_name in initial_chat_state
                initial_message = initial_chat_state.get(chat_name, '')
                
                # This is a NEW message if:
                # 1. It has unread indicator, OR
                # 2. The message text is different from initial state
                is_new_message = is_unread or (chat_was_in_initial and message_text != initial_message) or (not chat_was_in_initial)
                
                if not is_new_message:
                    logger.debug(f"Skipping old message from {chat_name}")
                    continue

                # Log what we found
                logger.info(f"Chat: {chat_name[:30]} | Message: {message_text[:60]}...")

                # Check for keywords (case insensitive)
                message_lower = message_text.lower()
                if any(keyword in message_lower for keyword in KEYWORDS):
                    create_whatsapp_md(chat_name, message_text)
                    processed_messages.add(msg_key)
                    save_processed_messages()  # Save to file for persistence
                    logger.info(f"[MATCH] Keyword found in chat: {chat_name}")
                    print(f"\n[NEW MESSAGE] From: {chat_name} | Text: {message_text[:50]}...")

            except Exception as e:
                logger.debug(f"Error processing chat row: {e}")
                continue

    except Exception as e:
        logger.error(f"Error checking WhatsApp messages: {e}")


def main():
    """Main polling loop."""
    logger.info("WhatsApp Watcher starting...")

    # Ensure directories exist
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
    
    # Load previously processed messages
    load_processed_messages()

    with sync_playwright() as p:
        # Launch with persistent context using launch_persistent_context
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )
        page = context.pages[0]

        # Navigate to WhatsApp Web
        logger.info("Navigating to WhatsApp Web...")
        page.goto('https://web.whatsapp.com')

        print("\n" + "=" * 60)
        print("WhatsApp Watcher - NEW Messages Only")
        print("=" * 60)
        print(f"Keywords: {', '.join(KEYWORDS)}")
        print(f"Poll interval: {POLL_INTERVAL} seconds")
        print("=" * 60)
        print("\nWaiting for WhatsApp Web to load... Please log in if needed.\n")
        
        # Wait for page to load and user to log in
        page.wait_for_timeout(15000)
        
        # Capture initial state (ignore old messages)
        capture_initial_state(page)
        
        print("Monitoring for NEW incoming messages...\n")
        print("Press Ctrl+C to stop.\n")

        while True:
            try:
                check_whatsapp(page)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")

            time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    import signal
    
    def signal_handler(sig, frame):
        """Save processed messages on exit."""
        print("\n\nSaving processed messages...")
        save_processed_messages()
        print("Goodbye! 👋")
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    main()
