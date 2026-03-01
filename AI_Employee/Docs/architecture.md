# AI Employee Vault - System Architecture

## Overview

The AI Employee Vault is a modular automation system that monitors multiple communication channels, processes tasks, and executes actions across domains. This document describes the **Gold Tier** architecture, which builds upon the **Silver Tier** foundation.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI EMPLOYEE VAULT - GOLD TIER                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │    Gmail     │    │   WhatsApp   │    │   LinkedIn   │    │ Instagram │  │
│  │   Watcher    │    │   Watcher    │    │  Scheduler   │    │  Watcher  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └─────┬─────┘  │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             │                                                │
│                             ▼                                                │
│                  ┌─────────────────────┐                                     │
│                  │   Needs_Action/     │                                     │
│                  │  (Message Queue)    │                                     │
│                  └──────────┬──────────┘                                     │
│                             │                                                │
│         ┌───────────────────┼───────────────────┐                           │
│         │                   │                   │                            │
│         ▼                   ▼                   ▼                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │  Approval   │    │   Auto      │    │   Archive   │                      │
│  │   Engine    │    │  Process    │    │   Store     │                      │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                      │
│         │                  │                  │                              │
│         └──────────────────┼──────────────────┘                              │
│                            │                                                 │
│                            ▼                                                 │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                    MCP LAYER (Gold Tier)                     │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │           │
│  │  │   Social    │  │   Email     │  │   (Future   │          │           │
│  │  │     MCP     │  │     MCP     │  │    MCPs)    │          │           │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │           │
│  └─────────┼────────────────┼────────────────┼─────────────────┘           │
│            │                │                │                              │
│            ▼                ▼                ▼                              │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                   SOCIAL LAYER (Gold Tier)                   │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │           │
│  │  │  Facebook   │  │  Instagram  │  │      X      │          │           │
│  │  │   Poster    │  │   Poster    │  │   Poster    │          │           │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                  AUDIT & LOGGING (Gold Tier)                 │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │           │
│  │  │     CEO     │  │   Social    │  │   System    │          │           │
│  │  │  Briefing   │  │     Logs    │  │    Logs     │          │           │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tier Comparison

### Silver Tier (Foundation)
| Component | Purpose | Status |
|-----------|---------|--------|
| Gmail Watcher | Monitor inbox for important emails | ✅ Active |
| WhatsApp Watcher | Monitor WhatsApp Web for keyword messages | ✅ Active |
| LinkedIn Scheduler | Automate LinkedIn posting | ✅ Active |
| Needs_Action Queue | Centralized message storage | ✅ Active |
| Approval Engine | Human-in-the-loop task approval | ✅ Active |
| Send Email | Terminal-based email sending | ✅ Active |

### Gold Tier (Cross-Domain)
| Component | Purpose | Status |
|-----------|---------|--------|
| Social Posters | Multi-platform posting (FB, IG, X) | ✅ New |
| Social MCP | Model Context Protocol for social ops | ✅ New |
| Instagram Watcher | Monitor Instagram DMs and notifications | ✅ New |
| CEO Briefing | Automated executive summaries | ✅ New |
| Rate Limiting | Configurable post limits per day | ✅ New |
| Simulation Mode | Safe testing without real posts | ✅ New |
| Centralized Logging | JSON logs for all social activity | ✅ New |

---

## MCP Architecture

### What is MCP?

**Model Context Protocol (MCP)** provides a standardized interface for AI agents to interact with external systems. Each MCP server exposes:

1. **Actions** - Operations that can be executed
2. **Structured Responses** - Consistent JSON response format
3. **Retry Logic** - Built-in fault tolerance
4. **Logging** - All operations are auditable

### MCP Server Structure

```
MCP/
├── email_mcp_server.py    (Silver - existing)
└── social_mcp_base.py     (Gold - new)
```

### Response Format

```json
{
  "status": "success|error",
  "action": "action_name",
  "timestamp": "2026-02-22T14:30:00",
  "data": { ... },
  "error": "error_message (if applicable)"
}
```

### Supported Actions

