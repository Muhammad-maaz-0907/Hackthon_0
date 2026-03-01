# AI Employee Vault - Gold Tier Architecture

**Version:** Gold Tier v1.0  
**Last Updated:** February 25, 2026  
**Author:** AI Employee Project

---

## Table of Contents

1. [System Overview](#system-overview)
2. [System Diagram](#system-diagram)
3. [Architecture Layers](#architecture-layers)
4. [Cross-Domain Integration](#cross-domain-integration)
5. [MCP Servers](#mcp-servers)
6. [Agent Skills](#agent-skills)
7. [RALPH Wiggum Loop](#ralph-wiggum-loop)
8. [Weekly Audit & CEO Briefing](#weekly-audit--ceo-briefing)
9. [Error Recovery](#error-recovery)
10. [Logging & Audit](#logging--audit)
11. [Step-by-Step Runtime Flow](#step-by-step-runtime-flow)
12. [Real-World Deployment Notes](#real-world-deployment-notes)

---

## System Overview

The **AI Employee Vault Gold Tier** is an autonomous AI agent system that monitors multiple communication channels, processes tasks intelligently, and executes actions across domains. It builds upon the Silver Tier foundation with cross-domain automation, MCP (Model Context Protocol) servers, agent skills abstraction, and comprehensive audit capabilities.

### Key Capabilities

- **24/7 Monitoring** - Gmail, WhatsApp, Instagram watchers
- **Intelligent Task Routing** - Automatic skill selection via TaskRouter
- **Multi-Step Execution** - RALPH Loop with retries and backoff
- **Cross-Domain Actions** - Personal triggers → Business actions
- **Human-in-the-Loop** - Approval workflow for critical actions
- **Executive Reporting** - Automated CEO briefings

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AI EMPLOYEE VAULT - GOLD TIER                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    PERCEPTION LAYER (Watchers)                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │   │
│  │  │  Gmail   │  │ WhatsApp │  │ LinkedIn │  │Instagram │                 │   │
│  │  │ Watcher  │  │ Watcher  │  │Scheduler │  │ Watcher  │                 │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘                 │   │
│  └───────┼─────────────┼─────────────┼─────────────┼────────────────────────┘   │
│          │             │             │             │                              │
│          └─────────────┴──────┬──────┴─────────────┘                              │
│                               │                                                    │
│                               ▼                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    MEMORY LAYER (File-Based Queue)                        │   │
│  │                          Needs_Action/                                    │   │
│  │                    (Markdown Task Files)                                  │   │
│  └──────────────────────────────┬───────────────────────────────────────────┘   │
│                                 │                                                │
│                                 ▼                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    REASONING LAYER (Core Engine)                          │   │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │   │
│  │  │  RALPH LOOP (Recursive Autonomous Learning & Processing Handler)   │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │  │   │
│  │  │  │ TaskRouter   │  │ SkillRegistry│  │ DecisionLog  │             │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘             │  │   │
│  │  └────────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────┬───────────────────────────────────────────┘   │
│                                 │                                                │
│                                 ▼                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    ACTION LAYER (MCP Servers)                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │  Gmail   │  │ LinkedIn │  │ Twitter  │  │ Facebook │  │Instagram │  │   │
│  │  │   MCP    │  │   MCP    │  │   MCP    │  │   MCP    │  │   MCP    │  │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │   │
│  │       │             │             │             │             │          │   │
│  │  ┌────┴─────────────┴─────────────┴─────────────┴─────────────┴──────┐  │   │
│  │  │                    MCPServerBase (Inheritance)                     │  │   │
│  │  │              connect() | execute() | retry_logic()                │  │   │
│  │  └────────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────┬───────────────────────────────────────────┘   │
│                                 │                                                │
│                                 ▼                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    AUDIT & LOGGING LAYER                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │   │
│  │  │ Weekly Audit │  │ CEO Briefing │  │ Error Handler│                   │   │
│  │  │   Engine     │  │  Generator   │  │  (Retry/     │                   │   │
│  │  │              │  │              │  │   Backoff)   │                   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                   │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │              Logs/ (JSON Audit Trail)                             │   │   │
│  │  │  mcp_audit.json | skills_audit.json | ralph_decisions.json       │   │   │
│  │  │  errors.json | social.json | whatsapp_replies.json                │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    APPROVAL WORKFLOW (Human-in-the-Loop)                  │   │
│  │          Needs_Action → Pending_Approval → Approved → Done/              │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Layers

### 1. Perception Layer (Watchers)

**Purpose:** Monitor external communication channels for incoming messages and events.

| Component | File | Poll Interval | Output |
|-----------|------|---------------|--------|
| Gmail Watcher | `Integrations/Gmail/gmail_watcher.py` | 120s | `Needs_Action/email_*.md` |
| WhatsApp Watcher | `Integrations/WhatsApp/whatsapp_watcher.py` | 5s | `Needs_Action/whatsapp_*.md` |
| Instagram Watcher | `Integrations/Instagram/instagram_watcher.py` | 15s | `Needs_Action/instagram_*.md` |
| LinkedIn Scheduler | `Integrations/LinkedIn/linkedin_scheduler.py` | Scheduled | Posts to LinkedIn |

**Key Features:**
- Persistent browser sessions (Playwright)
- Keyword-based filtering
- Unread message detection
- Session persistence across restarts

### 2. Memory Layer (File-Based Queue)

**Purpose:** Decouple perception from action using file-based message queue.

```
Needs_Action/
├── email_20260225_143022.md      # Incoming email task
├── whatsapp_20260225_143530.md   # WhatsApp message task
├── instagram_dm_20260225_150000.md # Instagram DM task
└── instagram_comment_20260225_150500.md # Instagram comment task
```

**Markdown Task Format:**
```markdown
---
type: whatsapp
from: John Doe
time: 2026-02-25T14:35:30
keywords: urgent, help
---
Message: Hi, I need urgent help with pricing information
```

**Queue States:**
```
Needs_Action/ → Pending_Approval/ → Approved/ → Done/
                      ↑
                  (Human Review)
```

### 3. Reasoning Layer (Core Engine)

**Purpose:** Route tasks to appropriate skills, manage execution, handle retries.

**Components:**
- **RALPH Loop** - Main orchestration loop
- **TaskRouter** - Keyword-based skill routing
- **SkillRegistry** - Available skills catalog
- **DecisionLogger** - Audit trail for decisions

### 4. Action Layer (MCP Servers)

**Purpose:** Execute actions on external platforms via standardized protocol.

**MCP Servers:**
- Gmail MCP, LinkedIn MCP, Twitter MCP, Facebook MCP, Instagram MCP, WhatsApp MCP

### 5. Audit & Logging Layer

**Purpose:** Comprehensive logging, weekly reports, executive briefings.

---

## Cross-Domain Integration

### Personal → Business Triggers

The Gold Tier enables **cross-domain automation** where personal communications trigger business actions.

### Example Flow

```
1. PERSONAL: Email arrives from client
   ↓
2. PERCEPTION: Gmail Watcher detects email
   ↓
3. MEMORY: Creates Needs_Action/email_client_inquiry.md
   ↓
4. REASONING: RALPH Loop processes task
   ↓
5. ROUTING: TaskRouter identifies "pricing inquiry"
   ↓
6. SKILL: social_post_skill selected
   ↓
7. ACTION: LinkedIn MCP creates post about pricing
   ↓
8. AUDIT: Logged to Logs/mcp_audit.json
   ↓
9. MEMORY: Moved to Done/
```

### Implementation

**Task Metadata (in .md file):**
```markdown
---
type: email
from: client@company.com
subject: Pricing Inquiry
triggers: business_action
required_action: social_post
platform: linkedin
---
Client is asking about enterprise pricing tiers.
```

**Cross-Domain Router:**
```python
# Core/task_router.py
def route_task(task_metadata):
    if task_metadata.get('triggers') == 'business_action':
        if task_metadata.get('required_action') == 'social_post':
            return 'social_post_skill', {
                'platform': task_metadata.get('platform'),
                'content': generate_content(task_metadata)
            }
```

---

## MCP Servers

### Overview

**Model Context Protocol (MCP)** provides a standardized interface for AI agents to interact with external systems.

### Base Class: `MCPServerBase`

**File:** `MCP/mcp_server_base.py`

```python
class MCPServerBase(ABC):
    """Base class for all MCP servers."""

    def __init__(self, server_name: str, max_retries: int = 3, retry_delay: float = 1.0):
        self.server_name = server_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connected = False
        self.audit_logger = MCPAuditLogger()

    @abstractmethod
    def connect(self, **kwargs) -> Dict:
        """Connect to external service."""
        pass

    @abstractmethod
    def _execute_action(self, action: str, payload: Dict) -> Dict:
        """Execute specific action."""
        pass

    def execute(self, action: str, payload: Dict) -> Dict:
        """Execute action with retry logic."""
        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._execute_action(action, payload)
                self.audit_logger.log(
                    server_name=self.server_name,
                    action=action,
                    status='success',
                    payload=payload,
                    result=result
                )
                return result
            except Exception as e:
                if attempt == self.max_retries:
                    self.audit_logger.log(
                        server_name=self.server_name,
                        action=action,
                        status='error',
                        payload=payload,
                        error=str(e)
                    )
                    return self.handle_error(e, action)
                time.sleep(self.retry_delay * attempt)  # Exponential backoff

    def handle_error(self, error: Exception, action: str) -> Dict:
        """Handle error gracefully."""
        return MCPResponse.error(str(error), action)
```

### Standardized Response Format

```python
class MCPResponse:
    @staticmethod
    def success(data: Dict[str, Any], action: str = None) -> Dict:
        return {
            "status": "success",
            "data": data,
            "error": None,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def error(message: str, action: str = None, details: Dict = None) -> Dict:
        return {
            "status": "error",
            "data": None,
            "error": message,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
```

### MCP Server Catalog

#### 1. Gmail MCP Server

**File:** `MCP/gmail_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `send_email` | `{to, subject, body, cc?, bcc?}` | Send email |
| `read_unread` | `{max_results: 10}` | Get unread emails |
| `search_email` | `{query: string}` | Search emails |

**Example:**
```python
from MCP.gmail_mcp import GmailMCPServer

server = GmailMCPServer()
server.connect()

result = server.execute('send_email', {
    'to': 'client@example.com',
    'subject': 'Re: Pricing Inquiry',
    'body': 'Thank you for your interest...'
})
```

#### 2. LinkedIn MCP Server

**File:** `MCP/linkedin_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{content: string}` | Create LinkedIn post |
| `get_profile_stats` | `{}` | Get profile statistics |
| `schedule_post` | `{content, scheduled_time}` | Schedule future post |

#### 3. Twitter/X MCP Server

**File:** `MCP/twitter_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{content: string (max 280 chars)}` | Post tweet |
| `get_metrics` | `{tweet_id}` | Get tweet metrics |
| `reply` | `{tweet_id, content}` | Reply to tweet |

#### 4. Facebook MCP Server

**File:** `MCP/facebook_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{content: string, image_path?: string}` | Post to Facebook |
| `get_page_metrics` | `{page_id}` | Get page insights |
| `reply_to_comment` | `{comment_id, content}` | Reply to comment |

#### 5. Instagram MCP Server

**File:** `MCP/instagram_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{caption, image_url, is_video?, video_url?}` | Create Instagram post |
| `get_metrics` | `{media_id?, metric_type?}` | Get post/profile metrics |

**Note:** Requires Instagram Business Account + Facebook Page connection.

#### 6. WhatsApp MCP Server

**File:** `MCP/whatsapp_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `send_message` | `{phone_number, message}` | Send WhatsApp message |
| `get_contacts` | `{}` | Get contact list |
| `broadcast` | `{contacts[], message}` | Broadcast to multiple contacts |

**Note:** Uses WhatsApp Web automation (Playwright).

---

## Agent Skills

### Overview

**Agent Skills** are reusable, domain-specific capabilities that the RALPH Loop can invoke.

### Base Class: `AgentSkill`

**File:** `Skills/agent_skill_base.py`

```python
class AgentSkill(ABC):
    """Base class for all agent skills."""

    def __init__(self, name: str, tier: str = "gold"):
        self.name = name
        self.tier = tier
        self.audit_logger = AuditLogger()

    @abstractmethod
    def execute(self, **context) -> Dict:
        """Execute the skill with given context."""
        pass

    @abstractmethod
    def validate(self, **context) -> bool:
        """Validate input context."""
        pass

    def _log_execution(self, action: str, status: str, context: Dict,
                       result: Dict = None, error: str = None):
        """Log skill execution to audit trail."""
        self.audit_logger.log(
            skill_name=self.name,
            action=action,
            status=status,
            context=context,
            result=result,
            error=error
        )
```

### Skill Registry

**File:** `Skills/skill_registry.py`

```python
class SkillRegistry:
    """Central registry for all agent skills."""

    def __init__(self):
        self.skills = {}
        self._register_default_skills()

    def _register_default_skills(self):
        """Register built-in skills."""
        from Skills.social_post_skill import SocialPostSkill
        from Skills.audit_skill import AuditSkill
        from Skills.email_response_skill import EmailResponseSkill

        self.register(SocialPostSkill())
        self.register(AuditSkill())
        self.register(EmailResponseSkill())

    def register(self, skill: AgentSkill):
        """Register a skill."""
        self.skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name}")

    def get(self, skill_name: str) -> Optional[AgentSkill]:
        """Get skill by name."""
        return self.skills.get(skill_name)

    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return list(self.skills.keys())
```

### Example Skills

#### 1. Social Post Skill

**File:** `Skills/social_post_skill.py`

```python
class SocialPostSkill(AgentSkill):
    """Skill for posting to social media platforms."""

    def __init__(self):
        super().__init__("social_post_skill", tier="gold")

    def execute(self, **context) -> Dict:
        platform = context.get('platform')
        content = context.get('content')
        image_path = context.get('image_path')

        # Validate
        if not self.validate(**context):
            return AgentSkill.error("Invalid context", self.name)

        # Route to appropriate MCP
        if platform == 'facebook':
            from MCP.facebook_mcp import FacebookMCPServer
            mcp = FacebookMCPServer()
            mcp.connect()
            result = mcp.execute('create_post', {
                'content': content,
                'image_path': image_path
            })
        elif platform == 'instagram':
            from MCP.instagram_mcp import InstagramMCPServer
            mcp = InstagramMCPServer()
            mcp.connect()
            result = mcp.execute('create_post', {
                'caption': content,
                'image_url': image_path
            })
        # ... other platforms

        self._log_execution('post', result['status'], context, result)
        return result

    def validate(self, **context) -> bool:
        required = ['platform', 'content']
        return all(k in context for k in required)
```

#### 2. Audit Skill

**File:** `Skills/audit_skill.py`

```python
class AuditSkill(AgentSkill):
    """Skill for generating audits and reports."""

    def __init__(self):
        super().__init__("audit_skill", tier="gold")

    def execute(self, **context) -> Dict:
        period = context.get('period', 'weekly')
        include_recommendations = context.get('include_recommendations', True)

        from Audit.weekly_report import WeeklyAuditEngine
        engine = WeeklyAuditEngine()
        report = engine.generate_report()

        self._log_execution('generate_audit', 'success', context, report)
        return AgentSkill.success({
            'report': report,
            'file': WEEKLY_REPORT_FILE
        }, self.name)

    def validate(self, **context) -> bool:
        return True  # Always valid
```

#### 3. RALPH Loop Skill

**File:** `Skills/ralph_loop_skill.py`

```python
class RalphLoopSkill(AgentSkill):
    """Skill for multi-step task execution via RALPH Loop."""

    def __init__(self):
        super().__init__("ralph_loop_skill", tier="gold")

    def execute(self, **context) -> Dict:
        task_description = context.get('task_description')
        max_iterations = context.get('max_iterations', 10)

        from Core.ralph_loop import RALPHLoop
        loop = RALPHLoop()

        result = loop.run_until_complete(
            task_description=task_description,
            max_iterations=max_iterations
        )

        return AgentSkill.success(result, self.name)

    def validate(self, **context) -> bool:
        return 'task_description' in context
```

---

## RALPH Wiggum Loop

### Overview

**RALPH** (Recursive Autonomous Learning & Processing Handler) is the main orchestration loop that iterates until tasks are complete.

**File:** `Core/ralph_loop.py`

### Architecture

```python
class RALPHLoop:
    """Autonomous decision engine."""

    def __init__(self):
        self.skill_registry = SkillRegistry()
        self.task_router = TaskRouter()
        self.decision_logger = DecisionLogger()
        self.state_store = StateStore()

    def run_until_complete(self, task_description: str,
                           max_iterations: int = 10) -> Dict:
        """
        Run loop until task is complete or max iterations reached.

        Args:
            task_description: Natural language task description
            max_iterations: Maximum loop iterations

        Returns:
            Dict: Task result
        """
        iteration = 0
        state = {
            'task': task_description,
            'status': 'in_progress',
            'steps_completed': [],
            'current_step': None
        }

        while iteration < max_iterations:
            iteration += 1

            # 1. Analyze current state
            analysis = self._analyze_state(state)

            # 2. Decide next action
            decision = self._make_decision(analysis, state)

            # 3. Route to appropriate skill
            skill_name = decision.get('skill')
            action = decision.get('action')
            skill = self.skill_registry.get(skill_name)

            if not skill:
                state['status'] = 'failed'
                state['error'] = f'Skill not found: {skill_name}'
                break

            # 4. Execute skill with retry
            result = self._execute_with_retry(skill, action, decision.get('context', {}))

            # 5. Update state
            state['steps_completed'].append({
                'iteration': iteration,
                'skill': skill_name,
                'action': action,
                'result': result
            })

            # 6. Check completion
            if self._is_task_complete(state, task_description):
                state['status'] = 'completed'
                break

            # 7. Log decision
            self.decision_logger.log_decision(
                task_id=task_description[:50],
                decision=decision
            )

        return state

    def _execute_with_retry(self, skill: AgentSkill, action: str,
                            context: Dict, max_retries: int = 3) -> Dict:
        """Execute skill with exponential backoff."""
        for attempt in range(1, max_retries + 1):
            try:
                result = skill.execute(**context)
                if result.get('status') == 'success':
                    return result
                raise Exception(result.get('error', 'Unknown error'))
            except Exception as e:
                if attempt == max_retries:
                    return AgentSkill.error(str(e), skill.name)
                time.sleep(2 ** attempt)  # Exponential backoff
```

### Completion Conditions

Task is complete when:
1. **File moved** - Task file moved to `Done/` folder
2. **Token present** - Completion token in state store
3. **Natural language** - Skill reports "task complete" in result

### Example: Multi-Step Task

**Task:** "Post about our new product on all social media platforms"

```
Iteration 1:
  - Skill: social_post_skill
  - Action: create_post
  - Platform: facebook
  - Result: Success

Iteration 2:
  - Skill: social_post_skill
  - Action: create_post
  - Platform: instagram
  - Result: Success

Iteration 3:
  - Skill: social_post_skill
  - Action: create_post
  - Platform: twitter
  - Result: Success

Iteration 4:
  - Analysis: All platforms posted
  - Status: completed
  - Loop exits
```

---

## Weekly Audit & CEO Briefing

### Overview

Automated executive reporting system that generates comprehensive weekly reports and condensed CEO briefings.

### Trigger

**Manual:**
```python
from Skills.audit_skill import AuditSkill

skill = AuditSkill()
result = skill.execute(period='weekly')
```

**Scheduled (Weekly):**
```bash
# Cron job or Windows Task Scheduler
# Runs every Sunday at 6 PM
0 18 * * 0 cd AI_Employee && python Audit\weekly_report.py
```

### Generation Process

**File:** `Audit/weekly_report.py`

```python
class WeeklyAuditEngine:
    """Generates weekly executive reports."""

    def generate_report(self, week_start: datetime, week_end: datetime) -> Dict:
        # 1. Pull social media metrics
        self._pull_social_metrics(week_start, week_end)

        # 2. Pull email statistics
        self._pull_email_statistics(week_start, week_end)

        # 3. Pull WhatsApp activity
        self._pull_whatsapp_activity(week_start, week_end)

        # 4. Pull task statistics
        self._pull_task_statistics(week_start, week_end)

        # 5. Analyze issues and bottlenecks
        self._analyze_issues()

        # 6. Generate recommendations
        self._generate_recommendations()

        # 7. Compile report
        report = self._compile_report(week_start, week_end)

        # 8. Save reports
        self._save_weekly_report(report)      # Full report
        self._save_ceo_briefing(report)       # Condensed version

        return report
```

### Data Sources

| Source | File | Data Extracted |
|--------|------|----------------|
| Social Metrics | `Data/weekly_metrics.json` | Posts, engagement, followers |
| Skills Audit | `Logs/skills_audit.json` | Skill executions, success rates |
| RALPH Decisions | `Logs/ralph_decisions.json` | Task routing decisions |
| Gmail Stats | Gmail API | Emails sent/received |
| WhatsApp Logs | `Logs/whatsapp_replies.json` | Messages sent/received |

### Output: CEO Briefing Template

**File:** `Audits/CEO_Briefing.md`

```markdown
# CEO Briefing Report

**Generated:** 2026-02-25
**Period:** February 18-25, 2026

## Executive Summary
- Total Tasks: 45
- Completed: 38 (84% success rate)
- Pending: 7
- Failed: 0

## Social Media Performance
| Platform  | Posts | Engagement | Followers |
|-----------|-------|------------|-----------|
| Facebook  | 5     | 234 likes  | +12       |
| Instagram | 3     | 156 likes  | +8        |
| Twitter   | 7     | 89 likes   | +5        |
| LinkedIn  | 4     | 312 likes  | +15       |

## Email Communications
- Emails Sent: 23
- Emails Received: 67
- Response Time (avg): 2.3 hours

## WhatsApp Activity
- Messages Received: 89
- Auto-Replies Sent: 45
- Manual Responses: 12

## Bottlenecks
1. 3 tasks awaiting approval in Pending_Approval/
2. Instagram API rate limit reached (2 times)

## Recommendations
1. Review pending approvals daily
2. Consider upgrading Instagram API tier
3. Schedule more LinkedIn content (high engagement)

---
*Generated by AI Employee Vault - Weekly Audit Engine*
```

---

## Error Recovery

### Multi-Level Error Handling

#### Level 1: Skill-Level Retry

```python
class AgentSkill(ABC):
    def execute_with_retry(self, **context) -> Dict:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                return self.execute(**context)
            except Exception as e:
                if attempt == max_retries:
                    return AgentSkill.error(str(e), self.name)
                time.sleep(2 ** attempt)  # Exponential backoff
```

#### Level 2: MCP-Level Retry

```python
class MCPServerBase(ABC):
    def execute(self, action: str, payload: Dict) -> Dict:
        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._execute_action(action, payload)
                return result
            except Exception as e:
                if attempt == self.max_retries:
                    return self.handle_error(e, action)
                time.sleep(self.retry_delay * attempt)
```

#### Level 3: RALPH-Level Graceful Degradation

```python
class RALPHLoop:
    def _execute_with_fallback(self, skill_name: str, context: Dict) -> Dict:
        try:
            skill = self.skill_registry.get(skill_name)
            return skill.execute(**context)
        except Exception as e:
            # Fallback: Queue task for later
            self._queue_for_later(context, error=str(e))
            return AgentSkill.error(f"Queued for later: {e}", skill_name)

    def _queue_for_later(self, context: Dict, error: str):
        """Queue task when API is down."""
        queue_file = os.path.join(DATA_DIR, 'retry_queue.json')
        queue = []
        if os.path.exists(queue_file):
            with open(queue_file, 'r') as f:
                queue = json.load(f)

        queue.append({
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'error': error,
            'retry_after': datetime.now() + timedelta(hours=1)
        })

        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
```

### Error Categories

```python
class ErrorCategory(Enum):
    NETWORK = "network"           # Connection errors
    AUTHENTICATION = "auth"       # Token/permission errors
    VALIDATION = "validation"     # Invalid input
    RATE_LIMIT = "rate_limit"     # API rate limit
    RESOURCE = "resource"         # Memory/disk issues
    TIMEOUT = "timeout"           # Request timeout
    INTERNAL = "internal"         # Internal errors
```

### Recovery Strategies

| Error Category | Strategy |
|----------------|----------|
| Network | Retry with exponential backoff (max 3 attempts) |
| Authentication | Alert user, pause task, queue for manual review |
| Rate Limit | Wait and retry after cooldown period |
| Timeout | Retry with longer timeout |
| Validation | Log error, move task to Archive/ |
| Resource | Graceful shutdown, save state |

---

## Logging & Audit

### Comprehensive JSON Logging

All operations are logged to `Logs/` directory in JSON format.

### Log Files

| File | Purpose | Retention |
|------|---------|-----------|
| `mcp_audit.json` | All MCP server operations | Last 500 entries |
| `skills_audit.json` | All skill executions | Last 500 entries |
| `ralph_decisions.json` | RALPH routing decisions | Last 500 entries |
| `ralph_task_history.json` | Task execution history | Last 1000 entries |
| `errors.json` | All errors with stack traces | Last 500 entries |
| `social.json` | Social media posts | Last 1000 entries |
| `whatsapp_replies.json` | WhatsApp auto-replies | Last 500 entries |
| `instagram.json` | Instagram activity | Last 500 entries |

### Log Entry Format

```json
{
  "timestamp": "2026-02-25T14:30:22.123456",
  "server": "instagram_mcp",
  "action": "create_post",
  "status": "success",
  "payload": {
    "caption": "New product launch! 🚀",
    "image_url": "https://example.com/image.jpg"
  },
  "result": {
    "status": "success",
    "data": {
      "media_id": "ig_20260225143022",
      "simulated": true
    }
  },
  "error": null
}
```

### Audit Logger Implementation

```python
class MCPAuditLogger:
    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(LOGS_DIR, 'mcp_audit.json')
        self._ensure_log_file()

    def log(self, server_name: str, action: str, status: str,
            payload: Dict = None, result: Dict = None, error: str = None):
        """Log an MCP operation."""
        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

        entry = {
            'timestamp': datetime.now().isoformat(),
            'server': server_name,
            'action': action,
            'status': status,
            'payload': payload,
            'result': result,
            'error': error
        }
        logs.append(entry)

        # Keep only last 500 entries
        logs = logs[-500:]

        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, default=str)
```

---

## Step-by-Step Runtime Flow

### Complete End-to-End Example

**Scenario:** Client emails asking about pricing → Auto-post to social media

---

### Step 1: Watchers Detect Input

```
Time: 9:00 AM
Gmail Watcher polling Gmail API (every 120 seconds)
```

**Code:** `Integrations/Gmail/gmail_watcher.py`
```python
def check_emails():
    results = service.users().messages().list(
        userId='me',
        q='is:unread is:important'
    ).execute()

    for message in results.get('messages', []):
        email_data = get_email_details(service, message['id'])
        create_email_md(email_data)  # Create task file
```

---

### Step 2: Drop .md in Needs_Action/

**File Created:** `Needs_Action/email_20260225_090022.md`

```markdown
---
type: email
from: client@company.com
subject: Pricing Inquiry
received: 2026-02-25T09:00:22
keywords: pricing, inquiry
---
Hi,

I'm interested in learning more about your enterprise pricing tiers.
Could you share detailed information?

Best regards,
John Doe
```

---

### Step 3: Orchestrator Triggers (Every 5min)

**Code:** `Core/ralph_loop.py`
```python
def monitor_needs_action():
    """Check Needs_Action/ folder every 5 minutes."""
    while True:
        tasks = scan_needs_action_folder()
        for task_file in tasks:
            process_task(task_file)
        time.sleep(300)  # 5 minutes
```

---

### Step 4: TaskRouter Routes Task to Skill

**Code:** `Core/task_router.py`
```python
def route_task(task_metadata: Dict) -> Tuple[str, Dict]:
    """Route task to appropriate skill based on keywords."""

    keywords = task_metadata.get('keywords', [])
    subject = task_metadata.get('subject', '').lower()

    # Routing rules
    if 'pricing' in keywords or 'pricing' in subject:
        return 'social_post_skill', {
            'platform': 'linkedin',
            'content': 'Exciting news! Enterprise pricing now available. DM for details! 🚀',
            'image_path': None
        }

    if 'help' in keywords or 'support' in subject:
        return 'email_response_skill', {
            'template': 'support_acknowledgment'
        }

    # Default route
    return 'ralph_loop_skill', {
        'task_description': f"Process: {task_metadata.get('subject')}"
    }
```

---

### Step 5: Multi-Step → RALPH Loop Runs Iterations

**Code:** `Core/ralph_loop.py`
```python
def run_until_complete(self, task_description: str, max_iterations: int = 10):
    iteration = 0
    state = {'task': task_description, 'status': 'in_progress'}

    while iteration < max_iterations:
        iteration += 1

        # Analyze current state
        analysis = self._analyze_state(state)

        # Decide next action
        decision = self._make_decision(analysis)

        # Execute skill
        skill = self.skill_registry.get(decision['skill'])
        result = skill.execute(**decision['context'])

        # Update state
        state['steps_completed'].append(result)

        # Check completion
        if result.get('status') == 'completed':
            state['status'] = 'completed'
            break

        # Retry with backoff on failure
        if result.get('status') == 'error':
            time.sleep(2 ** iteration)

    return state
```

---

### Step 6: Skill Checks HITL (Human-in-the-Loop)

**File Movement:** `Needs_Action/` → `Pending_Approval/` → `Approved/`

**Code:** `Approval/approval_engine.py`
```python
def check_approval_required(task_metadata: Dict) -> bool:
    """Check if task requires human approval."""

    # High-priority actions need approval
    if task_metadata.get('priority') == 'high':
        return True

    # Social media posts need approval
    if task_metadata.get('action_type') == 'social_post':
        return True

    # Financial transactions need approval
    if 'payment' in task_metadata.get('keywords', []):
        return True

    return False

def move_to_pending_approval(task_file: str):
    """Move task to Pending_Approval/ for human review."""
    src = os.path.join(NEEDS_ACTION_DIR, task_file)
    dst = os.path.join(PENDING_APPROVAL_DIR, task_file)
    shutil.move(src, dst)
```

**Human Review:**
```
User opens: Pending_Approval/email_20260225_090022.md
Reviews content
Adds: approved: true
Moves to: Approved/
```

---

### Step 7: Execute via MCP

**Code:** `Skills/social_post_skill.py`
```python
def execute(self, **context) -> Dict:
    platform = context.get('platform')  # 'linkedin'
    content = context.get('content')

    # Get appropriate MCP server
    from MCP.linkedin_mcp import LinkedInMCPServer
    mcp = LinkedInMCPServer()
    mcp.connect()

    # Execute action
    result = mcp.execute('create_post', {
        'content': content
    })

    return result
```

**MCP Execution:** `MCP/linkedin_mcp.py`
```python
def _execute_action(self, action: str, payload: Dict) -> Dict:
    if action == 'create_post':
        # LinkedIn API call
        response = self.client.share(text=payload['content'])
        return MCPResponse.success({
            'post_id': response['id'],
            'url': response['url']
        }, action)
```

---

### Step 8: Log Action (Audit Logger)

**Code:** `MCP/mcp_server_base.py`
```python
def execute(self, action: str, payload: Dict) -> Dict:
    result = self._execute_action(action, payload)

    # Log to audit trail
    self.audit_logger.log(
        server_name=self.server_name,
        action=action,
        status=result['status'],
        payload=payload,
        result=result
    )

    return result
```

**Log Entry:** `Logs/mcp_audit.json`
```json
{
  "timestamp": "2026-02-25T09:05:30",
  "server": "linkedin_mcp",
  "action": "create_post",
  "status": "success",
  "payload": {
    "content": "Exciting news! Enterprise pricing now available. DM for details! 🚀"
  },
  "result": {
    "status": "success",
    "data": {
      "post_id": "urn:li:share:7045123456789",
      "url": "https://linkedin.com/posts/..."
    }
  }
}
```

---

### Step 9: Move to Done/

**Code:** `Core/ralph_loop.py`
```python
def complete_task(task_file: str, result: Dict):
    """Move completed task to Done/ folder."""

    # Add completion metadata
    task_path = os.path.join(APPROVED_DIR, task_file)
    with open(task_path, 'a', encoding='utf-8') as f:
        f.write(f"\n---\ncompleted: {datetime.now().isoformat()}\n")
        f.write(f"result: {json.dumps(result)}\n")

    # Move to Done/
    dst = os.path.join(DONE_DIR, task_file)
    shutil.move(task_path, dst)

    logger.info(f"Task completed: {task_file}")
```

**Final State:**
```
Done/email_20260225_090022.md
```

---

### Step 10: Weekly → Audit Skill Generates Briefing

**Trigger:** Every Sunday at 6 PM

**Code:** `Audit/weekly_report.py`
```python
def generate_weekly_briefing():
    engine = WeeklyAuditEngine()

    # Calculate date range (last 7 days)
    week_end = datetime.now()
    week_start = week_end - timedelta(days=7)

    # Generate report
    report = engine.generate_report(week_start, week_end)

    # Save reports
    engine._save_weekly_report(report)
    engine._save_ceo_briefing(report)

    logger.info("Weekly briefing generated")
```

**Output:** `Audits/CEO_Briefing.md`
```markdown
# CEO Briefing Report
**Period:** February 18-25, 2026

## This Week's Highlights
- ✅ Processed 45 tasks (84% success rate)
- ✅ Posted to 4 social platforms
- ✅ Responded to 67 emails
- ✅ Handled 89 WhatsApp messages

## Pricing Inquiry Example
- Client: client@company.com
- Action: LinkedIn post created
- Result: Post ID urn:li:share:7045123456789
- Engagement: 312 likes, 23 comments

## Recommendations
1. Follow up with client@company.com (high engagement)
2. Schedule more pricing-related content
```

---

## Real-World Deployment Notes

### 1. Simulation Mode

**Purpose:** Test without making real API calls.

**Configuration (`.env`):**
```bash
SIMULATE_SOCIAL=true
```

**Effect:**
- Posts are logged but not published
- Responses include `"simulated": true`
- Safe for development/testing

**Code Example:**
```python
# Social/facebook_poster.py
def post(content: str) -> Dict:
    if SIMULATE:
        logger.info(f"[SIMULATE] Facebook post: {content}")
        return {
            "status": "success",
            "data": {
                "simulated": True,
                "content": content
            }
        }

    # Actual Facebook API call
    # ...
```

---

### 2. Secrets Management

**File:** `.env` (NOT committed to version control)

```bash
# ===========================================
# Gold Tier Configuration
# ===========================================

# Social Media Simulation Mode
SIMULATE_SOCIAL=true

# Audit Day
AUDIT_DAY=Sunday

# Rate Limits
RATE_LIMIT_POSTS_PER_DAY=5

# MCP Settings
MCP_MAX_RETRIES=3
MCP_RETRY_DELAY=2

# API Keys (NEVER commit these!)
GMAIL_CREDENTIALS_PATH=Integrations/Gmail/credentials.json
LINKEDIN_ACCESS_TOKEN=your_token_here
TWITTER_BEARER_TOKEN=your_token_here
FACEBOOK_ACCESS_TOKEN=your_token_here
INSTAGRAM_ACCESS_TOKEN=your_token_here
```

**Load in Code:**
```python
# Core/config.py
from dotenv import load_dotenv
load_dotenv('.env')

SIMULATE_SOCIAL = os.getenv('SIMULATE_SOCIAL', 'false').lower() == 'true'
RATE_LIMIT = int(os.getenv('RATE_LIMIT_POSTS_PER_DAY', '5'))
```

**.gitignore:**
```gitignore
.env
*.json
token.json
credentials.json
Logs/
Data/
Needs_Action/
Done/
```

---

### 3. Scalability (Cloud VM Deployment)

### Minimum Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 20 GB | 50 GB SSD |
| Network | 10 Mbps | 100 Mbps |

### Deployment Steps

**1. Provision VM (AWS/Azure/GCP)**
```bash
# Ubuntu 22.04 LTS
aws ec2 run-instances --image-id ami-0123456789 --instance-type t3.medium
```

**2. Install Dependencies**
```bash
sudo apt update
sudo apt install -y python3 python3-pip git
pip3 install -r requirements.txt
playwright install chromium
```

**3. Configure Environment**
```bash
cp .env.example .env
nano .env  # Add API keys
```

**4. Run as Systemd Service**
```ini
# /etc/systemd/system/ai-employee.service
[Unit]
Description=AI Employee Vault
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AI_Employee
ExecStart=/usr/bin/python3 Core/ralph_loop.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
sudo systemctl status ai-employee
```

**5. Set Up Cron for Weekly Audit**
```bash
crontab -e
# Add: Every Sunday at 6 PM
0 18 * * 0 cd /home/ubuntu/AI_Employee && python3 Audit/weekly_report.py
```

---

### 4. Privacy & Security (Local-First)

### Local-First Architecture

**All data stored locally:**
- Task files: `Needs_Action/`, `Done/`
- Logs: `Logs/`
- State: `Data/`
- Sessions: `Integrations/*/`

**No cloud dependencies** (except for API calls to external platforms)

### Security Best Practices

**1. File Permissions**
```bash
chmod 600 .env
chmod 600 Integrations/Gmail/credentials.json
chmod 700 Logs/
```

**2. Session Encryption**
```python
# Encrypt session tokens at rest
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

encrypted_token = cipher.encrypt(session_token.encode())
```

**3. Network Security**
```bash
# Firewall rules (UFW)
sudo ufw allow ssh
sudo ufw allow out 443/tcp  # HTTPS for API calls
sudo ufw enable
```

**4. Regular Credential Rotation**
```bash
# Monthly reminder
# Add to calendar: Rotate API keys on 1st of each month
```

**5. Audit Trail Access**
```bash
# Only allow owner to read logs
chown -R ubuntu:ubuntu Logs/
chmod 750 Logs/
```

---

### 5. Monitoring & Alerts

### Health Check Endpoint

**Code:** `Core/health_check.py`
```python
def system_health() -> Dict:
    """Check system health."""
    return {
        'status': 'healthy',
        'watchers': {
            'gmail': check_watcher_health('gmail'),
            'whatsapp': check_watcher_health('whatsapp'),
            'instagram': check_watcher_health('instagram')
        },
        'mcp_servers': {
            'gmail_mcp': check_mcp_health('gmail_mcp'),
            'linkedin_mcp': check_mcp_health('linkedin_mcp')
        },
        'disk_usage': get_disk_usage(),
        'memory_usage': get_memory_usage()
    }
```

### Alert Conditions

| Condition | Alert Method | Threshold |
|-----------|--------------|-----------|
| Watcher down | Email | 10 minutes |
| MCP server error | WhatsApp | 3 consecutive errors |
| Disk full | Email | 90% usage |
| High error rate | WhatsApp | >10% failure rate |

---

## Appendix A: File Structure

```
AI_Employee/
├── Core/                      # Reasoning Layer
│   ├── ralph_loop.py          # Main orchestration
│   ├── task_router.py         # Task routing logic
│   └── approval_engine.py     # HITL approval
├── Integrations/              # Perception Layer
│   ├── Gmail/
│   │   └── gmail_watcher.py
│   ├── WhatsApp/
│   │   ├── whatsapp_watcher.py
│   │   └── whatsapp_auto_reply.py
│   ├── Instagram/
│   │   └── instagram_watcher.py
│   └── LinkedIn/
│       └── linkedin_scheduler.py
├── MCP/                       # Action Layer
│   ├── mcp_server_base.py     # Base class
│   ├── gmail_mcp.py
│   ├── linkedin_mcp.py
│   ├── twitter_mcp.py
│   ├── facebook_mcp.py
│   ├── instagram_mcp.py
│   └── whatsapp_mcp.py
├── Skills/                    # Skill Registry
│   ├── agent_skill_base.py    # Base class
│   ├── social_post_skill.py
│   ├── audit_skill.py
│   └── email_response_skill.py
├── Audit/                     # Audit Layer
│   ├── weekly_report.py
│   └── error_handler.py
├── Social/                    # Social Posters
│   ├── facebook_poster.py
│   ├── instagram_poster.py
│   └── x_poster.py
├── Needs_Action/              # Input Queue
├── Pending_Approval/          # Awaiting Review
├── Approved/                  # Ready to Execute
├── Done/                      # Completed Tasks
├── Logs/                      # Audit Trail
│   ├── mcp_audit.json
│   ├── skills_audit.json
│   ├── ralph_decisions.json
│   └── errors.json
├── Data/                      # State Storage
│   ├── state_store.json
│   └── weekly_metrics.json
├── Docs/                      # Documentation
│   ├── architecture.md
│   └── architecture_gold.md
├── .env                       # Configuration
└── requirements.txt           # Dependencies
```

---

## Appendix B: Quick Reference Commands

### Run Components

```powershell
# Gmail Watcher
python Integrations\Gmail\gmail_watcher.py

# WhatsApp Watcher
python Integrations\WhatsApp\whatsapp_watcher.py

# Instagram Watcher
python Integrations\Instagram\instagram_watcher.py

# WhatsApp Auto-Reply
python Integrations\WhatsApp\whatsapp_auto_reply.py

# RALPH Loop (Main Orchestrator)
python Core\ralph_loop.py

# Weekly Audit
python Audit\weekly_report.py

# Test MCP Server
python MCP\gmail_mcp.py
python MCP\linkedin_mcp.py
python MCP\instagram_mcp.py
```

### View Logs

```powershell
# Real-time log tailing
Get-Content Logs\mcp_audit.json -Wait
Get-Content Logs\ralph_loop.log -Wait

# View latest decisions
python -c "import json; print(json.dumps(json.load(open('Logs/ralph_decisions.json'))[-5:], indent=2))"
```

---

**END OF GOLD TIER ARCHITECTURE DOCUMENT**

*Generated by AI Employee Vault - Documentation System*  
*Version: Gold Tier v1.0*  
*Date: February 25, 2026*
