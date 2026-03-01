# Instagram Watcher - NEW Messages Only! ✅

## 🎯 What Changed?

The Instagram Watcher now **ONLY detects NEW incoming messages** sent AFTER you start it.

### Before ❌
- Showed ALL existing DM conversations
- Created files for old messages
- Couldn't distinguish old from new

### After ✅
- Captures snapshot of all current DMs on startup
- Marks all existing messages as "processed"  
- **Only detects messages received in real-time**
- Remembers processed messages across restarts

---

## 🚀 How to Run

```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python Integrations\Instagram\instagram_watcher.py
```

---

## 📋 What You'll See

### Startup Output:
```
Instagram Watcher - Gold Tier
========================================
Monitoring: Instagram DMs (Direct Messages)
Keywords: urgent, help, hello, hi, hey... (20 total)
Poll interval: 15 seconds
========================================

Starting browser... Please log in to Instagram manually if prompted.

Instagram Watcher running - Waiting for login if needed...

Capturing initial DM state (ignoring old messages)...
Clicked DM button to open inbox
Captured initial state for 13 DM conversations
✅ Will only detect NEW messages received after startup!

Monitoring for NEW incoming messages...

Press Ctrl+C to stop.
```

---

## 🎯 How It Works

### Step 1: Startup (First 15 seconds)
```
1. Browser opens Instagram.com
2. You log in (if needed)
3. Watcher clicks DM button
4. Captures snapshot of ALL current DMs
5. Marks them as "OLD/Processed"
```

### Step 2: Monitoring (Every 15 seconds)
```
1. Opens DM inbox
2. Reads all conversation previews
3. Compares with initial snapshot
4. If message is NEW → Check keywords
5. If keyword matches → Create .md file
6. Save to processed list (won't duplicate)
```

---

## 🧪 Test It!

### Send a Test Message:
1. Run the watcher
2. Wait for "Monitoring for NEW incoming messages..."
3. Send an Instagram DM from another account: "Hi, need help"
4. Watch the magic! ✨

### Expected Output:
```
NEW DM from: username | Message: Hi, need help...
[NEW Instagram DM] From: @username | Text: Hi, need help...
[MATCH] Keyword found in NEW DM from: username
Created Instagram file: instagram_dm_20260227_121530.md
```

---

## 📁 Files Created

### Needs_Action/
```
instagram_dm_20260227_121530.md
```

**Content:**
```markdown
---
type: instagram
source_type: dm
from: username
time: 2026-02-27T12:15:30
preview: Hi, need help...
---
Message: Hi, need help
```

### Logs/
```
Logs/instagram.json          - Activity log
Logs/instagram_processed.json - Remembers all processed messages
```

---

## 🔑 Keywords Monitored (20 total)

```
urgent, help, hello, hi, hey, test,
collab, collaboration, partnership, sponsor,
question, inquiry, business, pricing,
dm, message, contact, reach out
```

**Add your own:** Edit `instagram_watcher.py` line 24-28

---

## 🔄 Persistence

The watcher **remembers** processed messages even after restart:

```
Session 1 (9:00 AM):
- Captures 13 existing DMs
- New message arrives: "Hi" from @john
- Creates file, saves to processed list

Session 2 (10:00 AM):
- Loads processed list from file
- Captures initial state (now 14 DMs)
- "Hi" from @john is already processed
- Only detects NEW messages after 10:00 AM
```

---

## ⚙️ Configuration

### Change Polling Interval
Edit `instagram_watcher.py`:
```python
POLL_INTERVAL = 15  # Change to 10, 30, 60, etc.
```

### Add Custom Keywords
Edit the `KEYWORDS` list:
```python
KEYWORDS = [
    'urgent', 'help', 'hello',  # existing
    'your_keyword', 'another'   # add yours
]
```

### Clear Processed History
Delete `Logs/instagram_processed.json` to reset.

---

## 🛑 How to Stop

Press **Ctrl+C** in the terminal.

The watcher will automatically save all processed messages before exiting.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Could not capture initial state" | This is OK! Will detect all as new on first run |
| "Not detecting new messages" | Check if message contains keywords |
| "Too many files created" | Add more specific keywords |
| "Browser closes immediately" | Check if Instagram is accessible |

---

## 📊 What's Monitored vs Ignored

| Monitored ✅ | Ignored ❌ |
|-------------|-----------|
| NEW DMs received after startup | Old DMs in inbox |
| Messages with keywords | Messages without keywords |
| All conversations (first 20) | Notifications (disabled) |

---

## 🆚 Comparison: Instagram vs WhatsApp Watcher

| Feature | Instagram Watcher | WhatsApp Watcher |
|---------|------------------|------------------|
| **Platform** | Instagram DMs | WhatsApp Messages |
| **Poll Interval** | 15 seconds | 5 seconds |
| **Keywords** | 20 keywords | 9 keywords |
| **Session** | instagram_session/ | whatsapp_session/ |
| **Output** | instagram_*.md | whatsapp_*.md |
| **Logs** | instagram.json | whatsapp_replies.json |

---

## 📝 Example Workflow

```
1. Run Instagram Watcher
   ↓
2. Captures 13 existing DMs (ignores them)
   ↓
3. NEW DM arrives: "Hi, need pricing info"
   ↓
4. Keyword "pricing" detected
   ↓
5. Creates: Needs_Action/instagram_dm_20260227_121530.md
   ↓
6. You review the file
   ↓
7. Respond manually via Instagram
```

---

## ✅ Summary

**What Changed:**
- ✅ Captures initial state on startup
- ✅ Ignores all existing messages
- ✅ Only detects NEW incoming messages
- ✅ Remembers processed messages across restarts
- ✅ Saves state on exit

**How to Use:**
```powershell
python Integrations\Instagram\instagram_watcher.py
```

**What to Expect:**
- Browser opens Instagram
- Captures initial DMs (first 15 seconds)
- Monitors every 15 seconds
- **Only NEW messages trigger alerts**

---

*Updated: February 27, 2026*
*Version: Gold Tier v2.0 - NEW Messages Only*
