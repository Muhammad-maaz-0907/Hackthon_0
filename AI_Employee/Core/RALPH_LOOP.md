# RALPH Loop - Autonomous Decision Engine

**Ralph**: Recursive Autonomous Learning & Processing Handler

## Overview

The RALPH Loop is the central autonomous decision engine that continuously monitors for tasks, routes them to appropriate skills, executes with retry logic, and logs all actions. It's designed to never crash the entire system and continues operating even if individual MCPs or skills fail.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      RALPH Loop                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ State Store  │───▶│  Task Router │───▶│Skill Executor│      │
│  │              │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         ▲                                       │               │
│         │                                       ▼               │
│         │    ┌──────────────────────────────────────┐          │
│         │    │   Multi-Step Orchestrator            │          │
│         └────│   (Detects & executes sequences)     │◀─────────┤
│              └──────────────────────────────────────┘          │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Decision Logger & Task History              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. StateStore
Manages task state in `Data/state_store.json`.

**Features:**
- Add/update tasks
- Get pending tasks (sorted by priority)
- Track task status and retry count

### 2. TaskRouter
Routes tasks to appropriate skills based on content analysis.

**Routing Rules:**
| Keywords | Skill | Default Action |
|----------|-------|----------------|
| post, social, marketing | marketing_skill | post_all |
| email, reply, respond | operations_skill | process_gmail |
| whatsapp, message, chat | operations_skill | process_whatsapp |
| briefing, report, summary | ceo_briefing_skill | generate |
| generate, create content | marketing_skill | generate_content |

### 3. SkillExecutor
Executes skills with error handling and retry logic.

**Features:**
- Exponential backoff retry (1s, 2s, 4s)
- Skill instance caching
- Success/failure logging

### 4. MultiStepOrchestrator
Detects and executes multi-step task sequences.

**Example Patterns:**
- "post marketing update" → generate_content → post_all
- "email and whatsapp" → process_gmail → process_whatsapp

### 5. DecisionLogger
Logs all decisions to `Logs/ralph_decisions.json` for audit and learning.

### 6. TaskHistory
Records task execution history to `Logs/ralph_task_history.json`.

---

## Usage

### Basic Usage

```python
from Core.ralph_loop import RALPHLoop, TaskPriority

# Create loop
loop = RALPHLoop(poll_interval=5.0)

# Add tasks
loop.add_task(
    "Post marketing update about our new AI features",
    metadata={'content': 'Exciting AI news! 🚀'},
    priority=TaskPriority.HIGH
)

loop.add_task(
    "Generate weekly CEO briefing",
    priority=TaskPriority.NORMAL
)

# Start the loop (runs forever)
loop.start()
```

### Manual Task Processing

```python
from Core.ralph_loop import RALPHLoop

loop = RALPHLoop()

# Add a task
task_id = loop.add_task(
    "Send email to team about meeting",
    metadata={
        'to': 'team@example.com',
        'subject': 'Meeting Update'
    },
    priority=TaskPriority.HIGH
)

# Process one iteration (not continuous)
# loop._loop_iteration()

# Get stats
stats = loop.get_stats()
print(f"Tasks processed: {stats['tasks_processed']}")
```

---

## Task Priority Levels

| Priority | Value | Use Case |
|----------|-------|----------|
| CRITICAL | 1 | Emergency, system-critical tasks |
| HIGH | 2 | Time-sensitive tasks |
| NORMAL | 3 | Standard tasks |
| LOW | 4 | Background tasks |
| BACKLOG | 5 | When resources available |

---

## Task Status States

| Status | Description |
|--------|-------------|
| `pending` | Waiting to be processed |
| `in_progress` | Currently being executed |
| `completed` | Successfully completed |
| `failed` | Failed after all retries |
| `retrying` | Scheduled for retry |
| `cancelled` | Manually cancelled |

---

## Multi-Step Task Detection

RALPH automatically detects multi-step patterns:

### Pattern 1: Marketing Post
**Input:** "Post marketing update about our new product"

**Detected Steps:**
1. `marketing_skill.generate_content` - Generate 3 content variations
2. `marketing_skill.post_all` - Post to all platforms

### Pattern 2: Cross-Platform Response
**Input:** "Send email and follow up on whatsapp"

**Detected Steps:**
1. `operations_skill.process_gmail` - Process emails
2. `operations_skill.process_whatsapp` - Process WhatsApp

