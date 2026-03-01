# Instagram Watcher - Gold Tier Integration
# Continuous polling for NEW unread Instagram DMs only

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
USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'instagram_session')
NEEDS_ACTION_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Needs_Action')
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'Logs')

# Polling interval in seconds
POLL_INTERVAL = 15

# Keywords to watch for in DMs and comments
KEYWORDS = [
    'urgent', 'help', 'hello', 'hi', 'hey', 'test',
    'collab', 'collaboration', 'partnership', 'sponsor',
    'question', 'inquiry', 'business', 'pricing',
    'dm', 'message', 'contact', 'reach out'
]

# Track processed messages (persisted across sessions)
PROCESSED_FILE = os.path.join(LOGS_DIR, 'instagram_processed.json')
processed_messages = set()

# Store initial chat state to ignore old messages
initial_chat_state = {}

# Ensure directories exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


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
        with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
            json.dump({'messages': list(processed_messages)}, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving processed messages: {e}")


def capture_initial_state(page):
    """Capture the initial state of all DMs to ignore old messages."""
    global initial_chat_state
    logger.info("Capturing initial DM state (ignoring old messages)...")
    
    try:
        # Click DM button first to open inbox
        dm_button = page.query_selector('svg[aria-label="Messages"]')
        if dm_button:
            dm_button.click()
            logger.info("Clicked DM button to open inbox")
            page.wait_for_timeout(3000)
        
        # Wait for DM panel to load
        page.wait_for_selector('article, div[role="row"]', timeout=5000)
        page.wait_for_timeout(2000)
        
        # Find all DM conversations
        dm_rows = page.query_selector_all('article, div[role="row"]')
        
        for row in dm_rows[:20]:
            try:
                # Get username
                username_elem = row.query_selector('span, strong, a')
                if not username_elem:
                    continue
                
                username = username_elem.inner_text().strip()
                if not username or len(username) < 2:
                    continue
                
                # Get message preview
                message_elem = row.query_selector_all('span')[-1] if row.query_selector_all('span') else None
                if not message_elem:
                    continue
                
                message_text = message_elem.inner_text().strip()
                if not message_text or len(message_text) < 3:
                    continue
                
                # Store this as "old" - we'll ignore it
                key = f"dm:{username}:{message_text[:50]}"
                initial_chat_state[username] = message_text
                processed_messages.add(key)
                logger.debug(f"Ignoring old DM from {username}: {message_text[:30]}...")
                
            except Exception:
                continue
        
        logger.info(f"Captured initial state for {len(initial_chat_state)} DM conversations")
        logger.info("✅ Will only detect NEW messages received after startup!\n")
        
    except Exception as e:
        logger.warning(f"Could not capture initial state (this is OK): {e}")
        logger.info("Will detect all current messages as new on first run")
        initial_chat_state = {}  # Reset so we detect everything as new


def create_instagram_md(source_type, source_name, message_text, additional_data=None):
    """
    Create markdown file for Instagram message/notification in Needs_Action folder.
    
    Args:
        source_type: 'dm' or 'comment' or 'mention'
        source_name: Username or post identifier
        message_text: The message/comment text
        additional_data: Optional dict with extra metadata
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"instagram_{source_type}_{timestamp}.md"
    filepath = os.path.join(NEEDS_ACTION_DIR, filename)

    additional_md = ""
    if additional_data:
        for key, value in additional_data.items():
            additional_md += f"{key}: {value}\n"

    content = f"""---
type: instagram
source_type: {source_type}
from: {source_name}
time: {datetime.now().isoformat()}
{additional_md}---
Message: {message_text}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"Created Instagram file: {filename}")


def log_activity(activity_type, data):
    """Log Instagram activity to logs/instagram.json."""
    log_file = os.path.join(LOGS_DIR, 'instagram.json')
    
    # Load existing logs
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, Exception):
            logs = []
    
    # Add new entry
    entry = {
        'timestamp': datetime.now().isoformat(),
        'activity_type': activity_type,
        'data': data
    }
    logs.append(entry)
    
    # Keep only last 500 entries
    logs = logs[-500:]
    
    # Save logs
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write log: {e}")


