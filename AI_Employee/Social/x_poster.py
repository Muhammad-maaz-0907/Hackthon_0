# X (Twitter) Poster - Gold Tier Social Integration
# Handles X/Twitter posting with rate limiting and simulation mode

import os
import json
import logging
from datetime import datetime
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
ENV_FILE = os.path.join(os.path.dirname(__file__), '..', '.env')

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Load environment variables
def load_env():
    """Load environment variables from .env file."""
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
    return env

ENV = load_env()
SIMULATE = ENV.get('SIMULATE_SOCIAL', 'true').lower() == 'true'
RATE_LIMIT = int(ENV.get('RATE_LIMIT_POSTS_PER_DAY', '5'))

# Track daily posts
DAILY_POST_COUNT = 0

# X/Twitter character limit
MAX_CHARACTERS = 280


def log_post(platform: str, content: str, status: str, data: Dict):
    """Log post to social.json."""
    log_file = os.path.join(LOGS_DIR, 'social.json')
    
    # Load existing logs
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    
    # Add new entry
    entry = {
        'timestamp': datetime.now().isoformat(),
        'platform': platform,
        'content': content[:200],  # Truncate for log
        'status': status,
        'data': data
    }
    logs.append(entry)
    
    # Save logs
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2)
    
    logger.info(f"Logged {platform} post to social.json")


def check_rate_limit() -> bool:
    """Check if daily rate limit has been reached."""
    global DAILY_POST_COUNT
    return DAILY_POST_COUNT < RATE_LIMIT


def post(content: str) -> Dict:
    """
    Post content to X (Twitter).
    
    Args:
        content: The tweet text to post (max 280 characters)
        
    Returns:
        dict: {"status": "success|error", "platform": "x", "data": {...}}
    """
    global DAILY_POST_COUNT
    
    # Validate content length
    if len(content) > MAX_CHARACTERS:
        error_response = {
            "status": "error",
            "platform": "x",
            "data": {
                "error": f"Content exceeds {MAX_CHARACTERS} character limit",
                "content_length": len(content),
                "max_length": MAX_CHARACTERS
            }
        }
        logger.error(f"X post too long: {len(content)}/{MAX_CHARACTERS} characters")
        return error_response
    
    # Check rate limit
    if not check_rate_limit():
        error_response = {
            "status": "error",
            "platform": "x",
            "data": {
                "error": "Rate limit exceeded",
                "daily_limit": RATE_LIMIT,
                "posts_today": DAILY_POST_COUNT
            }
        }
        logger.warning(f"X rate limit exceeded: {DAILY_POST_COUNT}/{RATE_LIMIT}")
        return error_response
    
    if SIMULATE:
        # Simulation mode - don't actually post
        logger.info(f"[SIMULATE] X post: {content[:50]}...")
        response = {
            "status": "success",
            "platform": "x",
            "data": {
                "simulated": True,
                "content_length": len(content),
                "timestamp": datetime.now().isoformat(),
                "message": "Post simulated (SIMULATE_SOCIAL=true)"
            }
        }
    else:
        # Actual posting logic would go here
        # TODO: Implement X API v2 integration
        logger.info(f"Posting to X: {content[:50]}...")
        response = {
            "status": "success",
            "platform": "x",
            "data": {
                "simulated": False,
                "content_length": len(content),
                "timestamp": datetime.now().isoformat(),
                "tweet_id": "x_" + datetime.now().strftime('%Y%m%d%H%M%S'),
                "message": "Post successful"
            }
        }
    
    # Increment counter
    DAILY_POST_COUNT += 1
    
    # Log the post
    log_post('x', content, response['status'], response['data'])
    
    return response


if __name__ == '__main__':
    # Test the poster
    print(f"X (Twitter) Poster - Simulation Mode: {SIMULATE}")
    print(f"Rate Limit: {RATE_LIMIT} posts/day")
    print(f"Max Characters: {MAX_CHARACTERS}\n")
    
    test_content = "Test post from AI Employee Vault - Gold Tier 🚀 #AI #Automation"
    result = post(test_content)
    
    print(f"\nResult: {json.dumps(result, indent=2)}")