| Action | Payload | Description |
|--------|---------|-------------|
| `post_facebook` | `{content: string}` | Post to Facebook |
| `post_instagram` | `{content: string, image_path?: string}` | Post to Instagram |
| `post_x` | `{content: string}` | Post to X (Twitter) |
| `get_stats` | `{platform: string}` | Get platform statistics |
| `schedule_post` | `{platform, content, scheduled_time}` | Schedule future post |

---

## Agent Skill Abstraction

```python
# Placeholder for Agent Skill Interface
class AgentSkill:
    """Base class for all agent skills."""
    
    def __init__(self, name: str, tier: str):
        self.name = name
        self.tier = tier
    
    def execute(self, **kwargs) -> dict:
        """Execute the skill with given parameters."""
        raise NotImplementedError
    
    def validate(self, **kwargs) -> bool:
        """Validate input parameters."""
        raise NotImplementedError


# Example: Social Posting Skill
class SocialPostingSkill(AgentSkill):
    
    def __init__(self):
        super().__init__("social_posting", "gold")
    
    def execute(self, platform: str, content: str, **kwargs) -> dict:
        # Route to appropriate poster
        if platform == "facebook":
            from Social.facebook_poster import post
            return post(content)
        # ... other platforms
    
    def validate(self, platform: str, content: str, **kwargs) -> bool:
        # Validate content length, platform support, etc.
        pass
```

---

## Cross-Domain Communication

### Data Flow

1. **Input** → Watchers capture messages from external sources
2. **Queue** → Messages stored in `Needs_Action/` with metadata
3. **Process** → Approval engine or auto-processing
4. **Action** → MCP layer executes cross-domain actions
5. **Log** → All actions logged to `Logs/` and `Audits/`

### Configuration

All tiers use `.env` for centralized configuration:

```bash
# Silver Tier
GMAIL_POLL_INTERVAL=120
WHATSAPP_POLL_INTERVAL=10

# Gold Tier
SIMULATE_SOCIAL=true
RATE_LIMIT_POSTS_PER_DAY=5
AUDIT_DAY=Sunday
MCP_MAX_RETRIES=3
MCP_RETRY_DELAY=2
```

---

## Directory Structure

```
AI_Employee/
├── Integrations/          # Silver + Gold Tier watchers
│   ├── Gmail/
│   ├── WhatsApp/
│   ├── LinkedIn/
│   └── Instagram/         # Gold Tier - NEW
├── Social/                # Gold Tier social posters
│   ├── facebook_poster.py
│   ├── instagram_poster.py
│   └── x_poster.py
├── MCP/                   # Gold Tier MCP servers
│   ├── email_mcp_server.py
│   └── social_mcp_base.py
├── Audits/                # Gold Tier audit templates
│   └── ceo_briefing_template.md
├── Docs/                  # Gold Tier documentation
│   ├── architecture.md
│   └── lessons_learned.md
├── Needs_Action/          # Silver + Gold message queue
├── Logs/                  # Silver + Gold logs
│   ├── social.json
│   └── instagram.json     # Gold Tier - NEW
├── Approval/              # Silver Tier approval
├── Archive/               # Silver Tier archive
├── Done/                  # Silver Tier completed
├── Data/                  # Gold Tier data storage
└── .env                   # Centralized configuration
```

---

## Extensibility

### Adding a New Platform

1. Create `Social/<platform>_poster.py`
2. Implement `post(content: str) -> dict`
3. Add action handler in `MCP/social_mcp_base.py`
4. Update configuration in `.env`

### Adding a New MCP Server

1. Create `MCP/<domain>_mcp_base.py`
2. Define `execute(action, payload)` function
3. Implement `retry_logic()` wrapper
4. Document supported actions

---

## Security Considerations

- API credentials stored in `.env` (not committed to version control)
- OAuth tokens stored in respective `Integrations/` folders
- Rate limiting prevents API abuse
- Simulation mode allows safe testing
- All actions logged for audit trail

---

*Last Updated: February 25, 2026*
*Version: Gold Tier v1.0*
