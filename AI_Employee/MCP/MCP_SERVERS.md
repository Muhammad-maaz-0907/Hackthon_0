# MCP Servers - Gold Tier Implementation

## Overview

This directory contains all MCP (Model Context Protocol) servers for the AI Employee Vault system. Each server extends `MCPServerBase` for consistent error handling, retry logic, and audit logging.

---

## File Structure

```
MCP/
├── mcp_server_base.py      # Base class for all MCP servers
├── social_mcp_base.py      # Social media MCP (legacy wrapper)
├── gmail_mcp.py            # Gmail API integration
├── linkedin_mcp.py         # LinkedIn API integration
├── twitter_mcp.py          # Twitter/X API integration
├── facebook_mcp.py         # Facebook Graph API integration
├── instagram_mcp.py        # Instagram Graph API integration
└── whatsapp_mcp.py         # WhatsApp Business API integration
```

---

## MCPServerBase Features

All servers inherit these capabilities:

| Feature | Description |
|---------|-------------|
| `connect()` | Establish API connection |
| `execute(action, payload)` | Execute action with error handling |
| `retry_logic()` | Exponential backoff retry (1s, 2s, 4s) |
| `handle_error()` | Graceful degradation |
| `health_check()` | Server health status |
| `disconnect()` | Clean shutdown |
| Audit logging | All operations logged to `Logs/mcp_audit.json` |

---

## Server Reference

### GmailMCPServer

**File:** `gmail_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `send_email` | `{to, subject, body, cc?}` | Send an email |
| `read_unread` | `{max_results?, label?}` | Get unread emails |
| `search_email` | `{query, max_results?}` | Search emails |

**Credentials Required:**
- `Integrations/Gmail/credentials.json` (OAuth)
- Auto-generates `token.json` on first run

**Usage:**
```python
from MCP.gmail_mcp import GmailMCPServer

server = GmailMCPServer()
server.connect()

# Send email
result = server.execute('send_email', {
    "to": "user@example.com",
    "subject": "Hello",
    "body": "Test message"
})

# Read unread
result = server.execute('read_unread', {"max_results": 5})
```

---

### LinkedInMCPServer

**File:** `linkedin_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{content, image_url?, visibility?}` | Create a post |
| `get_metrics` | `{post_id?, metric_type?}` | Get metrics |

**Credentials (Optional - simulation mode without):**
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN`
- `LINKEDIN_ORG_ID`

**Usage:**
```python
from MCP.linkedin_mcp import LinkedInMCPServer

server = LinkedInMCPServer()
result = server.execute('create_post', {
    "content": "Exciting news! #AI #Automation"
})
```

---

### TwitterMCPServer

**File:** `twitter_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{content, media_ids?, reply_to?}` | Create a tweet |
| `get_metrics` | `{tweet_id?, username?, metric_type?}` | Get metrics |

**Constraints:**
- Max 280 characters per tweet

**Credentials (Optional - simulation mode without):**
- `TWITTER_BEARER_TOKEN`
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`

**Usage:**
```python
from MCP.twitter_mcp import TwitterMCPServer

server = TwitterMCPServer()
result = server.execute('create_post', {
    "content": "Test tweet! 🚀 #AI"
})
```

---

### FacebookMCPServer

**File:** `facebook_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{message, link?, photo_url?, privacy?}` | Create a post |
| `get_metrics` | `{post_id?, metric_type?}` | Get metrics |

**Constraints:**
- Max 63,206 characters per post

**Credentials (Optional - simulation mode without):**
- `FACEBOOK_APP_ID`
- `FACEBOOK_APP_SECRET`
- `FACEBOOK_PAGE_TOKEN`
- `FACEBOOK_PAGE_ID`

**Usage:**
```python
from MCP.facebook_mcp import FacebookMCPServer

server = FacebookMCPServer()
result = server.execute('create_post', {
    "message": "Facebook post from MCP! 👍"
})
```

---

### InstagramMCPServer

**File:** `instagram_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `create_post` | `{caption, image_url?, is_video?, video_url?}` | Create a post |
| `get_metrics` | `{media_id?, metric_type?}` | Get metrics |

**Constraints:**
- Max 2,200 characters per caption
- Requires image_url or video_url

**Credentials (Optional - simulation mode without):**
- `INSTAGRAM_APP_ID`
- `INSTAGRAM_APP_SECRET`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`

**Usage:**
```python
from MCP.instagram_mcp import InstagramMCPServer

server = InstagramMCPServer()
result = server.execute('create_post', {
    "caption": "Instagram post! 📸",
    "image_url": "https://example.com/image.jpg"
})
```

---

### WhatsAppMCPServer

**File:** `whatsapp_mcp.py`

**Actions:**
| Action | Payload | Description |
|--------|---------|-------------|
| `read_messages` | `{limit?, unread_only?}` | Read from Needs_Action |
| `send_message` | `{to, message?, template_name?}` | Send a message |

**Features:**
- Reads messages captured by `whatsapp_watcher.py`
- Parses markdown files from `Needs_Action/` folder

**Credentials (Optional - simulation mode without):**
- `WHATSAPP_PHONE_ID`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_BUSINESS_ACCOUNT_ID`

**Usage:**
```python
from MCP.whatsapp_mcp import WhatsAppMCPServer

server = WhatsAppMCPServer()

# Read messages
result = server.execute('read_messages', {"limit": 10})

# Send message
result = server.execute('send_message', {
    "to": "+1234567890",
    "message": "Hello from MCP!"
})
```

---

## Response Format

All servers return standardized responses:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "error": null,
  "action": "action_name",
  "timestamp": "2026-02-24T12:00:00"
}
```

### Error Response
```json
{
  "status": "error",
  "data": null,
  "error": "Error message",
  "action": "action_name",
  "details": {
    "error_type": "ErrorType",
    "server": "server_name"
  },
  "timestamp": "2026-02-24T12:00:00"
}
```

---

## Configuration

Add credentials to `.env` file:

```bash
# Gmail (OAuth - automatic)
# Credentials in Integrations/Gmail/

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSON_URN=urn:li:person:YOUR_ID

# Twitter/X
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_PAGE_TOKEN=your_page_token

# Instagram
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id

# WhatsApp
WHATSAPP_PHONE_ID=your_phone_id
WHATSAPP_ACCESS_TOKEN=your_token

# MCP Settings
MCP_MAX_RETRIES=3
MCP_RETRY_DELAY=2
```

---

## Testing

Each server can be tested directly:

```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python MCP\gmail_mcp.py
python MCP\twitter_mcp.py
python MCP\whatsapp_mcp.py
```

---

## Audit Logging

All operations are logged to `Logs/mcp_audit.json`:

```json
[
  {
    "timestamp": "2026-02-24T12:00:00",
    "server": "twitter_mcp",
    "action": "create_post",
    "status": "success",
    "payload": {"content": "Test tweet"},
    "result": {...}
  }
]
```

---

## Error Recovery

All servers implement automatic retry with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: After 2 seconds
- Attempt 3: After 4 seconds

If all retries fail, a structured error response is returned (no crashes).

---

## Simulation Mode

All social media servers run in **simulation mode** by default when no credentials are provided. This allows:
- Safe testing without posting to real platforms
- Development without API access
- Validation of request/response formats

Set `SIMULATE_SOCIAL=false` in `.env` to disable (requires credentials).

---

*Last Updated: February 24, 2026*
*Version: Gold Tier v1.0*
