# Central Error Handler - Documentation

## Overview

The Central Error Handler provides unified error processing for the entire AI Employee system. It ensures the system never fully crashes by implementing graceful degradation, structured error logging, and intelligent retry logic.

---

## File Structure

```
Audit/
└── error_handler.py      # Centralized error handling
```

**Generated Logs:**
- `Logs/errors.json` - All error records
- `Logs/critical_errors.json` - High/critical severity only
- `Logs/error_statistics.json` - Error analytics
- `Logs/error_audit.json` - Audit trail
- `Logs/error_handler.log` - Runtime logs

---

## Features

| Feature | Description |
|---------|-------------|
| Central Error Processing | Single point for all error handling |
| Retry Wrapper | Exponential backoff retry logic |
| Structured Logging | JSON error records with context |
| Graceful Degradation | Safe defaults instead of crashes |
| System Resilience | Never fully crashes |
| Audit Integration | All errors logged to audit trail |
| Error Statistics | Analytics and trending |
| Severity Classification | LOW/MEDIUM/HIGH/CRITICAL/FATAL |
| Error Categorization | NETWORK, AUTH, VALIDATION, etc. |

---

## Usage

### Basic Error Handling

```python
from Audit.error_handler import CentralErrorHandler

# Create handler
handler = CentralErrorHandler("my_component")

# Handle an error
try:
    result = risky_operation()
except Exception as e:
    result = handler.handle(e, context={'operation': 'risky_operation'})
    print(f"Error handled: {result}")
```

### Retry with Backoff

```python
from Audit.error_handler import CentralErrorHandler

handler = CentralErrorHandler("network_ops")

# Wrap function with retry logic
@handler.retry_with_backoff(max_retries=3, base_delay=1.0)
def fetch_data():
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()

# Or wrap manually
def fetch_data():
    # ... might fail ...
    pass

wrapped = handler.retry_with_backoff(
    fetch_data,
    max_retries=3,
    base_delay=1.0,
    exceptions=(ConnectionError, Timeout)
)
result = wrapped()
```

### Safe Execution (Never Raises)

```python
from Audit.error_handler import CentralErrorHandler

handler = CentralErrorHandler("data_processor")

# Wrap function to never raise
@handler.safe_execute(default={'status': 'error', 'data': []})
def process_data(data):
    # Complex processing that might fail
    return transformed_data

# Always returns something, never crashes
result = process_data(invalid_data)
```

### Error Context Manager

```python
from Audit.error_handler import ErrorContext, get_error_handler

handler = get_error_handler("database_ops")

# Use context manager
with ErrorContext("database_query", handler) as ctx:
    result = db.execute(query)

if ctx.error:
    print(f"Error was handled gracefully: {ctx.error}")
else:
    print(f"Success: {ctx.result}")
```

### Convenience Decorators

```python
from Audit.error_handler import retry, safe

# Retry decorator
@retry(max_retries=3, base_delay=1.0)
def api_call():
    return requests.get(url).json()

# Safe execute decorator
@safe(default={'status': 'offline'})
def get_status():
    return check_service_status()
```

---

## Error Severity Levels

| Severity | Description | Action |
|----------|-------------|--------|
| LOW | Minor issues, expected errors | Log only |
| MEDIUM | Validation errors, missing data | Log and continue |
| HIGH | Connection failures, auth issues | Retry with backoff |
| CRITICAL | System errors, data corruption | Alert and retry |
| FATAL | System exit, unrecoverable | Graceful shutdown |

### Automatic Classification

Errors are automatically classified based on type and message:

```python
# HIGH severity
ConnectionError("Connection refused")
PermissionError("Access denied")
TimeoutError("Request timed out")

# MEDIUM severity
ValueError("Invalid input")
TypeError("Wrong type")
KeyError("Missing key")

# LOW severity
FileNotFoundError("Config missing")
IndexError("Out of range")
```

---

## Error Categories

| Category | Triggers |
|----------|----------|
| NETWORK | Connection, socket, HTTP errors |
| AUTHENTICATION | Auth, token, permission errors |
| VALIDATION | Value, type, key errors |
| CONFIGURATION | Config, not found, missing |
| RESOURCE | Memory, disk, resource errors |
| TIMEOUT | Timeout, timed out |
| RATE_LIMIT | Rate limit, too many requests |
| INTERNAL | Internal system errors |
| UNKNOWN | Unclassified errors |

---

## Graceful Degradation

When all retries fail, the handler returns safe defaults:

```python
# Get/fetch functions
{'status': 'degraded', 'data': [], 'error': '...'}

# Process/execute functions
{'status': 'degraded', 'processed': False, 'error': '...'}

# Send/post functions
{'status': 'degraded', 'sent': False, 'error': '...'}
```

---

## Error Statistics

Track error trends and retry success rates:

```python
handler = CentralErrorHandler("my_component")
summary = handler.get_error_summary()

print(summary)
# {
#     'component': 'my_component',
#     'statistics': {
#         'total_errors': 42,
#         'retry_success_rate': 78.5,
#         'top_categories': [('network', 15), ('validation', 10)],
#         'recent_hours': {'2026-02-24 14:00': 5, ...}
#     },
#     'recent_errors': [...],
#     'critical_count': 2,
#     'system_status': 'healthy'
# }
```

### System Status

