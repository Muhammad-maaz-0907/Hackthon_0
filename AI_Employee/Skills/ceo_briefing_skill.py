# CEO Briefing Skill - Gold Tier
# Generate executive summaries and briefings

import os
import json
import logging
from datetime import datetime, timedelta
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
    from ..MCP.linkedin_mcp import LinkedInMCPServer
    from ..MCP.twitter_mcp import TwitterMCPServer
    from ..MCP.facebook_mcp import FacebookMCPServer
    from ..MCP.instagram_mcp import InstagramMCPServer
    from ..MCP.whatsapp_mcp import WhatsAppMCPServer
except ImportError:
    from MCP.gmail_mcp import GmailMCPServer
    from MCP.linkedin_mcp import LinkedInMCPServer
    from MCP.twitter_mcp import TwitterMCPServer
    from MCP.facebook_mcp import FacebookMCPServer
    from MCP.instagram_mcp import InstagramMCPServer
    from MCP.whatsapp_mcp import WhatsAppMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
AUDIT_DIR = os.path.join(os.path.dirname(__file__), '..', 'Audits')
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
NEEDS_ACTION_DIR = os.path.join(os.path.dirname(__file__), '..', 'Needs_Action')

BRIEFING_FILE = os.path.join(AUDIT_DIR, 'CEO_Briefing.md')
METRICS_FILE = os.path.join(DATA_DIR, 'weekly_metrics.json')
INBOUND_LOG = os.path.join(DATA_DIR, 'inbound_requests.json')

# Ensure directories exist
os.makedirs(AUDIT_DIR, exist_ok=True)