def check_instagram_dms(page):
    """
    Check for NEW Instagram Direct Messages only.
    Ignores all messages that existed at startup.
    """
    try:
        # Wait for DM panel to load
        page.wait_for_timeout(3000)
        
        # Click DM button to open inbox
        dm_selectors = [
            'svg[aria-label="Messages"]',
            'svg[aria-label*="message" i]',
            'a[href*="/direct/inbox/"]',
        ]
        
        dm_button = None
        for selector in dm_selectors:
            try:
                dm_button = page.query_selector(selector)
                if dm_button:
                    logger.info(f"Found DM button with selector: {selector}")
                    dm_button.click()
                    page.wait_for_timeout(2000)
                    break
            except Exception:
                continue
        
        if not dm_button:
            logger.debug("No DM button found")
            return
        
        # Find all DM conversations
        dm_rows = page.query_selector_all('article, div[role="row"]')
        logger.debug(f"Found {len(dm_rows)} potential DM conversations")
        
        for row in dm_rows[:20]:
            try:
                # Get username
                username_elem = row.query_selector('span, strong, a')
                if not username_elem:
                    continue
                
                username = username_elem.inner_text().strip()
                if not username or len(username) < 2:
                    continue
                
                # Get message preview
                message_elem = row.query_selector_all('span')[-1] if row.query_selector_all('span') else None
                if not message_elem:
                    continue
                
                message_text = message_elem.inner_text().strip()
                if not message_text or len(message_text) < 3:
                    continue
                
                # Check if this is a NEW message (not in initial state)
                msg_key = f"dm:{username}:{message_text[:50]}"
                
                # Skip if already processed
                if msg_key in processed_messages:
                    logger.debug(f"Skipping known message from {username}")
                    continue
                
                # Check if message existed in initial state
                if username in initial_chat_state:
                    if message_text == initial_chat_state[username]:
                        logger.debug(f"Skipping initial state message from {username}")
                        continue
                
                logger.info(f"NEW DM from: {username[:30]} | Message: {message_text[:60]}...")
                
                # Check for keywords
                message_lower = message_text.lower()
                if any(keyword in message_lower for keyword in KEYWORDS):
                    create_instagram_md('dm', username, message_text, {
                        'preview': message_text[:100]
                    })
                    processed_messages.add(msg_key)
                    save_processed_messages()
                    
                    log_activity('dm_detected', {
                        'username': username,
                        'message_preview': message_text[:100],
                        'keywords_matched': [k for k in KEYWORDS if k in message_lower]
                    })
                    
                    logger.info(f"[MATCH] Keyword found in NEW DM from: {username}")
                    print(f"\n[NEW Instagram DM] From: @{username} | Text: {message_text[:60]}...")
                
            except Exception as e:
                logger.debug(f"Error processing DM row: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error checking Instagram DMs: {e}")
        
        if dm_button:
            try:
                dm_button.click()
                logger.info("Clicked DM button to open inbox")
                page.wait_for_timeout(2000)
            except Exception as e:
                logger.debug(f"Could not click DM button: {e}")
        
        # Wait for DM list to load
        page.wait_for_timeout(2000)
        
        # Look for DM conversation rows
        # Instagram DM conversations are typically in article or div elements
        dm_rows = page.query_selector_all('article, div[role="button"], div._aa_c')
        
        logger.info(f"Found {len(dm_rows)} potential DM conversations")
        
        for row in dm_rows[:10]:  # Limit to first 10 conversations
            try:
                # Get username/sender name
                username_elem = row.query_selector('span, strong, a')
                if not username_elem:
                    continue
                username = username_elem.inner_text().strip()
                
                if not username or len(username) < 2:
                    continue
                
                # Get message preview text
                message_elem = row.query_selector_all('span')[-1] if row.query_selector_all('span') else None
                if not message_elem:
                    continue
                message_text = message_elem.inner_text().strip()
                
                if not message_text or len(message_text) < 3:
                    continue
                
                # Check for unread indicator (optional)
                # Instagram shows a blue dot or bold text for unread
                
                logger.info(f"DM from: {username[:30]} | Message: {message_text[:60]}...")
                
                # Check for keywords (case insensitive)
                message_lower = message_text.lower()
                if any(keyword in message_lower for keyword in KEYWORDS):
                    # Create unique key to avoid duplicates
                    msg_key = f"dm:{username}:{message_text[:50]}"
                    
                    if msg_key in processed_messages:
                        logger.debug(f"Already processed DM: {msg_key}")
                        continue
                    
                    create_instagram_md('dm', username, message_text, {
                        'preview': message_text[:100]
                    })
                    processed_messages.add(msg_key)
                    
                    log_activity('dm_detected', {
                        'username': username,
                        'message_preview': message_text[:100],
                        'keywords_matched': [k for k in KEYWORDS if k in message_lower]
                    })
                    
                    logger.info(f"[MATCH] Keyword found in DM from: {username}")
                    print(f"\n[NEW Instagram DM] From: @{username} | Text: {message_text[:60]}...")
                
            except Exception as e:
                logger.debug(f"Error processing DM row: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error checking Instagram DMs: {e}")


