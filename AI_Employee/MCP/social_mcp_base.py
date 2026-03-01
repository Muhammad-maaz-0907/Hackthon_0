# Social MCP Base - Gold Tier MCP Architecture
# Provides MCP (Model Context Protocol) server for social media operations
# Extends MCPServerBase for standardized error handling and retry logic

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Import base class from mcp_server_base
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


class SocialMCPServer(MCPServerBase):
    """
    MCP Server for social media operations.
    Extends MCPServerBase with social-specific actions.
    """
    
    def __init__(self):
        super().__init__("social_mcp", max_retries=3, retry_delay=1.0)
    
    def _execute_action(self, action: str, payload: Dict) -> Dict:
        """
        Execute MCP action with payload.
        
        Supported Actions:
            - post_facebook: {"content": "text"}
            - post_instagram: {"content": "text", "image_path": "path"}
            - post_x: {"content": "text"}
            - get_stats: {"platform": "facebook|instagram|x"}
            - schedule_post: {"platform": "...", "content": "...", "scheduled_time": "..."}
        
        Args:
            action: Action to execute
            payload: Action parameters
            
        Returns:
            dict: MCPResponse formatted result
        """
        logger.info(f"Social MCP executing: {action}")
        
        # Import social posters dynamically
        from ..Social.facebook_poster import post as facebook_post
        from ..Social.instagram_poster import post as instagram_post
        from ..Social.x_poster import post as x_post
        
        # Route to appropriate handler
        if action == 'post_facebook':
            content = payload.get('content', '')
            result = facebook_post(content)
            return MCPResponse.success({
                "platform": "facebook",
                "post_result": result
            }, action)
        
        elif action == 'post_instagram':
            content = payload.get('content', '')
            image_path = payload.get('image_path')
            result = instagram_post(content, image_path)
            return MCPResponse.success({
                "platform": "instagram",
                "post_result": result
            }, action)
        
        elif action == 'post_x':
            content = payload.get('content', '')
            result = x_post(content)
            return MCPResponse.success({
                "platform": "x",
                "post_result": result
            }, action)
        
        elif action == 'get_stats':
            platform = payload.get('platform', 'all')
            stats = self._get_platform_stats(platform)
            return MCPResponse.success(stats, action)
        
        elif action == 'schedule_post':
            platform = payload.get('platform')
            content = payload.get('content')
            scheduled_time = payload.get('scheduled_time')
            result = self._schedule_post(platform, content, scheduled_time)
            return MCPResponse.success(result, action)
        
        else:
            return MCPResponse.error(f"Unknown action: {action}", action)
    
    def _get_platform_stats(self, platform: str) -> Dict:
        """Get statistics for a platform."""
        # TODO: Implement actual stats retrieval from social.json logs
        log_file = os.path.join(LOGS_DIR, 'social.json')
        
        stats = {
            "platform": platform,
            "posts_today": 0,
            "total_posts": 0,
            "engagement": {}
        }
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    
                # Count posts for platform
                now = datetime.now()
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                
                for entry in logs:
                    entry_platform = entry.get('platform', '')
                    entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                    
                    if platform == 'all' or entry_platform == platform:
                        stats['total_posts'] += 1
                        if entry_time >= today_start:
                            stats['posts_today'] += 1
            except Exception as e:
                logger.error(f"Error reading social logs: {e}")
        
        return stats
    
    def _schedule_post(self, platform: str, content: str, 
                       scheduled_time: str) -> Dict:
        """Schedule a post for later."""
        # TODO: Implement scheduling system
        return {
            "platform": platform,
            "content": content[:100],
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "scheduled_at": datetime.now().isoformat()
        }


# Convenience functions for backward compatibility
def execute(action: str, payload: Dict) -> Dict:
    """Execute an action using SocialMCPServer."""
    server = SocialMCPServer()
    return server.execute(action, payload)


def retry_logic(func, action: str, payload: Dict, 
                max_retries: int = None, delay: float = None) -> Dict:
    """Execute function with retry logic using SocialMCPServer."""
    server = SocialMCPServer()
    return server.retry_logic(func, action, payload, max_retries, delay)


# MCP Server entry point for CLI testing
if __name__ == '__main__':
    print("Social MCP Base - Gold Tier")
    print("=" * 40)
    
    # Test using the class
    server = SocialMCPServer()
    
    print("\n1. Testing connection:")
    result = server.connect()
    print(json.dumps(result, indent=2))
    
    print("\n2. Testing post_x action:")
    test_payload = {"content": "Test post from MCP"}
    result = server.execute('post_x', test_payload)
    print(json.dumps(result, indent=2))
    
    print("\n3. Testing get_stats action:")
    result = server.execute('get_stats', {"platform": "all"})
    print(json.dumps(result, indent=2))
    
    print("\n4. Testing health check:")
    result = server.health_check()
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 40)
    print("Social MCP Base test complete!")
