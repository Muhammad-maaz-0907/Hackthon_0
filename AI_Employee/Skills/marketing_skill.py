# Marketing Skill - Gold Tier
# Generate and post social media content across platforms

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

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
    from ..MCP.linkedin_mcp import LinkedInMCPServer
    from ..MCP.twitter_mcp import TwitterMCPServer
    from ..MCP.facebook_mcp import FacebookMCPServer
    from ..MCP.instagram_mcp import InstagramMCPServer
except ImportError:
    from MCP.linkedin_mcp import LinkedInMCPServer
    from MCP.twitter_mcp import TwitterMCPServer
    from MCP.facebook_mcp import FacebookMCPServer
    from MCP.instagram_mcp import InstagramMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
METRICS_FILE = os.path.join(DATA_DIR, 'weekly_metrics.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


class MarketingSkill(AgentSkill):
    """
    Marketing skill for social media content generation and posting.
    
    Capabilities:
    - Generate social media content ideas
    - Post to LinkedIn, Twitter, Facebook, Instagram
    - Track and store metrics
    - Generate weekly performance reports
    """
    
    def __init__(self):
        super().__init__("marketing_skill", tier="gold")
        
        # Initialize MCP servers
        self.linkedin = LinkedInMCPServer()
        self.twitter = TwitterMCPServer()
        self.facebook = FacebookMCPServer()
        self.instagram = InstagramMCPServer()
        
        # Content templates
        self.content_templates = [
            "Exciting update from our team! {topic} #Innovation #AI",
            "Just discovered something amazing about {topic}. Here's what I learned... 🧵",
            "Behind the scenes: How we're using AI to transform {topic}",
            "Quick tip for {topic}: {tip} #ProductivityTips",
            "The future of {topic} is here! Check out what's new 🚀"
        ]
    
    def validate(self, context: Dict) -> tuple:
        """Validate marketing context."""
        action = context.get('action')
        valid_actions = ['generate_content', 'post', 'post_all', 'get_metrics', 'weekly_report']
        
        if not action:
            return False, "Missing required field: 'action'"
        
        if action not in valid_actions:
            return False, f"Invalid action. Must be one of: {valid_actions}"
        
        if action == 'post' and not context.get('platform'):
            return False, "Missing required field: 'platform' for post action"
        
        return True, None
    
    def execute(self, context: Dict) -> Dict:
        """
        Execute marketing skill.
        
        Context:
            - action: generate_content | post | post_all | get_metrics | weekly_report
            - topic: (optional) Topic for content generation
            - content: (optional) Custom content to post
            - platform: (optional) Platform to post to
            - image_url: (optional) Image URL for post
        """
        action = context.get('action')
        
        if action == 'generate_content':
            return self._generate_content(context)
        elif action == 'post':
            return self._post(context)
        elif action == 'post_all':
            return self._post_all(context)
        elif action == 'get_metrics':
            return self._get_metrics(context)
        elif action == 'weekly_report':
            return self._weekly_report(context)
        else:
            return AgentSkillResponse.error(f"Unknown action: {action}", self.skill_name)
    
    def _generate_content(self, context: Dict) -> Dict:
        """Generate social media content ideas."""
        topic = context.get('topic', 'AI and automation')
        count = context.get('count', 5)
        
        content_ideas = []
        
        # Generate variations
        for i, template in enumerate(self.content_templates[:count]):
            content = template.format(
                topic=topic,
                tip="Automate repetitive tasks to save 10+ hours per week"
            )
            content_ideas.append({
                "id": i + 1,
                "content": content,
                "platform": "all",
                "character_count": len(content),
                "hashtags": self._extract_hashtags(content)
            })
        
        logger.info(f"Generated {len(content_ideas)} content ideas for topic: {topic}")
        
        return AgentSkillResponse.success({
            "topic": topic,
            "ideas": content_ideas,
            "count": len(content_ideas)
        }, self.skill_name)
    
    def _post(self, context: Dict) -> Dict:
        """Post to a specific platform."""
        platform = context.get('platform').lower()
        content = context.get('content')
        image_url = context.get('image_url')
        
        if not content:
            return AgentSkillResponse.error(
                "Missing required field: 'content'",
                self.skill_name
            )
        
        result = None
        
        if platform == 'linkedin':
            result = self.linkedin.execute('create_post', {
                "content": content,
                "image_url": image_url
            })
        elif platform == 'twitter' or platform == 'x':
            result = self.twitter.execute('create_post', {
                "content": content
            })
        elif platform == 'facebook':
            result = self.facebook.execute('create_post', {
                "message": content,
                "photo_url": image_url
            })
        elif platform == 'instagram':
            result = self.instagram.execute('create_post', {
                "caption": content,
                "image_url": image_url or "https://example.com/placeholder.jpg"
            })
        else:
            return AgentSkillResponse.error(
                f"Unknown platform: {platform}",
                self.skill_name,
                {"valid_platforms": ["linkedin", "twitter", "facebook", "instagram"]}
            )
        
        # Store metrics
        self._store_post_metrics(platform, result)
        
        return AgentSkillResponse.success({
            "platform": platform,
            "content": content[:100],
            "post_result": result
        }, self.skill_name)
    
    def _post_all(self, context: Dict) -> Dict:
        """Post to all platforms."""
        content = context.get('content')
        image_url = context.get('image_url')
        
        if not content:
            return AgentSkillResponse.error(
                "Missing required field: 'content'",
                self.skill_name
            )
        
        results = {}
        
        # Post to each platform
        platforms = [
            ('linkedin', self.linkedin),
            ('twitter', self.twitter),
            ('facebook', self.facebook),
            ('instagram', self.instagram)
        ]
        
        for platform_name, mcp_server in platforms:
            try:
                if platform_name == 'linkedin':
                    result = mcp_server.execute('create_post', {
                        "content": content,
                        "image_url": image_url
                    })
                elif platform_name == 'twitter':
                    result = mcp_server.execute('create_post', {
                        "content": content
                    })
                elif platform_name == 'facebook':
                    result = mcp_server.execute('create_post', {
                        "message": content,
                        "photo_url": image_url
                    })
                elif platform_name == 'instagram':
                    result = mcp_server.execute('create_post', {
                        "caption": content,
                        "image_url": image_url or "https://example.com/placeholder.jpg"
                    })
                
                results[platform_name] = result
                self._store_post_metrics(platform_name, result)
                
            except Exception as e:
                results[platform_name] = {"status": "error", "error": str(e)}
        
        return AgentSkillResponse.success({
            "content": content[:100],
            "platforms": results,
            "success_count": sum(1 for r in results.values() if r.get('status') == 'success')
        }, self.skill_name)
    
    def _get_metrics(self, context: Dict) -> Dict:
        """Get social media metrics."""
        platform = context.get('platform', 'all')
        
        metrics = {}
        
        if platform == 'all' or platform == 'linkedin':
            result = self.linkedin.execute('get_metrics', {})
            metrics['linkedin'] = result.get('data', {})
        
        if platform == 'all' or platform == 'twitter':
            result = self.twitter.execute('get_metrics', {})
            metrics['twitter'] = result.get('data', {})
        
        if platform == 'all' or platform == 'facebook':
            result = self.facebook.execute('get_metrics', {})
            metrics['facebook'] = result.get('data', {})
        
        if platform == 'all' or platform == 'instagram':
            result = self.instagram.execute('get_metrics', {})
            metrics['instagram'] = result.get('data', {})
        
        return AgentSkillResponse.success({
            "platform": platform,
            "metrics": metrics
        }, self.skill_name)
    
    def _weekly_report(self, context: Dict) -> Dict:
        """Generate weekly performance report."""
        week_start = context.get('week_start')
        
        # Load existing metrics
        all_metrics = self._load_weekly_metrics()
        
        # Calculate summary
        total_posts = 0
        platforms = {}
        
        for week_data in all_metrics:
            for platform, data in week_data.get('posts', {}).items():
                if platform not in platforms:
                    platforms[platform] = 0
                platforms[platform] += len(data) if isinstance(data, list) else 1
                total_posts += len(data) if isinstance(data, list) else 1
        
        return AgentSkillResponse.success({
            "report_type": "weekly_summary",
            "week_start": week_start or "N/A",
            "total_posts": total_posts,
            "platforms": platforms,
            "data_file": METRICS_FILE
        }, self.skill_name)
    
    def _store_post_metrics(self, platform: str, result: Dict):
        """Store post metrics to weekly_metrics.json."""
        try:
            # Load existing metrics
            metrics = []
            if os.path.exists(METRICS_FILE):
                with open(METRICS_FILE, 'r', encoding='utf-8') as f:
                    try:
                        metrics = json.load(f)
                    except json.JSONDecodeError:
                        metrics = []
            
            # Get current week
            now = datetime.now()
            week_start = now - timedelta(days=now.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            # Find or create week entry
            week_entry = None
            for entry in metrics:
                if entry.get('week') == week_key:
                    week_entry = entry
                    break
            
            if not week_entry:
                week_entry = {
                    'week': week_key,
                    'posts': {},
                    'created_at': now.isoformat()
                }
                metrics.append(week_entry)
            
            # Store post
            if platform not in week_entry['posts']:
                week_entry['posts'][platform] = []
            
            week_entry['posts'][platform].append({
                'timestamp': now.isoformat(),
                'result': result
            })
            
            # Keep only last 52 weeks
            metrics = metrics[-52:]
            
            # Save metrics
            with open(METRICS_FILE, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2)
            
            logger.debug(f"Stored metrics for platform: {platform}")
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def _load_weekly_metrics(self) -> List[Dict]:
        """Load weekly metrics from file."""
        try:
            if os.path.exists(METRICS_FILE):
                with open(METRICS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
        return []
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content."""
        import re
        return re.findall(r'#\w+', content)


# Convenience function
def execute(action: str, **kwargs) -> Dict:
    """Execute marketing skill."""
    skill = MarketingSkill()
    return skill._execute_with_logging({"action": action, **kwargs})


if __name__ == '__main__':
    print("Marketing Skill - Gold Tier")
    print("=" * 40)
    
    skill = MarketingSkill()
    
    print("\n1. Testing generate_content:")
    result = skill._execute_with_logging({
        "action": "generate_content",
        "topic": "AI automation"
    })
    print(json.dumps(result, indent=2))
    
    print("\n2. Testing post (LinkedIn):")
    result = skill._execute_with_logging({
        "action": "post",
        "platform": "linkedin",
        "content": "Test post from Marketing Skill! 🚀 #AI #Automation"
    })
    print(json.dumps(result, indent=2))
    
    print("\n3. Testing get_metrics:")
    result = skill._execute_with_logging({
        "action": "get_metrics",
        "platform": "all"
    })
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 40)
