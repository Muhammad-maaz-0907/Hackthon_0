# Instagram Integration - Gold Tier

## Components

### 1. Instagram Watcher (`instagram_watcher.py`)

**Purpose:** Continuously monitors Instagram for:
- **Direct Messages (DMs)** - Incoming messages containing keywords
- **Comments** - New comments on your posts
- **Mentions** - When users mention you in posts/comments

**Features:**
- ✅ Persistent browser session (saves login)
- ✅ Keyword-based filtering
- ✅ Creates markdown files in `Needs_Action/` folder
- ✅ JSON logging to `Logs/instagram.json`
- ✅ Duplicate message detection
- ✅ Rate-limited polling (15 second intervals)

**Keywords Monitored:**
```
urgent, help, hello, hi, hey, test, collab, collaboration, 
partnership, sponsor, question, inquiry, business, pricing, 
dm, message, contact, reach out
```

---

## Setup

### 1. Install Dependencies

Make sure Playwright is installed:

```bash
pip install playwright
playwright install chromium
```

### 2. First Run

```bash
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python Integrations\Instagram\instagram_watcher.py
```

**What happens:**
1. A browser window opens
2. Navigate to Instagram and log in manually (first time only)
3. Session is saved to `Integrations/Instagram/instagram_session/`
4. Watcher starts monitoring automatically

### 3. Subsequent Runs

Your Instagram session is persisted, so you won't need to log in again (unless Instagram clears sessions).

---

## Output

### Needs_Action Files

When a keyword match is found, a markdown file is created:

**DM Example:** `Needs_Action/instagram_dm_20260225_143022.md`
```markdown
---
type: instagram
source_type: dm
from: username
time: 2026-02-25T14:30:22
preview: Hello, I'd like to collaborate...
---
Message: Hello, I'd like to collaborate on a project!
```

**Comment Example:** `Needs_Action/instagram_comment_20260225_143530.md`
```markdown
---
type: instagram
source_type: comment
from: username
time: 2026-02-25T14:35:30
notification_type: comment
---
Message: username mentioned you in a comment: Great post!
```

### Logs

All activity is logged to `Logs/instagram.json`:
```json
{
  "timestamp": "2026-02-25T14:30:22",
  "activity_type": "dm_detected",
  "data": {
    "username": "username",
    "message_preview": "Hello, I'd like to collaborate...",
    "keywords_matched": ["collab", "hello"]
  }
}
```

---

## Configuration

### Change Polling Interval

Edit `instagram_watcher.py`:
```python
POLL_INTERVAL = 15  # Change to desired seconds
```

### Add/Remove Keywords

Edit the `KEYWORDS` list in `instagram_watcher.py`:
```python
KEYWORDS = [
    'urgent', 'help', 'hello',  # Add your keywords here
    'your_keyword', 'another_keyword'
]
```

---

## Usage in Workflow

1. **Watcher runs continuously** in background
2. **Incoming messages** matching keywords → `Needs_Action/` folder
3. **Review markdown files** to see what needs attention
4. **Process messages** using your existing approval workflow
5. **Respond via Instagram MCP** (optional automation)

---

## Troubleshooting

### "Session expired" or login required
- Instagram may have cleared your session
- Log in again manually when browser opens
- Session will be re-saved automatically

### "No messages detected"
- Ensure you're logged into the correct Instagram account
- Check if DM panel is accessible on Instagram Web
- Instagram may have updated their UI (selectors may need updating)

### "Too many duplicate files"
- Check `processed_messages` set in memory
- Restart the watcher to clear the set
- Files are deduplicated based on message content hash

### Browser crashes frequently
- Increase `POLL_INTERVAL` to reduce load
- Ensure sufficient system resources
- Try running in headless mode (change `headless=True`)

---

## Integration with MCP

The Instagram Watcher works alongside:
- **`MCP/instagram_mcp.py`** - For posting content
- **`Social/instagram_poster.py`** - For cross-domain posting

**Full workflow:**
```
Instagram DM → Watcher → Needs_Action → Approval Engine → MCP → Post Response
```

---

## Security Notes

- ⚠️ **Session data** is stored in `instagram_session/` folder
- ⚠️ **Do not share** your session folder with others
- ✅ **Credentials** are NOT stored in plain text
- ✅ **Use a dedicated business account** for automation

---

## API Limitations

Instagram Web does not have an official public API for:
- Reading DMs programmatically
- Reading comments/mentions programmatically

This watcher uses **browser automation** (Playwright) to interact with Instagram Web, similar to the WhatsApp watcher.

**For production use**, consider:
- Instagram Graph API (requires Business account)
- Third-party Instagram management tools
- Meta Business Suite integration

---

*Version: Gold Tier v1.0*
*Last Updated: February 25, 2026*