---

## Retry Logic

Tasks are automatically retried up to 3 times with exponential backoff:

```
Attempt 1: Immediate
Wait 1 second
Attempt 2: Retry
Wait 2 seconds
Attempt 3: Retry
Wait 4 seconds
Attempt 4: Final retry
→ Mark as failed if all attempts fail
```

---

## State Store Format

`Data/state_store.json`:

```json
{
  "tasks": [
    {
      "id": "task_20260224162156_0",
      "description": "Post marketing update",
      "metadata": {"content": "Exciting news!"},
      "priority": 2,
      "status": "completed",
      "created_at": "2026-02-24T16:21:56",
      "started_at": "2026-02-24T16:21:57",
      "completed_at": "2026-02-24T16:22:05",
      "retry_count": 0,
      "max_retries": 3,
      "result": {"status": "success", ...}
    }
  ],
  "last_updated": "2026-02-24T16:22:05",
  "system_status": "running"
}
```

---

## Log Files

| File | Purpose |
|------|---------|
| `Logs/ralph_loop.log` | Main RALPH loop logs |
| `Logs/ralph_decisions.json` | Decision audit trail |
| `Logs/ralph_task_history.json` | Task execution history |
| `Data/state_store.json` | Current task state |

---

## Statistics

Get real-time statistics:

```python
stats = loop.get_stats()
print(stats)

# Output:
{
    "tasks_processed": 15,
    "tasks_failed": 2,
    "multistep_detected": 3,
    "retries_total": 5,
    "uptime_seconds": 3600,
    "success_rate": 0.88,
    "pending_tasks": 4
}
```

---

## Error Handling

RALPH is designed to never crash:

1. **Individual task failures** → Task marked as failed, loop continues
2. **Skill import errors** → Logged, task scheduled for retry
3. **MCP failures** → Graceful degradation, continue with other tasks
4. **State store corruption** → Create new state, log error
5. **KeyboardInterrupt** → Graceful shutdown

---

## Best Practices

### 1. Task Descriptions
Be specific in task descriptions for better routing:
```python
# Good
loop.add_task("Post to LinkedIn about our Q1 results")

# Better (includes metadata)
loop.add_task(
    "Post quarterly results",
    metadata={
        'platform': 'linkedin',
        'content': 'Q1 results: 25% growth! 📈'
    }
)
```

### 2. Priority Assignment
```python
# Urgent customer issue
TaskPriority.CRITICAL

# Time-sensitive marketing post
TaskPriority.HIGH

# Regular daily briefing
TaskPriority.NORMAL

# Archive old data
TaskPriority.LOW
```

### 3. Monitoring
```python
# Check stats periodically
while True:
    stats = loop.get_stats()
    if stats['success_rate'] < 0.5:
        print("Warning: Low success rate!")
    time.sleep(60)
```

---

## Example: Full Workflow

```python
from Core.ralph_loop import RALPHLoop, TaskPriority
import time

# Initialize
loop = RALPHLoop(poll_interval=3.0)

# Add various tasks
tasks = [
    ("Post marketing update", {'content': 'New features!'}, TaskPriority.HIGH),
    ("Generate CEO briefing", {}, TaskPriority.NORMAL),
    ("Process unread emails", {'auto_respond': True}, TaskPriority.HIGH),
    ("Archive old tasks", {}, TaskPriority.LOW),
]

for desc, meta, priority in tasks:
    loop.add_task(desc, metadata=meta, priority=priority)

print(f"Added {len(tasks)} tasks")

# Run for 60 seconds
import threading
timer = threading.Timer(60.0, loop.stop)
timer.start()

# Start processing
loop.start()

# Print final stats
loop.print_stats()
```

---

## Troubleshooting

### Task Not Processing
- Check `Data/state_store.json` for task status
- Verify skill imports work: `python -c "from Skills.marketing_skill import MarketingSkill"`
- Check `Logs/ralph_loop.log` for errors

### High Failure Rate
- Review `Logs/ralph_decisions.json` for patterns
- Check MCP server availability
- Verify credentials in `.env`

### Memory Issues
- Task history auto-truncates to 1000 entries
- Decision log auto-truncates to 500 entries
- Restart loop to clear skill cache

---

*Last Updated: February 24, 2026*
*Version: Gold Tier v1.0*
