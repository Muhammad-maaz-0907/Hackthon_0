# Instagram Watcher - Quick Start Guide

## 🚀 How to Run

### Step 1: Open Terminal
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
```

### Step 2: Run the Watcher
```powershell
python Integrations\Instagram\instagram_watcher.py
```

---

## 📋 What Happens Next

1. **Browser Opens** - A Chromium browser window will launch
2. **Login to Instagram** - If not already logged in, manually log in to your Instagram account
3. **Session Saved** - Your login session is saved for future runs
4. **Monitoring Starts** - The watcher begins monitoring for:
   - 📩 **Direct Messages** containing keywords
   - 💬 **Comments** on your posts
   - 🏷️ **Mentions** by other users

---

## 🔍 What It Monitors

### Keywords (20 total):
```
urgent, help, hello, hi, hey, test, collab, 
collaboration, partnership, sponsor, question, 
inquiry, business, pricing, dm, message, 
contact, reach out
```

### Example Output in Terminal:
```
Instagram Watcher - Gold Tier
========================================
Monitoring: DMs and Notifications (comments, mentions)
Keywords: urgent, help, hello, hi, hey... (20 total)
Poll interval: 15 seconds
========================================

Starting browser... Please log in to Instagram manually if prompted.

Instagram Watcher running - Waiting for login if needed...
Monitoring Instagram for new messages and notifications...

Press Ctrl+C to stop.

INFO:__main__:Found 12 potential DM conversations
INFO:__main__:DM from: john_doe | Message: Hey! I'd like to collaborate on a project...
[MATCH] Keyword found in DM from: john_doe

[NEW Instagram DM] From: @john_doe | Text: Hey! I'd like to collaborate on a project...
INFO:__main__:Created Instagram file: instagram_dm_20260225_143022.md
```

---

## 📁 Where Files Are Created

### Needs_Action Folder
When a keyword match is found, a markdown file is created:
```
Needs_Action/
├── instagram_dm_20260225_143022.md
├── instagram_comment_20260225_145530.md
└── instagram_mention_20260225_151215.md
```

### Logs Folder
All activity is logged to:
```
Logs/instagram.json
```

---

## ⚙️ Configuration

### Change Polling Interval
Edit `Integrations/Instagram/instagram_watcher.py`:
```python
POLL_INTERVAL = 15  # Change to 30, 60, etc.
```

### Add Custom Keywords
Edit the `KEYWORDS` list:
```python
KEYWORDS = [
    'urgent', 'help', 'hello',  # existing keywords
    'your_custom_keyword',       # add yours here
    'another_keyword'
]
```

---

## 🛑 How to Stop

Press **Ctrl+C** in the terminal to stop the watcher.

---

## 🔄 Daily Workflow

1. **Morning**: Start the Instagram Watcher
2. **Throughout the day**: Monitor `Needs_Action/` folder for new messages
3. **Respond**: Use the Instagram MCP or manually respond via Instagram
4. **Evening**: Stop the watcher (optional - can run 24/7)

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser doesn't open | Check if Playwright is installed: `pip install playwright` |
| Login required every time | Session saved in `Integrations/Instagram/instagram_session/` |
| No messages detected | Ensure you're logged into the correct Instagram account |
| Too many files created | Adjust keywords to be more specific |

---

## 📝 Example Markdown File

**File:** `Needs_Action/instagram_dm_20260225_143022.md`

```markdown
---
type: instagram
source_type: dm
from: john_doe
time: 2026-02-25T14:30:22
preview: Hello, I'd like to collaborate...
---
Message: Hello, I'd like to collaborate on a project!
```

---

## 🔗 Related Components

- **`MCP/instagram_mcp.py`** - For posting to Instagram
- **`Social/instagram_poster.py`** - For cross-domain posting
- **`approval_engine.py`** - For task approval workflow

---

*Created: February 25, 2026*
*Version: Gold Tier v1.0*
