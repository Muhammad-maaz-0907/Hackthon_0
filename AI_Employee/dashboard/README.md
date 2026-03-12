# AI Employee Vault - Dashboard

Complete web-based control panel for managing your AI Employee automation system.

---

## 🚀 Quick Start

### 1. Start Backend

```cmd
cd AI_Employee\dashboard\backend
python main.py
```

Keep this terminal open!

### 2. Open Frontend

In a new terminal:

```cmd
start "" AI_Employee\dashboard\frontend\index.html
```

Or double-click `index.html` in File Explorer.

---

## 📡 Features

### ✅ Watchers Control
- **Start/Stop Gmail Watcher** - Monitor incoming emails
- **Start/Stop WhatsApp Watcher** - Monitor WhatsApp messages
- **Start/Stop Instagram Watcher** - Monitor Instagram DMs and notifications
- **Stop All** - Emergency stop for all watchers

### 📧 Email Messaging
- Send emails via Gmail
- View sent email history
- Task creation in Needs_Action folder

### 💬 WhatsApp Messaging
- Send WhatsApp messages to any number
- Select country code from dropdown
- View message history with status
- Real-time message tracking

### 📸 Instagram Messaging
- Send DMs to Instagram users
- View sent DM history
- Task-based automation

### 📱 Social Media Posting
- Post to LinkedIn
- Post to Twitter/X
- Post to Facebook
- Post to Instagram
- Character counter
- Hashtag support

### 🤖 AI Content Generator
- Generate text content
- Generate social media posts
- Generate replies to messages
- Multiple tone options:
  - Professional
  - Friendly
  - Engaging
  - Helpful
  - Enthusiastic

### 📊 Log Viewer
- View all system logs
- Filter by type (WhatsApp, Email, Social)
- Search logs by keyword
- Clear logs functionality

---

## 🗂️ Backend Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point |
| `watchers_api.py` | Watcher control endpoints |
| `whatsapp_api.py` | WhatsApp messaging API |
| `email_api.py` | Email sending API |
| `instagram_api.py` | Instagram DM API |
| `social_api.py` | Social media posting API |
| `ai_api.py` | AI content generation API |
| `logs_api.py` | Log viewing API |

---

## 🔌 API Endpoints

### Watchers (`/api/watchers`)
- `POST /start-gmail` - Start Gmail watcher
- `POST /start-whatsapp` - Start WhatsApp watcher
- `POST /start-instagram` - Start Instagram watcher
- `POST /stop-watchers` - Stop all watchers
- `GET /status` - Get watcher status

### WhatsApp (`/api/whatsapp`)
- `POST /send-whatsapp` - Send WhatsApp message
- `GET /messages` - Get WhatsApp message history

### Email (`/api/email`)
- `POST /send-email` - Send email
- `GET /sent` - Get sent emails

### Instagram (`/api/instagram`)
- `POST /send-dm` - Send Instagram DM
- `GET /messages` - Get Instagram DM history

### Social Media (`/api/social`)
- `POST /post-linkedin` - Post to LinkedIn
- `POST /post-twitter` - Post to Twitter
- `POST /post-facebook` - Post to Facebook
- `POST /post-instagram` - Post to Instagram

### AI Generation (`/api/ai`)
- `POST /generate-text` - Generate text
- `POST /generate-post` - Generate social post
- `POST /generate-reply` - Generate reply

### Logs (`/api/logs`)
- `GET /` - Get all log files
- `GET /whatsapp-logs` - Get WhatsApp logs
- `GET /email-logs` - Get email logs
- `GET /{filename}` - Get specific log file
- `POST /clear` - Clear all logs

---

## 📁 Frontend Files

| File | Purpose |
|------|---------|
| `index.html` | Landing/welcome page |
| `dashboard.html` | Main dashboard UI |
| `script.js` | Frontend logic and API calls |

---

## 🛠️ Installation

### Backend Requirements

```cmd
cd AI_Employee\dashboard\backend
pip install -r requirements.txt
```

### Optional: For Full Automation

To enable actual WhatsApp and Instagram sending (not just task creation):

```cmd
pip install selenium
```

For Gmail API:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth credentials
4. Download as `credentials.json`
5. Place in `AI_Employee/Integrations/Gmail/`

---

## 🎯 How It Works

### Task-Based System

When you send a message (WhatsApp, Email, Instagram), the system:

1. **Creates a task file** in `Needs_Action/` folder
2. **Logs the action** to JSON log files
3. **Attempts to send** via automation scripts
4. **Updates status** (queued → sent/failed)

### Watcher System

Watchers run in the background and:

1. **Monitor** their respective platforms
2. **Detect** new messages/notifications
3. **Create tasks** for important items
4. **Log activities** to JSON files

---

## 📊 Dashboard Sections

1. **Watchers** - Control automation scripts
2. **WhatsApp** - Send messages and view history
3. **Email** - Send emails and view sent items
4. **Instagram** - Send DMs and view history
5. **Social Posting** - Post to multiple platforms
6. **AI Generator** - Generate content with AI
7. **Log Viewer** - View all system logs

---

## 🔧 Troubleshooting

### Backend Won't Start
- Check if port 8000 is available
- Run `pip install -r requirements.txt`
- Check for Python errors in terminal

### Frontend Shows "Disconnected"
- Make sure backend is running
- Check browser console for errors
- Verify `http://localhost:8000/api/health` works

### Messages Not Sending
- Check if Selenium is installed (`pip install selenium`)
- For Gmail: Verify `credentials.json` exists
- Messages are queued if automation unavailable

---

## 🌐 API Documentation

Interactive API docs available at:
```
http://localhost:8000/docs
```

This shows all endpoints with test buttons!

---

## 📝 Notes

- **Keep backend running** while using the dashboard
- **Logs are auto-saved** to `AI_Employee/Logs/` folder
- **Tasks are created** in `AI_Employee/Needs_Action/` folder
- **Auto-refresh** runs every 30 seconds

---

## 🚀 What's New

✅ WhatsApp messaging with history  
✅ Email sending via Gmail  
✅ Instagram DM sending  
✅ Social media posting to 4 platforms  
✅ AI content generation  
✅ Comprehensive log viewer  
✅ Real-time status updates  

---

**Built for AI Employee Vault - Hackathon 0**
