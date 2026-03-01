# Weekly Audit Engine - Gold Tier
# Generates comprehensive weekly executive reports

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
AUDIT_DIR = os.path.join(os.path.dirname(__file__), '..', 'Audits')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
NEEDS_ACTION_DIR = os.path.join(os.path.dirname(__file__), '..', 'Needs_Action')

# Files
METRICS_FILE = os.path.join(DATA_DIR, 'weekly_metrics.json')
INBOUND_FILE = os.path.join(DATA_DIR, 'inbound_requests.json')
SKILLS_AUDIT_FILE = os.path.join(LOGS_DIR, 'skills_audit.json')
RALPH_DECISIONS_FILE = os.path.join(LOGS_DIR, 'ralph_decisions.json')

# Output
WEEKLY_REPORT_FILE = os.path.join(AUDIT_DIR, 'Weekly_Audit_Report.md')
CEO_BRIEFING_FILE = os.path.join(AUDIT_DIR, 'CEO_Briefing.md')

# Ensure directories exist
os.makedirs(AUDIT_DIR, exist_ok=True)


class WeeklyAuditEngine:
    """
    Weekly Audit Engine for generating comprehensive executive reports.
    
    Pulls data from:
    - Social media metrics (Data/weekly_metrics.json)
    - Gmail statistics
    - WhatsApp activity
    - Task processing logs
    
    Generates:
    - Audit/CEO_Briefing.md with executive summary
    """
    
    def __init__(self):
        self.report_date = datetime.now()
        self.data = {
            'social': {},
            'email': {},
            'whatsapp': {},
            'tasks': {},
            'issues': [],
            'recommendations': []
        }
        logger.info("Weekly Audit Engine initialized")
    
    def generate_report(self, week_start: datetime = None, 
                        week_end: datetime = None) -> Dict:
        """
        Generate comprehensive weekly audit report.
        
        Args:
            week_start: Start of week (defaults to 7 days ago)
            week_end: End of week (defaults to today)
            
        Returns:
            Dict: Report data
        """
        # Set date range
        if not week_end:
            week_end = datetime.now()
        if not week_start:
            week_start = week_end - timedelta(days=7)
        
        logger.info(f"Generating weekly audit: {week_start.date()} to {week_end.date()}")
        
        # Pull all data
        self._pull_social_metrics(week_start, week_end)
        self._pull_email_statistics(week_start, week_end)
        self._pull_whatsapp_activity(week_start, week_end)
        self._pull_task_statistics(week_start, week_end)
        self._analyze_issues()
        self._generate_recommendations()
        
        # Generate report
        report = self._compile_report(week_start, week_end)
        
        # Save reports
        self._save_weekly_report(report)
        self._save_ceo_briefing(report)
        
        logger.info(f"Weekly audit complete. Report saved to: {WEEKLY_REPORT_FILE}")
        
        return report
    
    def _pull_social_metrics(self, week_start: datetime, week_end: datetime):
        """Pull social media metrics from weekly_metrics.json."""
        try:
            if not os.path.exists(METRICS_FILE):
                logger.warning("No social metrics file found")
                self.data['social'] = {
                    'total_posts': 0,
                    'by_platform': {},
                    'posts': []
                }
                return
            
            with open(METRICS_FILE, 'r', encoding='utf-8') as f:
                all_metrics = json.load(f)
            
            # Filter by date range
            week_posts = []
            platform_counts = defaultdict(int)
            
            for week_data in all_metrics:
                week_date = datetime.fromisoformat(week_data.get('week', '2000-01-01'))
                if week_start <= week_date <= week_end:
                    for platform, posts in week_data.get('posts', {}).items():
                        if isinstance(posts, list):
                            for post in posts:
                                week_posts.append({
                                    'platform': platform,
                                    'timestamp': post.get('timestamp'),
                                    'result': post.get('result', {})
                                })
                                platform_counts[platform] += 1
            
            self.data['social'] = {
                'total_posts': len(week_posts),
                'by_platform': dict(platform_counts),
                'posts': week_posts,
                'platforms_active': len(platform_counts)
            }
            
            logger.info(f"Pulled {len(week_posts)} social posts")
            
        except Exception as e:
            logger.error(f"Failed to pull social metrics: {e}")
            self.data['social'] = {'total_posts': 0, 'by_platform': {}, 'posts': []}
    
    def _pull_email_statistics(self, week_start: datetime, week_end: datetime):
        """Pull Gmail statistics from inbound requests and skills audit."""
        try:
            email_stats = {
                'total_processed': 0,
                'unread_current': 0,
                'by_category': defaultdict(int),
                'responses_sent': 0
            }
            
            # Pull from inbound requests
            if os.path.exists(INBOUND_FILE):
                with open(INBOUND_FILE, 'r', encoding='utf-8') as f:
                    inbound_logs = json.load(f)
                
                for entry in inbound_logs:
                    if entry.get('source') == 'email':
                        entry_date = datetime.fromisoformat(
                            entry.get('timestamp', '2000-01-01')
                        )
                        if week_start <= entry_date <= week_end:
                            email_stats['total_processed'] += 1
                            category = entry.get('data', {}).get('category', 'unknown')
                            email_stats['by_category'][category] += 1
            
            # Pull from skills audit
            if os.path.exists(SKILLS_AUDIT_FILE):
                with open(SKILLS_AUDIT_FILE, 'r', encoding='utf-8') as f:
                    skills_logs = json.load(f)
                
                for entry in skills_logs:
                    if entry.get('skill') == 'operations_skill':
                        action = entry.get('action', '')
                        if 'send_response' in action:
                            email_stats['responses_sent'] += 1
            
            # Get current unread count (from Gmail MCP if available)
            try:
                from MCP.gmail_mcp import GmailMCPServer
                gmail = GmailMCPServer()
                result = gmail.execute('read_unread', {'max_results': 1})
                email_stats['unread_current'] = result.get('data', {}).get('count', 0)
            except Exception as e:
                logger.debug(f"Could not get current unread count: {e}")
                email_stats['unread_current'] = 0
            
            self.data['email'] = {
                **email_stats,
                'by_category': dict(email_stats['by_category'])
            }
            
            logger.info(f"Pulled email stats: {email_stats['total_processed']} processed")
            
        except Exception as e:
            logger.error(f"Failed to pull email statistics: {e}")
            self.data['email'] = {
                'total_processed': 0,
                'unread_current': 0,
                'by_category': {},
                'responses_sent': 0
            }
    
    def _pull_whatsapp_activity(self, week_start: datetime, week_end: datetime):
        """Pull WhatsApp activity from inbound requests."""
        try:
            whatsapp_stats = {
                'total_messages': 0,
                'unique_contacts': set(),
                'by_category': defaultdict(int),
                'messages_sent': 0
            }
            
            # Pull from inbound requests
            if os.path.exists(INBOUND_FILE):
                with open(INBOUND_FILE, 'r', encoding='utf-8') as f:
                    inbound_logs = json.load(f)
                
                for entry in inbound_logs:
                    if entry.get('source') == 'whatsapp':
                        entry_date = datetime.fromisoformat(
                            entry.get('timestamp', '2000-01-01')
                        )
                        if week_start <= entry_date <= week_end:
                            whatsapp_stats['total_messages'] += 1
                            contact = entry.get('data', {}).get('from', 'unknown')
                            whatsapp_stats['unique_contacts'].add(contact)
                            category = entry.get('data', {}).get('category', 'unknown')
                            whatsapp_stats['by_category'][category] += 1
            
            # Count messages sent
            if os.path.exists(SKILLS_AUDIT_FILE):
                with open(SKILLS_AUDIT_FILE, 'r', encoding='utf-8') as f:
                    skills_logs = json.load(f)
                
                for entry in skills_logs:
                    if entry.get('skill') == 'operations_skill':
                        result = entry.get('result', {})
                        if 'send_message' in str(result):
                            whatsapp_stats['messages_sent'] += 1
            
            self.data['whatsapp'] = {
                'total_messages': whatsapp_stats['total_messages'],
                'unique_contacts': len(whatsapp_stats['unique_contacts']),
                'contacts_list': list(whatsapp_stats['unique_contacts'])[:10],
                'by_category': dict(whatsapp_stats['by_category']),
                'messages_sent': whatsapp_stats['messages_sent']
            }
            
            logger.info(f"Pulled WhatsApp stats: {whatsapp_stats['total_messages']} messages")
            
        except Exception as e:
            logger.error(f"Failed to pull WhatsApp activity: {e}")
            self.data['whatsapp'] = {
                'total_messages': 0,
                'unique_contacts': 0,
                'by_category': {},
                'messages_sent': 0
            }
    
    def _pull_task_statistics(self, week_start: datetime, week_end: datetime):
        """Pull task processing statistics from RALPH decisions."""
        try:
            task_stats = {
                'total_processed': 0,
                'completed': 0,
                'failed': 0,
                'multistep': 0,
                'retries': 0,
                'avg_duration': 0
            }
            
            durations = []
            
            if os.path.exists(RALPH_DECISIONS_FILE):
                with open(RALPH_DECISIONS_FILE, 'r', encoding='utf-8') as f:
                    decisions = json.load(f)
                
                for entry in decisions:
                    entry_date = datetime.fromisoformat(
                        entry.get('timestamp', '2000-01-01')
                    )
                    if week_start <= entry_date <= week_end:
                        task_stats['total_processed'] += 1
                        
                        decision_type = entry.get('decision_type', '')
                        status = entry.get('status', '')
                        
                        if decision_type == 'execution':
                            if status == 'success':
                                task_stats['completed'] += 1
                                if entry.get('duration'):
                                    durations.append(entry['duration'])
                            elif status == 'failed':
                                task_stats['failed'] += 1
                            
                            if entry.get('attempts', 1) > 1:
                                task_stats['retries'] += 1
                        
                        if decision_type == 'routing' and 'multistep' in str(entry):
                            task_stats['multistep'] += 1
            
            task_stats['avg_duration'] = (
                sum(durations) / len(durations) if durations else 0
            )
            
            # Also count Needs_Action files
            pending_count = 0
            if os.path.exists(NEEDS_ACTION_DIR):
                pending_count = len([
                    f for f in os.listdir(NEEDS_ACTION_DIR)
                    if f.endswith('.md')
                ])
            
            task_stats['pending_items'] = pending_count
            
            self.data['tasks'] = task_stats
            
            logger.info(f"Pulled task stats: {task_stats['total_processed']} processed")
            
        except Exception as e:
            logger.error(f"Failed to pull task statistics: {e}")
            self.data['tasks'] = {
                'total_processed': 0,
                'completed': 0,
                'failed': 0,
                'multistep': 0,
                'retries': 0,
                'avg_duration': 0,
                'pending_items': 0
            }
    
    def _analyze_issues(self):
        """Analyze data to identify operational issues."""
        issues = []
        
        # Email backlog
        email_unread = self.data['email'].get('unread_current', 0)
        if email_unread > 50:
            issues.append({
                'severity': 'HIGH',
                'area': 'Email Communications',
                'issue': f'High email backlog: {email_unread} unread emails',
                'impact': 'Delayed response times, potential missed opportunities'
            })
        elif email_unread > 20:
            issues.append({
                'severity': 'MEDIUM',
                'area': 'Email Communications',
                'issue': f'Moderate email backlog: {email_unread} unread emails',
                'impact': 'Response times may be affected'
            })
        
        # Task failures
        task_failures = self.data['tasks'].get('failed', 0)
        total_tasks = self.data['tasks'].get('total_processed', 1)
        failure_rate = (task_failures / total_tasks * 100) if total_tasks > 0 else 0
        
        if failure_rate > 20:
            issues.append({
                'severity': 'HIGH',
                'area': 'Task Processing',
                'issue': f'High task failure rate: {failure_rate:.1f}%',
                'impact': 'Automation reliability compromised'
            })
        
        # Low social media activity
        social_posts = self.data['social'].get('total_posts', 0)
        if social_posts < 3:
            issues.append({
                'severity': 'LOW',
                'area': 'Social Media',
                'issue': f'Low social media activity: {social_posts} posts this week',
                'impact': 'Reduced brand visibility and engagement opportunities'
            })
        
        # Pending items backlog
        pending = self.data['tasks'].get('pending_items', 0)
        if pending > 30:
            issues.append({
                'severity': 'MEDIUM',
                'area': 'Task Management',
                'issue': f'Large pending items backlog: {pending} items',
                'impact': 'Cognitive load, potential missed deadlines'
            })
        
        self.data['issues'] = issues
        logger.info(f"Identified {len(issues)} operational issues")
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on data."""
        recommendations = []
        
        # Email recommendations
        email_unread = self.data['email'].get('unread_current', 0)
        if email_unread > 20:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Email Management',
                'recommendation': 'Implement auto-responders for common inquiries',
                'expected_impact': 'Reduce response time by 50%, improve customer satisfaction',
                'effort': 'Low'
            })
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Email Management',
                'recommendation': 'Set up email filtering rules for automatic categorization',
                'expected_impact': 'Reduce manual sorting time by 70%',
                'effort': 'Medium'
            })
        
        # Social media recommendations
        social_posts = self.data['social'].get('total_posts', 0)
        if social_posts < 5:
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Social Media',
                'recommendation': 'Increase posting frequency to 3-5 times per week',
                'expected_impact': 'Improved brand visibility and engagement',
                'effort': 'Low'
            })
        
        # Task processing recommendations
        task_failures = self.data['tasks'].get('failed', 0)
        if task_failures > 0:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Automation',
                'recommendation': 'Review and fix failed task patterns',
                'expected_impact': 'Improve automation reliability',
                'effort': 'Medium'
            })
        
        # WhatsApp recommendations
        whatsapp_messages = self.data['whatsapp'].get('total_messages', 0)
        if whatsapp_messages > 10:
            recommendations.append({
                'priority': 'LOW',
                'area': 'WhatsApp Communications',
                'recommendation': 'Create template responses for common inquiries',
                'expected_impact': 'Faster response times for WhatsApp messages',
                'effort': 'Low'
            })
        
        self.data['recommendations'] = recommendations
        logger.info(f"Generated {len(recommendations)} recommendations")
    
    def _compile_report(self, week_start: datetime, week_end: datetime) -> Dict:
        """Compile all data into report format."""
        return {
            'report_date': self.report_date.isoformat(),
            'period': {
                'start': week_start.isoformat(),
                'end': week_end.isoformat(),
                'week_number': week_start.isocalendar()[1]
            },
            'executive_summary': self._generate_executive_summary(),
            'social_media': self.data['social'],
            'email_communications': self.data['email'],
            'whatsapp_activity': self.data['whatsapp'],
            'task_processing': self.data['tasks'],
            'operational_issues': self.data['issues'],
            'recommendations': self.data['recommendations'],
            'key_metrics': self._calculate_key_metrics()
        }
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary paragraph."""
        social_posts = self.data['social'].get('total_posts', 0)
        emails_processed = self.data['email'].get('total_processed', 0)
        whatsapp_msgs = self.data['whatsapp'].get('total_messages', 0)
        tasks_completed = self.data['tasks'].get('completed', 0)
        
        summary = f"This week, the AI Employee system processed {tasks_completed} tasks "
        summary += f"across multiple channels. "
        summary += f"Social media activity included {social_posts} posts "
        
        if social_posts > 5:
            summary += "with strong consistency. "
        elif social_posts > 0:
            summary += "with room for increased frequency. "
        else:
            summary += "though no posts were published. "
        
        summary += f"Email communications totaled {emails_processed} messages, "
        summary += f"and WhatsApp handled {whatsapp_msgs} inbound messages. "
        
        if self.data['issues']:
            summary += f"Key attention areas: {len(self.data['issues'])} operational issues identified."
        
        return summary
    
    def _calculate_key_metrics(self) -> Dict:
        """Calculate key performance metrics."""
        tasks = self.data['tasks']
        total = tasks.get('total_processed', 0)
        completed = tasks.get('completed', 0)
        
        return {
            'task_success_rate': f"{(completed/total*100) if total > 0 else 0:.1f}%",
            'social_posts': self.data['social'].get('total_posts', 0),
            'emails_processed': self.data['email'].get('total_processed', 0),
            'whatsapp_messages': self.data['whatsapp'].get('total_messages', 0),
            'avg_task_duration': f"{tasks.get('avg_duration', 0):.2f}s",
            'issues_identified': len(self.data['issues']),
            'recommendations': len(self.data['recommendations'])
        }
    
    def _save_weekly_report(self, report: Dict):
        """Save full weekly report as markdown."""
        md = self._convert_to_markdown(report, full_report=True)
        
        with open(WEEKLY_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info(f"Weekly report saved: {WEEKLY_REPORT_FILE}")
    
    def _save_ceo_briefing(self, report: Dict):
        """Save condensed CEO briefing."""
        md = self._convert_to_markdown(report, full_report=False)
        
        with open(CEO_BRIEFING_FILE, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info(f"CEO briefing saved: {CEO_BRIEFING_FILE}")
    
    def _convert_to_markdown(self, report: Dict, full_report: bool = True) -> str:
        """Convert report to markdown format."""
        period = report.get('period', {})
        metrics = report.get('key_metrics', {})
        social = report.get('social_media', {})
        email = report.get('email_communications', {})
        whatsapp = report.get('whatsapp_activity', {})
        tasks = report.get('task_processing', {})
        issues = report.get('operational_issues', [])
        recommendations = report.get('recommendations', [])
        
        md = f"""# Weekly Audit Report

**Generated:** {report.get('report_date', 'N/A')[:19]}
**Period:** Week {period.get('week_number', 'N/A')} ({period.get('start', 'N/A')[:10]} to {period.get('end', 'N/A')[:10]})

---

## Executive Summary

{report.get('executive_summary', 'No summary available.')}

---

## Key Metrics at a Glance

| Metric | Value |
|--------|-------|
| Task Success Rate | {metrics.get('task_success_rate', 'N/A')} |
| Social Media Posts | {metrics.get('social_posts', 0)} |
| Emails Processed | {metrics.get('emails_processed', 0)} |
| WhatsApp Messages | {metrics.get('whatsapp_messages', 0)} |
| Avg Task Duration | {metrics.get('avg_task_duration', 'N/A')} |
| Issues Identified | {metrics.get('issues_identified', 0)} |

---

## Social Media Performance

### Overview
- **Total Posts:** {social.get('total_posts', 0)}
- **Platforms Active:** {social.get('platforms_active', 0)}

### Posts by Platform
| Platform | Posts |
|----------|-------|
"""
        
        for platform, count in social.get('by_platform', {}).items():
            md += f"| {platform.title()} | {count} |\n"
        
        if not social.get('by_platform'):
            md += "| No activity this week | - |\n"
        
        md += "\n### Recent Posts\n"
        
        if full_report and social.get('posts'):
            md += "| Date | Platform | Content |\n"
            md += "|------|----------|--------|\n"
            for post in social.get('posts', [])[:10]:
                result = post.get('result', {}).get('data', {})
                content = result.get('content', 'N/A')[:50]
                md += f"| {post.get('timestamp', 'N/A')[:10]} | {post.get('platform', 'N/A').title()} | {content}... |\n"
        else:
            md += f"*{social.get('total_posts', 0)} posts made this week. See full report for details.*\n"
        
        md += f"""
---

## Email Communications

### Statistics
- **Total Processed:** {email.get('total_processed', 0)}
- **Current Unread:** {email.get('unread_current', 0)}
- **Responses Sent:** {email.get('responses_sent', 0)}

### By Category
| Category | Count |
|----------|-------|
"""
        
        for category, count in email.get('by_category', {}).items():
            md += f"| {category.title()} | {count} |\n"
        
        if not email.get('by_category'):
            md += "| No categorized emails | - |\n"
        
        md += f"""
---

## WhatsApp Activity

### Statistics
- **Total Messages:** {whatsapp.get('total_messages', 0)}
- **Unique Contacts:** {whatsapp.get('unique_contacts', 0)}
- **Messages Sent:** {whatsapp.get('messages_sent', 0)}

### By Category
| Category | Count |
|----------|-------|
"""
        
        for category, count in whatsapp.get('by_category', {}).items():
            md += f"| {category.title()} | {count} |\n"
        
        if not whatsapp.get('by_category'):
            md += "| No categorized messages | - |\n"
        
        if whatsapp.get('contacts_list'):
            md += f"\n**Top Contacts:** {', '.join(whatsapp.get('contacts_list', [])[:5])}\n"
        
        md += f"""
---

## Task Processing

### Overview
- **Total Processed:** {tasks.get('total_processed', 0)}
- **Completed:** {tasks.get('completed', 0)}
- **Failed:** {tasks.get('failed', 0)}
- **Multi-step Tasks:** {tasks.get('multistep', 0)}
- **Retries Required:** {tasks.get('retries', 0)}
- **Pending Items:** {tasks.get('pending_items', 0)}
- **Average Duration:** {tasks.get('avg_duration', 0):.2f} seconds

---

## Operational Issues

"""
        
        if issues:
            for issue in issues:
                md += f"""### [{issue.get('severity', 'MEDIUM')}] {issue.get('area', 'General')}

**Issue:** {issue.get('issue', 'N/A')}

**Impact:** {issue.get('impact', 'N/A')}

"""
        else:
            md += "*No critical operational issues identified this week.*\n\n"
        
        md += """---

## Recommendations

"""
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                md += f"""### {i}. [{rec.get('priority', 'MEDIUM')}] {rec.get('area', 'General')}

**Recommendation:** {rec.get('recommendation', 'N/A')}

**Expected Impact:** {rec.get('expected_impact', 'N/A')}

**Effort:** {rec.get('effort', 'N/A')}

"""
        else:
            md += "*No specific recommendations at this time.*\n\n"
        
        md += """---

## Inbound Leads Summary

This week's inbound communications represent potential business opportunities:

"""
        
        # Calculate leads
        inquiry_count = (
            email.get('by_category', {}).get('inquiry', 0) +
            whatsapp.get('by_category', {}).get('inquiry', 0) +
            email.get('by_category', {}).get('sales', 0) +
            whatsapp.get('by_category', {}).get('sales', 0)
        )
        
        md += f"- **Total Inquiries:** {inquiry_count}\n"
        md += f"- **Email Inquiries:** {email.get('by_category', {}).get('inquiry', 0)}\n"
        md += f"- **WhatsApp Inquiries:** {whatsapp.get('by_category', {}).get('inquiry', 0)}\n"
        
        md += """
---

## Next Week Priorities

Based on this week's performance, recommended focus areas:

1. """
        
        if recommendations:
            md += recommendations[0].get('recommendation', 'Continue current operations')
        else:
            md += "Maintain current operational excellence"
        
        md += f"""
2. Address {len(issues)} identified operational issue(s)
3. """
        
        if social.get('total_posts', 0) < 5:
            md += "Increase social media posting frequency"
        else:
            md += "Continue strong social media presence"
        
        md += """

---

*Generated by AI Employee Vault - Weekly Audit Engine*
*Report Classification: Internal Executive Use*
"""
        
        return md


# Convenience function
def generate_weekly_audit(week_start: datetime = None, 
                          week_end: datetime = None) -> Dict:
    """Generate weekly audit report."""
    engine = WeeklyAuditEngine()
    return engine.generate_report(week_start, week_end)


# Main entry point
if __name__ == '__main__':
    print("=" * 60)
    print("Weekly Audit Engine - Gold Tier")
    print("=" * 60)
    print()
    
    # Generate report
    engine = WeeklyAuditEngine()
    report = engine.generate_report()
    
    print("\n[OK] Weekly audit complete!")
    print(f"\nReports generated:")
    print(f"  - Full Report: {WEEKLY_REPORT_FILE}")
    print(f"  - CEO Briefing: {CEO_BRIEFING_FILE}")
    
    print("\n" + "=" * 60)
    print("Key Metrics")
    print("=" * 60)
    
    metrics = report.get('key_metrics', {})
    for key, value in metrics.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 60)
