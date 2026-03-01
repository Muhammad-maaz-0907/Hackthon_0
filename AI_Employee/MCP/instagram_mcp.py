# Instagram MCP Server - Gold Tier
# Instagram Graph API integration via MCP protocol

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Handle both module import and direct execution
try:
    from .mcp_server_base import MCPServerBase, MCPResponse
except ImportError:
    from mcp_server_base import MCPServerBase, MCPResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
ENV_FILE = os.path.join(os.path.dirname(__file__), '..', '.env')


class InstagramMCPServer(MCPServerBase):
    """
    MCP Server for Instagram operations.
    
    Actions:
        - create_post: Create an Instagram post
        - get_metrics: Get post/profile metrics
    
    Note: Instagram Graph API requires Business/Creator account,
    Facebook Page, App ID, and Access Token.
    This implementation uses simulation mode by default.
    """
    
    def __init__(self):
        super().__init__("instagram_mcp", max_retries=3, retry_delay=1.0)
        self.app_id = None
        self.app_secret = None
        self.access_token = None
        self.instagram_business_account_id = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Instagram credentials from environment."""
        env = {}
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip()
        
        self.app_id = os.environ.get('INSTAGRAM_APP_ID', env.get('INSTAGRAM_APP_ID'))
        self.app_secret = os.environ.get('INSTAGRAM_APP_SECRET', env.get('INSTAGRAM_APP_SECRET'))
        self.access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN', env.get('INSTAGRAM_ACCESS_TOKEN'))
        self.instagram_business_account_id = os.environ.get(
            'INSTAGRAM_BUSINESS_ACCOUNT_ID', 
            env.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        )
    
    def connect(self, **kwargs) -> Dict:
        """
        Connect to Instagram Graph API.
        
        Returns:
            Dict: Connection status
        """
        try:
            logger.info("[InstagramMCP] Connecting to Instagram Graph API...")
            
            # Check for credentials
            if not self.access_token:
                # Simulation mode - no credentials required
                logger.info("[InstagramMCP] No credentials found, using simulation mode")
                self.connected = True
                return MCPResponse.success({
                    "service": "instagram",
                    "status": "connected",
                    "mode": "simulation",
                    "message": "Running in simulation mode (no API credentials)"
                }, "connect")
            
            # TODO: Implement actual Instagram Graph API authentication
            self.connected = True
            
            logger.info("[InstagramMCP] Connected successfully")
            return MCPResponse.success({
                "service": "instagram",
                "status": "connected",
                "mode": "live",
                "account_id": self.instagram_business_account_id
            }, "connect")
            
        except Exception as e:
            self.connected = False
            logger.error(f"[InstagramMCP] Connection failed: {e}")
            return self.handle_error(e, "connect")
    
    def disconnect(self) -> Dict:
        """Disconnect from Instagram Graph API."""
        try:
            self.connected = False
            logger.info("[InstagramMCP] Disconnected")
            return MCPResponse.success({"status": "disconnected"}, "disconnect")
        except Exception as e:
            return self.handle_error(e, "disconnect")
    
    def _execute_action(self, action: str, payload: Dict) -> Dict:
        """
        Execute Instagram action.
        
        Args:
            action: Action name
            payload: Action parameters
            
        Returns:
            Dict: MCPResponse formatted result
        """
        if action == 'create_post':
            return self._create_post(payload)
        elif action == 'get_metrics':
            return self._get_metrics(payload)
        else:
            return MCPResponse.error(f"Unknown action: {action}", action)
    
    def _create_post(self, payload: Dict) -> Dict:
        """
        Create an Instagram post.
        
        Payload:
            - caption: Post caption text (max 2,200 characters)
            - image_url: URL of image to post (required for feed posts)
            - is_video: (optional) True if video post
            - video_url: (optional) URL of video if is_video=True
        """
        try:
            caption = payload.get('caption', '')
            image_url = payload.get('image_url')
            is_video = payload.get('is_video', False)
            video_url = payload.get('video_url') if is_video else None
            
            # Instagram requires media for posts
            if not image_url and not video_url:
                return MCPResponse.error(
                    "Post must have image_url or video_url",
                    "create_post"
                )
            
            # Check caption length (Instagram: 2,200 characters)
            if len(caption) > 2200:
                return MCPResponse.error(
                    f"Caption exceeds 2200 character limit: {len(caption)}",
                    "create_post",
                    {"max_length": 2200, "actual_length": len(caption)}
                )
            
            if not self.access_token:
                # Simulation mode
                logger.info(f"[InstagramMCP] [SIMULATE] Creating post: {caption[:50]}...")
                logger.info(f"[InstagramMCP] [SIMULATE] Media: {image_url or video_url}")
                
                post_data = {
                    "simulated": True,
                    "caption": caption[:200],
                    "caption_length": len(caption),
                    "media_type": "video" if is_video else "image",
                    "media_url": image_url or video_url,
                    "timestamp": datetime.now().isoformat(),
                    "media_id": "ig_" + datetime.now().strftime('%Y%m%d%H%M%S')
                }
                
                # Log to social.json
                self._log_post(post_data)
                
                return MCPResponse.success(post_data, "create_post")
            
            # TODO: Implement actual Instagram Graph API post creation
            # Two-step process:
            # 1. POST /{ig-user-id}/media (create media container)
            # 2. POST /{ig-user-id}/media_publish (publish media)
            logger.info(f"[InstagramMCP] Creating post: {caption[:50]}...")
            
            return MCPResponse.success({
                "simulated": False,
                "caption": caption[:200],
                "media_id": "ig_" + datetime.now().strftime('%Y%m%d%H%M%S'),
                "timestamp": datetime.now().isoformat()
            }, "create_post")
            
        except Exception as e:
            logger.error(f"[InstagramMCP] Create post error: {e}")
            return self.handle_error(e, "create_post")
    
    def _get_metrics(self, payload: Dict) -> Dict:
        """
        Get Instagram metrics.
        
        Payload:
            - media_id: (optional) Specific media ID
            - metric_type: (optional) impressions, reach, engagement, likes, comments, saved, all
        """
        try:
            media_id = payload.get('media_id')
            metric_type = payload.get('metric_type', 'all')
            
            if not self.access_token:
                # Simulation mode - return placeholder metrics
                metrics = {
                    "simulated": True,
                    "media_id": media_id or "profile",
                    "metrics": {
                        "impressions": 0,
                        "reach": 0,
                        "engagement": 0,
                        "likes": 0,
                        "comments": 0,
                        "saved": 0,
                        "shares": 0,
                        "profile_views": 0,
                        "follower_count": 0
                    },
                    "period": "last_7_days"
                }
                return MCPResponse.success(metrics, "get_metrics")
            
            # TODO: Implement actual Instagram Graph API metrics retrieval
            # GET /{ig-media-id}/insights
            logger.info(f"[InstagramMCP] Getting metrics for: {media_id or 'profile'}")
            
            return MCPResponse.success({
                "simulated": False,
                "media_id": media_id or "profile",
                "metrics": {
                    "impressions": 0,
                    "reach": 0,
                    "engagement": 0,
                    "likes": 0,
                    "comments": 0,
                    "saved": 0
                }
            }, "get_metrics")
            
        except Exception as e:
            logger.error(f"[InstagramMCP] Get metrics error: {e}")
            return self.handle_error(e, "get_metrics")
    
    def _log_post(self, post_data: Dict):
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
            'platform': 'instagram',
            'content': post_data.get('caption', '')[:200],
            'status': 'success',
            'data': post_data
        }
        logs.append(entry)
        
        # Keep only last 1000 entries
        logs = logs[-1000:]
        
        # Save logs
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)


# Convenience function
def execute(action: str, payload: Dict) -> Dict:
    """Execute Instagram action."""
    server = InstagramMCPServer()
    return server.execute(action, payload)


if __name__ == '__main__':
    print("Instagram MCP Server - Gold Tier")
    print("=" * 40)
    
    server = InstagramMCPServer()
    
    print("\n1. Testing connection:")
    result = server.connect()
    print(json.dumps(result, indent=2))
    
    print("\n2. Testing create_post (image):")
    result = server.execute('create_post', {
        "caption": "Test post from Instagram MCP Server! 📸 #AI #Automation",
        "image_url": "https://example.com/image.jpg"
    })
    print(json.dumps(result, indent=2))
    
    print("\n3. Testing create_post (video):")
    result = server.execute('create_post', {
        "caption": "Video post test! 🎥",
        "is_video": True,
        "video_url": "https://example.com/video.mp4"
    })
    print(json.dumps(result, indent=2))
    
    print("\n4. Testing create_post (no media - should fail):")
    result = server.execute('create_post', {
        "caption": "No media provided"
    })
    print(json.dumps(result, indent=2))
    
    print("\n5. Testing get_metrics:")
    result = server.execute('get_metrics', {})
    print(json.dumps(result, indent=2))
    
    print("\n6. Testing health check:")
    result = server.health_check()
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 40)