def check_instagram_notifications(page):
    """
    Check for new Instagram notifications (comments, mentions, likes).
    
    Note: Instagram requires login for notifications page.
    This function now skips navigation to avoid errors.
    """
    try:
        # Skip notifications page navigation to avoid "page not available" error
        # Instagram blocks automated access to activity feed
        logger.debug("Skipping notifications check (requires manual login)")
        return
        
        # Original code disabled to prevent errors
        # To re-enable, remove the 'return' statement above
        page.wait_for_timeout(2000)
        
        # Look for notification items
        # Instagram notifications are typically in article or li elements
        notification_items = page.query_selector_all('article, li._a90z, div._aa_c')
        
        logger.info(f"Found {len(notification_items)} notification items")
        
        for item in notification_items[:15]:  # Limit to first 15 notifications
            try:
                # Get notification text
                text_elem = item.query_selector('span, div')
                if not text_elem:
                    continue
                
                notification_text = text_elem.inner_text().strip()
                
                if not notification_text or len(notification_text) < 5:
                    continue
                
                # Determine notification type
                notif_type = 'unknown'
                if 'comment' in notification_text.lower():
                    notif_type = 'comment'
                elif 'mentioned' in notification_text.lower() or 'mention' in notification_text.lower():
                    notif_type = 'mention'
                elif 'liked' in notification_text.lower():
                    notif_type = 'like'
                elif 'follow' in notification_text.lower():
                    notif_type = 'follow'
                elif 'message' in notification_text.lower() or 'dm' in notification_text.lower():
                    notif_type = 'dm'
                
                # Only process comments and mentions (most actionable)
                if notif_type not in ['comment', 'mention']:
                    continue
                
                # Extract username if possible (usually before the action)
                username = "unknown_user"
                username_match = notification_text.split()[0] if notification_text.split() else "unknown_user"
                
                # Create unique key
                notif_key = f"notif:{notif_type}:{username}:{notification_text[:50]}"
                
                if notif_key in processed_messages:
                    continue
                
                create_instagram_md(notif_type, username, notification_text, {
                    'notification_type': notif_type
                })
                processed_messages.add(notif_key)
                
                log_activity('notification_detected', {
                    'type': notif_type,
                    'username': username,
                    'text': notification_text[:200]
                })
                
                logger.info(f"[MATCH] New {notif_type} from: {username}")
                print(f"\n[New Instagram {notif_type.title()}] From: @{username} | {notification_text[:60]}...")
                
            except Exception as e:
                logger.debug(f"Error processing notification: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error checking Instagram notifications: {e}")


def main():
    """Main polling loop."""
    logger.info("Instagram Watcher starting...")
    print("Instagram Watcher - Gold Tier")
    print("=" * 40)
    print(f"Monitoring: Instagram DMs (Direct Messages)")
    print(f"Keywords: {', '.join(KEYWORDS[:5])}... ({len(KEYWORDS)} total)")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print("=" * 40)
    print("\nStarting browser... Please log in to Instagram manually if prompted.\n")

    with sync_playwright() as p:
        # Launch with persistent context using launch_persistent_context
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )
        page = context.pages[0]

        # Navigate to Instagram
        logger.info("Navigating to Instagram...")
        page.goto('https://www.instagram.com/')
        
        print("Instagram Watcher running - Waiting for login if needed...")
        
        # Wait for initial page load and potential login
        page.wait_for_timeout(15000)
        
        # Load previously processed messages
        load_processed_messages()
        
        # Capture initial state (ignore old messages)
        capture_initial_state(page)
        
        print("Monitoring for NEW incoming messages...\n")
        print("Press Ctrl+C to stop.\n")

        while True:
            try:
                # Check DMs
                check_instagram_dms(page)

                # Check notifications (disabled)
                # check_instagram_notifications(page)

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