| Status | Criteria |
|--------|----------|
| healthy | <100 errors, >50% retry success |
| warning | >100 errors OR <50% retry success |
| degraded | >5 critical errors in recent history |

---

## Integration Examples

### With MCP Servers

```python
from Audit.error_handler import CentralErrorHandler
from MCP.gmail_mcp import GmailMCPServer

class ResilientGmailMCP(GmailMCPServer):
    def __init__(self):
        super().__init__()
        self.error_handler = CentralErrorHandler("gmail_mcp")
    
    @property
    def safe_execute(self):
        return self.error_handler.safe_execute
    
    def connect(self):
        @self.error_handler.retry_with_backoff(max_retries=3)
        def _connect():
            return super().connect()
        return _connect()
```

### With Skills

```python
from Audit.error_handler import CentralErrorHandler, ErrorContext
from Skills.agent_skill_base import AgentSkill

class ResilientSkill(AgentSkill):
    def __init__(self, skill_name):
        super().__init__(skill_name)
        self.error_handler = CentralErrorHandler(skill_name)
    
    def execute(self, context):
        with ErrorContext(f"{self.skill_name}_execute", self.error_handler) as ctx:
            # Your skill logic
            result = self._execute_skill(context)
            ctx.result = result
            return result
        
        # If error occurred, return graceful degradation
        return AgentSkillResponse.error(
            str(ctx.error),
            self.skill_name,
            {'graceful_degradation': True}
        )
```

### With RALPH Loop

```python
from Core.ralph_loop import RALPHLoop
from Audit.error_handler import CentralErrorHandler

class ResilientRALPH(RALPHLoop):
    def __init__(self):
        super().__init__()
        self.error_handler = CentralErrorHandler("ralph_loop")
    
    def _process_task(self, task):
        with ErrorContext(f"process_task_{task.get('id')}", self.error_handler):
            super()._process_task(task)
    
    def _loop_iteration(self):
        # Never crash the main loop
        safe_iteration = self.error_handler.safe_execute(
            super()._loop_iteration,
            default=None
        )
        safe_iteration()
```

---

## Log File Formats

### errors.json

```json
[
  {
    "timestamp": "2026-02-24T16:48:36",
    "error_type": "ValueError",
    "error_message": "Invalid input",
    "traceback": "Traceback...",
    "context": {"operation": "validate"},
    "severity": "medium",
    "category": "validation",
    "handled": true,
    "resolved": false
  }
]
```

### error_statistics.json

```json
{
  "total_errors": 42,
  "by_severity": {
    "low": 20,
    "medium": 15,
    "high": 5,
    "critical": 2,
    "fatal": 0
  },
  "by_category": {
    "validation": 15,
    "network": 12,
    "internal": 10
  },
  "retry_successes": 8,
  "retry_failures": 2,
  "system_uptime": "2026-02-24T10:00:00"
}
```

---

## Best Practices

### 1. Always Handle Errors Centrally

```python
# Good
handler = CentralErrorHandler("component")
try:
    operation()
except Exception as e:
    handler.handle(e, context={'op': 'operation'})

# Bad - silent failure
try:
    operation()
except:
    pass
```

### 2. Use Appropriate Retry Settings

```python
# Network operations - more retries, longer delay
handler.retry_with_backoff(
    api_call,
    max_retries=5,
    base_delay=2.0,
    max_delay=120.0
)

# Validation - no retry needed
handler.safe_execute(
    validate_input,
    default={'valid': False}
)
```

### 3. Provide Meaningful Context

```python
# Good context
handler.handle(e, context={
    'user_id': user_id,
    'operation': 'process_payment',
    'amount': amount,
    'request_id': request_id
})

# Bad - no context
handler.handle(e)
```

### 4. Clear Resolved Errors Periodically

```python
# Run weekly to mark old errors as resolved
handler.clear_resolved(older_than_hours=168)  # 1 week
```

---

## API Reference

### CentralErrorHandler

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `handle()` | error, context, raise_error | Dict | Handle error centrally |
| `retry_with_backoff()` | func, max_retries, base_delay, max_delay, exceptions | Callable | Wrap with retry logic |
| `safe_execute()` | func, default, catch_exceptions | Callable | Wrap to never raise |
| `get_error_summary()` | - | Dict | Get error statistics |
| `clear_resolved()` | older_than_hours | None | Mark old errors resolved |

### ErrorRecord

| Attribute | Type | Description |
|-----------|------|-------------|
| timestamp | datetime | When error occurred |
| error_type | str | Exception class name |
| error_message | str | Exception message |
| traceback | str | Full stack trace |
| context | Dict | Additional context |
| severity | ErrorSeverity | LOW/MEDIUM/HIGH/CRITICAL/FATAL |
| category | ErrorCategory | NETWORK/AUTH/VALIDATION/etc. |

---

## Troubleshooting

### Errors Not Being Logged
- Check `Logs/` directory permissions
- Verify logger is configured
- Check disk space

### Retry Not Working
- Ensure exception type matches `exceptions` parameter
- Check `retry_recommended` in handle result
- Verify delay settings

### System Still Crashing
- Check for FATAL severity errors
- Ensure error handler is wrapping all operations
- Review `_graceful_degradation` implementation

---

*Last Updated: February 24, 2026*
*Version: Gold Tier v1.0*