class CEOBriefingSkill(AgentSkill):
    """
    CEO Briefing skill for generating executive summaries.
    
    Capabilities:
    - Pull social media metrics
    - Pull Gmail insights
    - Summarize activity across all channels
    - Generate CEO_Briefing.md report
    - Identify bottlenecks and suggestions
    """
    
    def __init__(self):
        super().__init__("ceo_briefing_skill", tier="gold")
        
        # Initialize MCP servers
        self.gmail = GmailMCPServer()
        self.linkedin = LinkedInMCPServer()
        self.twitter = TwitterMCPServer()
        self.facebook = FacebookMCPServer()
        self.instagram = InstagramMCPServer()
        self.whatsapp = WhatsAppMCPServer()
    
    def validate(self, context: Dict) -> tuple:
        """Validate briefing context."""
        action = context.get('action')
        valid_actions = ['generate', 'daily', 'weekly', 'social_summary', 'email_summary']
        
        if not action:
            return False, "Missing required field: 'action'"
        
        # Allow both direct actions and internal prefixed actions
        if action not in valid_actions and not action.startswith('_'):
            # Check if it's a valid internal method
            internal_action = f"_{action}" if not action.startswith('_') else action
            if not hasattr(self, internal_action):
                return False, f"Invalid action: {action}"
        
        return True, None
    
    def execute(self, context: Dict) -> Dict:
        """
        Execute CEO briefing skill.
        
        Context:
            - action: generate | daily | weekly | social_summary | email_summary
            - period: (optional) Number of days to cover
            - include_recommendations: (optional) Include AI recommendations
        """
        action = context.get('action')
        
        if action == 'generate':
            return self._generate(context)
        elif action == 'daily':
            return self._daily_briefing(context)
        elif action == 'weekly':
            return self._weekly_briefing(context)
        elif action == 'social_summary':
            return self._social_summary(context)
        elif action == 'email_summary':
            return self._email_summary(context)
        else:
            return AgentSkillResponse.error(f"Unknown action: {action}", self.skill_name)
    
    def _generate(self, context: Dict) -> Dict:
        """Generate full CEO briefing."""
        period = context.get('period', 7)
        include_recommendations = context.get('include_recommendations', True)
        
        logger.info(f"Generating CEO briefing for last {period} days")
        
        # Gather all data
        social_data = self._gather_social_metrics(period)
        email_data = self._gather_email_insights(period)
        whatsapp_data = self._gather_whatsapp_insights(period)
        tasks_data = self._gather_tasks_status()
        
        # Generate briefing
        briefing = self._compile_briefing({
            'social': social_data,
            'email': email_data,
            'whatsapp': whatsapp_data,
            'tasks': tasks_data,
            'period_days': period,
            'include_recommendations': include_recommendations
        })
        
        # Save briefing
        self._save_briefing(briefing)
        
        return AgentSkillResponse.success({
            "briefing": briefing,
            "file": BRIEFING_FILE,
            "generated_at": datetime.now().isoformat()
        }, self.skill_name)
    
    def _daily_briefing(self, context: Dict) -> Dict:
        """Generate daily briefing."""
        return self._generate({"period": 1, "include_recommendations": True})
    
    def _weekly_briefing(self, context: Dict) -> Dict:
        """Generate weekly briefing."""
        return self._generate({"period": 7, "include_recommendations": True})
    
    def _social_summary(self, context: Dict) -> Dict:
        """Get social media summary."""
        period = context.get('period', 7)
        
        social_data = self._gather_social_metrics(period)
        
        return AgentSkillResponse.success({
            "period_days": period,
            "social_metrics": social_data
        }, self.skill_name)
    
    def _email_summary(self, context: Dict) -> Dict:
        """Get email summary."""
        period = context.get('period', 7)
        
        email_data = self._gather_email_insights(period)
        
        return AgentSkillResponse.success({
            "period_days": period,
            "email_metrics": email_data
        }, self.skill_name)
    
    def _gather_social_metrics(self, period: int) -> Dict:
        """Gather social media metrics from all platforms."""
        metrics = {}
        
        # LinkedIn
        try:
            result = self.linkedin.execute('get_metrics', {})
            metrics['linkedin'] = result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to get LinkedIn metrics: {e}")
            metrics['linkedin'] = {"error": str(e)}
        
        # Twitter
        try:
            result = self.twitter.execute('get_metrics', {})
            metrics['twitter'] = result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to get Twitter metrics: {e}")
            metrics['twitter'] = {"error": str(e)}
        
        # Facebook
        try:
            result = self.facebook.execute('get_metrics', {})
            metrics['facebook'] = result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to get Facebook metrics: {e}")
            metrics['facebook'] = {"error": str(e)}
        
        # Instagram
        try:
            result = self.instagram.execute('get_metrics', {})
            metrics['instagram'] = result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to get Instagram metrics: {e}")
            metrics['instagram'] = {"error": str(e)}
        
        # Load historical metrics
        historical = self._load_weekly_metrics()
        
        # Calculate totals
        total_posts = 0
        for week_data in historical:
            for platform, posts in week_data.get('posts', {}).items():
                total_posts += len(posts) if isinstance(posts, list) else 1
        
        metrics['summary'] = {
            "total_posts_all_time": total_posts,
            "platforms_tracked": 4,
            "period_days": period
        }
        
        return metrics
    
    def _gather_email_insights(self, period: int) -> Dict:
        """Gather Gmail insights."""
        insights = {
            "period_days": period,
            "unread_count": 0,
            "processed_count": 0,
            "categories": {}
        }
        
        # Get unread count
        try:
            result = self.gmail.execute('read_unread', {"max_results": 100})
            insights['unread_count'] = result.get('data', {}).get('count', 0)
        except Exception as e:
            logger.error(f"Failed to get Gmail unread: {e}")
        
        # Load inbound log for processed emails
        try:
            if os.path.exists(INBOUND_LOG):
                with open(INBOUND_LOG, 'r', encoding='utf-8') as f:
                    inbound_logs = json.load(f)
                
                # Filter by period and source
                cutoff = datetime.now() - timedelta(days=period)
                email_logs = [
                    log for log in inbound_logs
                    if log.get('source') == 'email' and
                    datetime.fromisoformat(log.get('timestamp', '2000-01-01')) > cutoff
                ]
                
                insights['processed_count'] = len(email_logs)
                
                # Categorize
                categories = {}
                for log in email_logs:
                    category = log.get('data', {}).get('category', 'unknown')
                    categories[category] = categories.get(category, 0) + 1
                
                insights['categories'] = categories
        except Exception as e:
            logger.error(f"Failed to load inbound logs: {e}")
        
        return insights
    
    def _gather_whatsapp_insights(self, period: int) -> Dict:
        """Gather WhatsApp insights."""
        insights = {
            "period_days": period,
            "message_count": 0,
            "contacts": set()
        }
        
        # Load inbound log for WhatsApp
        try:
            if os.path.exists(INBOUND_LOG):
                with open(INBOUND_LOG, 'r', encoding='utf-8') as f:
                    inbound_logs = json.load(f)
                
                # Filter by period and source
                cutoff = datetime.now() - timedelta(days=period)
                whatsapp_logs = [
                    log for log in inbound_logs
                    if log.get('source') == 'whatsapp' and
                    datetime.fromisoformat(log.get('timestamp', '2000-01-01')) > cutoff
                ]
                
                insights['message_count'] = len(whatsapp_logs)
                insights['contacts'] = list(set(
                    log.get('data', {}).get('from', 'unknown')
                    for log in whatsapp_logs
                ))
        except Exception as e:
            logger.error(f"Failed to load WhatsApp logs: {e}")
        
        insights['contacts'] = list(insights['contacts'])
        return insights
    
    def _gather_tasks_status(self) -> Dict:
        """Gather tasks status from Needs_Action folder."""
        tasks = {
            "pending": 0,
            "completed_today": 0,
            "by_type": {}
        }
        
        try:
            if os.path.exists(NEEDS_ACTION_DIR):
                for filename in os.listdir(NEEDS_ACTION_DIR):
                    if filename.endswith('.md'):
                        tasks['pending'] += 1
                        
                        # Extract type from file
                        if filename.startswith('email_'):
                            tasks['by_type']['email'] = tasks['by_type'].get('email', 0) + 1
                        elif filename.startswith('whatsapp_'):
                            tasks['by_type']['whatsapp'] = tasks['by_type'].get('whatsapp', 0) + 1
                        elif filename.startswith('linkedin_'):
                            tasks['by_type']['linkedin'] = tasks['by_type'].get('linkedin', 0) + 1
        except Exception as e:
            logger.error(f"Failed to gather tasks status: {e}")
        
        return tasks
    
    def _compile_briefing(self, data: Dict) -> Dict:
        """Compile all data into briefing format."""
        social = data.get('social', {})
        email = data.get('email', {})
        whatsapp = data.get('whatsapp', {})
        tasks = data.get('tasks', {})
        period = data.get('period_days', 7)
        
        briefing = {
            "generated_at": datetime.now().isoformat(),
            "period": f"Last {period} days",
            "sections": {}
        }
        
        # Revenue Summary (placeholder)
        briefing['sections']['revenue_summary'] = {
            "daily_revenue": "$[PLACEHOLDER]",
            "weekly_revenue": "$[PLACEHOLDER]",
            "monthly_revenue": "$[PLACEHOLDER]",
            "note": "Revenue tracking not yet integrated"
        }
        
        # Social Performance
        briefing['sections']['social_performance'] = {
            "linkedin": social.get('linkedin', {}),
            "twitter": social.get('twitter', {}),
            "facebook": social.get('facebook', {}),
            "instagram": social.get('instagram', {}),
            "summary": social.get('summary', {})
        }
        
        # Email Communications
        briefing['sections']['email_communications'] = {
            "unread_count": email.get('unread_count', 0),
            "processed_count": email.get('processed_count', 0),
            "categories": email.get('categories', {})
        }
        
        # WhatsApp Messages
        briefing['sections']['whatsapp_messages'] = {
            "message_count": whatsapp.get('message_count', 0),
            "unique_contacts": len(whatsapp.get('contacts', [])),
            "contacts": whatsapp.get('contacts', [])[:10]  # Top 10
        }
        
        # Tasks Status
        briefing['sections']['tasks_status'] = {
            "pending": tasks.get('pending', 0),
            "by_type": tasks.get('by_type', {})
        }
        
        # Bottlenecks (AI-generated)
        briefing['sections']['bottlenecks'] = self._identify_bottlenecks({
            "email": email,
            "tasks": tasks,
            "social": social
        })
        
        # Suggestions (AI-generated)
        if data.get('include_recommendations', True):
            briefing['sections']['suggestions'] = self._generate_suggestions({
                "email": email,
                "whatsapp": whatsapp,
                "tasks": tasks,
                "social": social
            })
        
        # Risks
        briefing['sections']['risks'] = self._identify_risks({
            "email": email,
            "tasks": tasks
        })
        
        return briefing
    
    def _identify_bottlenecks(self, data: Dict) -> List[Dict]:
        """Identify bottlenecks from data."""
        bottlenecks = []
        
        # Check email backlog
        email_unread = data.get('email', {}).get('unread_count', 0)
        if email_unread > 20:
            bottlenecks.append({
                "type": "email_backlog",
                "severity": "high" if email_unread > 50 else "medium",
                "description": f"High email backlog: {email_unread} unread emails",
                "recommendation": "Consider auto-responders or email triage"
            })
        
        # Check task backlog
        tasks_pending = data.get('tasks', {}).get('pending', 0)
        if tasks_pending > 10:
            bottlenecks.append({
                "type": "task_backlog",
                "severity": "high" if tasks_pending > 30 else "medium",
                "description": f"Task backlog: {tasks_pending} pending items",
                "recommendation": "Prioritize and delegate tasks"
            })
        
        return bottlenecks
    
    def _generate_suggestions(self, data: Dict) -> List[Dict]:
        """Generate AI suggestions."""
        suggestions = []
        
        # Email suggestions
        email = data.get('email', {})
        if email.get('unread_count', 0) > 0:
            suggestions.append({
                "priority": "high",
                "area": "email",
                "suggestion": f"Process {email.get('unread_count')} unread emails",
                "expected_impact": "Improved response time and customer satisfaction"
            })
        
        # Task suggestions
        tasks = data.get('tasks', {})
        if tasks.get('pending', 0) > 0:
            suggestions.append({
                "priority": "medium",
                "area": "tasks",
                "suggestion": f"Clear {tasks.get('pending')} pending tasks in Needs_Action",
                "expected_impact": "Reduced cognitive load and better focus"
            })
        
        # Social media suggestions
        social = data.get('social', {})
        summary = social.get('summary', {})
        if summary.get('total_posts_all_time', 0) < 10:
            suggestions.append({
                "priority": "low",
                "area": "social_media",
                "suggestion": "Increase social media posting frequency",
                "expected_impact": "Better brand visibility and engagement"
            })
        
        return suggestions
    
    def _identify_risks(self, data: Dict) -> List[Dict]:
        """Identify potential risks."""
        risks = []
        
        # Email risk
        email = data.get('email', {})
        if email.get('unread_count', 0) > 100:
            risks.append({
                "risk": "Missed important communications",
                "probability": "high",
                "impact": "high",
                "mitigation": "Implement email filtering and auto-responses"
            })
        
        # Task risk
        tasks = data.get('tasks', {})
        if tasks.get('pending', 0) > 50:
            risks.append({
                "risk": "Task overload leading to burnout",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Delegate tasks and set realistic deadlines"
            })
        
        return risks
    
    def _save_briefing(self, briefing: Dict):
        """Save briefing to markdown file."""
        try:
            md_content = self._convert_to_markdown(briefing)
            
            with open(BRIEFING_FILE, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"CEO briefing saved to: {BRIEFING_FILE}")
            
        except Exception as e:
            logger.error(f"Failed to save briefing: {e}")
    
    def _convert_to_markdown(self, briefing: Dict) -> str:
        """Convert briefing dict to markdown format."""
        sections = briefing.get('sections', {})
        
        md = f"""# CEO Briefing Report

**Generated:** {briefing.get('generated_at', 'N/A')}
**Period:** {briefing.get('period', 'N/A')}

---

## Revenue Summary

| Metric | Value | Change |
|--------|-------|--------|
| Daily Revenue | {sections.get('revenue_summary', {}).get('daily_revenue', 'N/A')} | - |
| Weekly Revenue | {sections.get('revenue_summary', {}).get('weekly_revenue', 'N/A')} | - |
| Monthly Revenue | {sections.get('revenue_summary', {}).get('monthly_revenue', 'N/A')} | - |

> {sections.get('revenue_summary', {}).get('note', '')}

---

## Social Performance

| Platform | Status | Metrics |
|----------|--------|---------|
| LinkedIn | {'✅' if sections.get('social_performance', {}).get('linkedin') else '⚠️'} | {json.dumps(sections.get('social_performance', {}).get('linkedin', {}))[:100]} |
| Twitter | {'✅' if sections.get('social_performance', {}).get('twitter') else '⚠️'} | {json.dumps(sections.get('social_performance', {}).get('twitter', {}))[:100]} |
| Facebook | {'✅' if sections.get('social_performance', {}).get('facebook') else '⚠️'} | {json.dumps(sections.get('social_performance', {}).get('facebook', {}))[:100]} |
| Instagram | {'✅' if sections.get('social_performance', {}).get('instagram') else '⚠️'} | {json.dumps(sections.get('social_performance', {}).get('instagram', {}))[:100]} |

**Summary:** {json.dumps(sections.get('social_performance', {}).get('summary', {}))}

---

## Email Communications

- **Unread:** {sections.get('email_communications', {}).get('unread_count', 0)}
- **Processed (period):** {sections.get('email_communications', {}).get('processed_count', 0)}
- **Categories:** {sections.get('email_communications', {}).get('categories', {})}

---

## WhatsApp Messages

- **Messages (period):** {sections.get('whatsapp_messages', {}).get('message_count', 0)}
- **Unique Contacts:** {sections.get('whatsapp_messages', {}).get('unique_contacts', 0)}
- **Top Contacts:** {', '.join(sections.get('whatsapp_messages', {}).get('contacts', [])[:5])}

---

## Tasks Status

- **Pending:** {sections.get('tasks_status', {}).get('pending', 0)}
- **By Type:** {sections.get('tasks_status', {}).get('by_type', {})}

---

## Bottlenecks

"""
        bottlenecks = sections.get('bottlenecks', [])
        if bottlenecks:
            for b in bottlenecks:
                md += f"- **[{b.get('severity', 'medium').upper()}]** {b.get('description', '')}\n"
                md += f"  - Recommendation: {b.get('recommendation', '')}\n"
        else:
            md += "No critical bottlenecks identified.\n"
        
        md += """
---

## Suggestions

"""
        suggestions = sections.get('suggestions', [])
        if suggestions:
            for s in suggestions:
                md += f"1. **[{s.get('priority', 'medium').upper()}]** {s.get('suggestion', '')}\n"
                md += f"   - Expected Impact: {s.get('expected_impact', '')}\n"
        else:
            md += "No suggestions at this time.\n"
        
        md += """
---

## Risks

"""
        risks = sections.get('risks', [])
        if risks:
            for r in risks:
                md += f"- **{r.get('risk', '')}**\n"
                md += f"  - Probability: {r.get('probability', 'N/A')} | Impact: {r.get('impact', 'N/A')}\n"
                md += f"  - Mitigation: {r.get('mitigation', '')}\n"
        else:
            md += "No critical risks identified.\n"
        
        md += """
---

*Generated by AI Employee Vault - CEO Briefing Skill*
"""
        return md
    
    def _load_weekly_metrics(self) -> List[Dict]:
        """Load weekly metrics from file."""
        try:
            if os.path.exists(METRICS_FILE):
                with open(METRICS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
        return []


# Convenience function
def execute(action: str, **kwargs) -> Dict:
    """Execute CEO briefing skill."""
    skill = CEOBriefingSkill()
    return skill._execute_with_logging({"action": action, **kwargs})


if __name__ == '__main__':
    print("CEO Briefing Skill - Gold Tier")
    print("=" * 40)
    
    skill = CEOBriefingSkill()
    
    print("\n1. Testing social_summary:")
    result = skill._execute_with_logging({
        "action": "social_summary",
        "period": 7
    })
    print(json.dumps(result, indent=2))
    
    print("\n2. Testing email_summary:")
    result = skill._execute_with_logging({
        "action": "email_summary",
        "period": 7
    })
    print(json.dumps(result, indent=2))
    
    print("\n3. Testing daily (using generate with period=1):")
    result = skill._execute_with_logging({
        "action": "generate",
        "period": 1
    })
    print(json.dumps(result.get('data', {}).get('briefing', {}), indent=2)[:500] + "...")
    
    print(f"\n4. Briefing saved to: {BRIEFING_FILE}")
    
    print("\n" + "=" * 40)
