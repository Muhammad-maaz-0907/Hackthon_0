# Approval Engine - LinkedIn Posts
# Monitors Approved/ folder and posts content to LinkedIn automatically

import os
import sys
import time
import shutil
import logging
from datetime import datetime

# Add Integrations/LinkedIn to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'Integrations', 'LinkedIn'))

from linkedin_executor import extract_post_content, post_to_linkedin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = SCRIPT_DIR  # approval_engine.py is already in AI_Employee root
APPROVED_DIR = os.path.join(BASE_DIR, 'Approved')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'Archive')

# Polling interval in seconds
POLL_INTERVAL = 5

# Track processed files to avoid duplicates
processed_files = set()


def ensure_directories():
    """Ensure required directories exist."""
    os.makedirs(APPROVED_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    logger.info(f"Monitoring folder: {APPROVED_DIR}")


def scan_approved_folder():
    """Scan Approved/ folder for new .md files."""
    try:
        if not os.path.exists(APPROVED_DIR):
            return []
        
        files = [f for f in os.listdir(APPROVED_DIR) 
                 if f.endswith('.md') and f not in processed_files]
        
        return files
    
    except Exception as e:
        logger.error(f"Error scanning Approved folder: {e}")
        return []


def process_file(filename):
    """
    Process a single approved file.
    Returns True if successful, False otherwise.
    """
    filepath = os.path.join(APPROVED_DIR, filename)
    
    logger.info(f"Processing: {filename}")
    print(f"\n{'='*50}")
    print(f"Processing: {filename}")
    print(f"{'='*50}")
    
    try:
        # Extract post content
        logger.info("Extracting post content...")
        print("  → Extracting post content...")
        content = extract_post_content(filepath)
        
        if not content:
            logger.error("Empty post content")
            print("  [ERROR] Empty post content")
            return False
        
        print(f"  Content preview: {content[:100]}...")
        
        # Post to LinkedIn
        success = post_to_linkedin(content)
        
        if success:
            # Move to Archive
            archive_path = os.path.join(ARCHIVE_DIR, filename)
            shutil.move(filepath, archive_path)
            
            # Also move any metadata file if exists
            metadata_file = filename.replace('.md', '_metadata.md')
            metadata_path = os.path.join(APPROVED_DIR, metadata_file)
            if os.path.exists(metadata_path):
                shutil.move(metadata_path, os.path.join(ARCHIVE_DIR, metadata_file))
            
            logger.info(f"Archived: {filename}")
            print(f"  [OK] File moved to Archive/")
            
            # Mark as processed
            processed_files.add(filename)
            
            return True
        else:
            logger.error("Posting failed - file remains in Approved/")
            print("  [WARN] Posting failed - file remains in Approved/ for retry")
            return False
            
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        print(f"  [ERROR] Error: {e}")
        return False


def main():
    """Main approval monitoring loop."""
    print("=" * 50)
    print("LinkedIn Approval Engine")
    print("=" * 50)
    print(f"Monitoring: {APPROVED_DIR}")
    print(f"Archive: {ARCHIVE_DIR}")
    print("\nWorkflow:")
    print("  1. Generate post -> Needs_Action/")
    print("  2. Review & move to -> Approved/")
    print("  3. Auto-post & archive -> Archive/")
    print("\nPress Ctrl+C to stop\n")
    
    ensure_directories()
    
    logger.info("Approval Engine started...")
    print("[OK] Approval Engine started...")
    
    try:
        while True:
            # Scan for new files
            new_files = scan_approved_folder()
            
            if new_files:
                # Process one file at a time
                filename = new_files[0]
                success = process_file(filename)
                
                if success:
                    logger.info(f"Successfully processed: {filename}")
                else:
                    logger.warning(f"Failed to process: {filename}")
            else:
                # No files - wait and check again
                time.sleep(POLL_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("Approval Engine stopped by user")
        print("\n[OK] Approval Engine stopped")


if __name__ == "__main__":
    main()
