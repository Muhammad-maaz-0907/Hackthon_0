# AI Employee Vault - Command Reference

A centralized automation system that monitors multiple communication channels (Gmail, WhatsApp, LinkedIn) and captures important messages for processing.

---

## 📁 Project Structure

```
AI_Employee/
├── Integrations/
│   ├── Gmail/
│   │   └── gmail_watcher.py      # Monitor Gmail for important emails
│   ├── WhatsApp/
│   │   └── whatsapp_watcher.py   # Monitor WhatsApp messages
│   └── LinkedIn/
│       └── linkedin_scheduler.ps1 # LinkedIn automation
├── Needs_Action/                  # Captured messages appear here
├── send_email.py                  # Send emails from terminal
└── scheduler.ps1                  # Master scheduler
```

---

## 🚀 Quick Start

### 1. Navigate to the AI_Employee Directory
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
```

### 2. Run Any Watcher
```powershell
python Integrations\<Watcher_Name>\<watcher_name>.py
```

---

## 📧 Gmail Watcher

Monitors your Gmail inbox for **unread + important** emails and creates markdown files in `Needs_Action/`.

### Configuration
- **Polling Interval:** 120 seconds (2 minutes)
- **Filters:** `is:unread is:important`
- **Output:** `Needs_Action/email_<message_id>.md`

### Run Command
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python Integrations\Gmail\gmail_watcher.py
```

### First-Time Setup
1. Ensure `credentials.json` exists in `Integrations/Gmail/`
2. On first run, browser will open for OAuth authentication
3. Grant Gmail permissions
4. `token.json` will be created automatically

### Modify Polling Speed
Edit `Integrations/Gmail/gmail_watcher.py`:
```python
POLL_INTERVAL = 30  # Change from 120 to desired seconds
```

---

## 💬 WhatsApp Watcher

Monitors WhatsApp Web for messages containing keywords and creates markdown files in `Needs_Action/`.

### Configuration
- **Polling Interval:** 10 seconds
- **Keywords:** `urgent`, `invoice`, `payment`, `pricing`, `help`, `hello`, `hi`, `test`, `hey`
- **Output:** `Needs_Action/whatsapp_<timestamp>.md`

### Run Command
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python Integrations\WhatsApp\whatsapp_watcher.py
```

### First-Time Setup
1. A Chromium browser window will open
2. Scan QR code to log into WhatsApp Web
3. Session is saved in `Integrations/WhatsApp/whatsapp_session/`
4. Future runs will stay logged in

### Modify Keywords
Edit `Integrations/WhatsApp/whatsapp_watcher.py`:
```python
KEYWORDS = ['urgent', 'invoice', 'payment', 'your_keyword']
```

### Modify Polling Speed
Edit `Integrations/WhatsApp/whatsapp_watcher.py`:
```python
POLL_INTERVAL = 3  # Change from 10 to desired seconds
```

---

## 💼 LinkedIn Scheduler

Automates LinkedIn posting and activity monitoring.

### Run Command
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
powershell -ExecutionPolicy Bypass -File linkedin_scheduler.ps1
```

---

## 📤 Send Email

Send emails directly from the terminal using your Gmail account.

### Interactive Mode (Recommended)
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python send_email.py
```

**Then follow the prompts:**
```
To: recipient@example.com
Subject: Your Subject
Enter email body (type 'SEND' on a new line to send):
Your message here...
SEND
```

### One-Liner Mode
```powershell
python -c "from send_email import send_email; send_email('recipient@example.com', 'Subject', 'Message body')"
```

---

## 📂 Output Location

All captured messages are saved to:
```
D:\Hacthon 0\AI_Employee_Vault\AI_Employee\Needs_Action\
```

### File Types
| Type | Pattern | Example |
|------|---------|---------|
| Gmail | `email_*.md` | `email_19be6e7f2ec7e15b.md` |
| WhatsApp | `whatsapp_*.md` | `whatsapp_20260222_143645.md` |
| LinkedIn | `linkedin_post_*.md` | `linkedin_post_20260221_150048.md` |

---

## 🗑️ Cleanup Commands

### Delete All Email Files
```powershell
del "Needs_Action\email_*.md"
```

### Delete All WhatsApp Files
```powershell
del "Needs_Action\whatsapp_*.md"
```

### Delete All LinkedIn Files
```powershell
del "Needs_Action\linkedin_post_*.md"
```

### Delete All Captured Files
```powershell
del "Needs_Action\*.md"
```

---

## 🔧 Running Multiple Watchers Simultaneously

Open multiple terminal windows/tabs and run different watchers:

**Terminal 1 - Gmail:**
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python Integrations\Gmail\gmail_watcher.py
```

**Terminal 2 - WhatsApp:**
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python Integrations\WhatsApp\whatsapp_watcher.py
```

---

## 🛑 Stopping a Watcher

Press **`Ctrl + C`** in the terminal to stop any running watcher.

---

## 📋 Quick Reference Table

| Watcher | Command | Polling | Output |
|---------|---------|---------|--------|
| Gmail | `python Integrations\Gmail\gmail_watcher.py` | 120s | `Needs_Action/email_*.md` |
| WhatsApp | `python Integrations\WhatsApp\whatsapp_watcher.py` | 10s | `Needs_Action/whatsapp_*.md` |
| LinkedIn | `powershell -File linkedin_scheduler.ps1` | - | `Needs_Action/linkedin_post_*.md` |
| Send Email | `python send_email.py` | - | - |

---

## ⚠️ Troubleshooting

### Gmail Watcher Issues
- **Error: `credentials.json not found`** → Add your Gmail API credentials file
- **Error: `token.json expired`** → Delete `token.json` and re-authenticate

### WhatsApp Watcher Issues
- **Not detecting messages** → Ensure WhatsApp Web is fully loaded
- **Session expired** → Re-scan QR code when browser opens
- **Messages not detected immediately** → Reduce `POLL_INTERVAL` in the script

### General Issues
- **Module not found** → Run `pip install -r requirements.txt`
- **Permission denied** → Run terminal as Administrator

---

## 📦 Dependencies

Install all required packages:
```powershell
pip install -r requirements.txt
```

Key packages:
- `playwright` - WhatsApp browser automation
- `google-api-python-client` - Gmail API
- `google-auth-httplib2` - Gmail authentication

---

**Last Updated:** February 22, 2026
