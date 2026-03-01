# LinkedIn Executor - Playwright Automation
# Posts content to LinkedIn using browser automation

import os
import re
import time
import logging
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Go up to AI_Employee (2 levels)
SESSION_DIR = os.path.join(SCRIPT_DIR, 'linkedin_session')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'Archive')


def extract_post_content(filepath):
    """Extract post content from markdown file (ignore frontmatter)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove frontmatter (everything between --- markers)
    match = re.match(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()


def post_to_linkedin(content):
    """
    Post content to LinkedIn using Playwright.
    Returns True if successful, False otherwise.
    """
    logger.info("Launching browser...")
    print("  → Launching browser...")
    
    try:
        with sync_playwright() as p:
            # Launch browser with persistent context (saves session)
            context = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=False,  # Visible for demo
                slow_mo=300,     # Human-like speed for demo
                viewport={'width': 1280, 'height': 720}
            )
            
            page = context.pages[0] if context.pages else context.new_page()
            
            logger.info("Opening LinkedIn...")
            print("  → Opening LinkedIn...")
            
            # Navigate to LinkedIn
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            
            # Wait for page to load (check for feed or login)
            time.sleep(3)
            
            # Check if logged in (look for share box)
            share_box = page.locator('div[role="textbox"][aria-label*="post" i], div[contenteditable="true"][aria-label*="post" i]').first
            
            if not share_box.is_visible(timeout=5000):
                logger.warning("Not logged in. Please log in manually.")
                print("  [WARN] Not logged in. Please log in to LinkedIn manually...")
                print("  (Session will be saved for next time)")
                
                # Wait for user to log in (max 2 minutes)
                for i in range(24):
                    time.sleep(5)
                    if share_box.is_visible(timeout=1000):
                        logger.info("User logged in successfully")
                        print("  [OK] Logged in successfully!")
                        break
                else:
                    logger.error("Login timeout")
                    print("  [ERROR] Login timeout. Please try again.")
                    context.close()
                    return False
            
            logger.info("Creating post...")
            print("  -> Creating post...")
            
            # Click on share box to open post editor
            share_box.click()
            time.sleep(2)
            
            # Find the post editor textarea
            editor = page.locator('div[contenteditable="true"][aria-label*="post" i], div[role="textbox"][aria-label*="post" i]').first
            
            # Wait for editor to be ready
            editor.wait_for(state='visible', timeout=10000)
            time.sleep(1)
            
            # Clear any existing content and type new content
            editor.click()
            time.sleep(1)
            
            # Use keyboard to select all and delete (more reliable)
            page.keyboard.press('Control+A')
            time.sleep(0.5)
            page.keyboard.press('Delete')
            time.sleep(0.5)
            
            # Type the post content
            editor.type(content, delay=50)
            time.sleep(2)
            
            # Find and click the post button
            # LinkedIn's post button has various selectors, try multiple
            post_button = None
            
            selectors = [
                'button:has-text("Post")',
                'button:has-text("post")',
                '[aria-label*="post" i]',
                'button[data-control-name*="post"]'
            ]
            
            for selector in selectors:
                try:
                    post_button = page.locator(selector).first
                    if post_button.is_visible(timeout=3000):
                        break
                except:
                    continue
            
            if post_button and post_button.is_visible():
                logger.info("Posting...")
                print("  -> Posting...")
                
                post_button.click()
                time.sleep(3)
                
                # Wait for post to complete (look for success indicator)
                time.sleep(5)
                
                logger.info("Post successful!")
                print("  [OK] Post successful!")
                
                context.close()
                return True
            else:
                logger.error("Post button not found")
                print("  [ERROR] Post button not found. Manual intervention may be needed.")
                context.close()
                return False
                
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {e}")
        print(f"  [ERROR] Error: {e}")
        return False


def main():
    """Test the LinkedIn poster with sample content."""
    print("=" * 50)
    print("LinkedIn Executor - Test Mode")
    print("=" * 50)
    
    test_content = "Testing LinkedIn automation! #Test #Automation"
    
    success = post_to_linkedin(test_content)
    
    if success:
        print("\n[OK] Test post successful!")
    else:
        print("\n[ERROR] Test post failed. Check logs for details.")


if __name__ == "__main__":
    main()
