# WhatsApp Auto-Reply Agent - Quick Start Guide

## 🚀 What It Does

This agent automatically replies to WhatsApp messages 24/7 with intelligent responses based on keywords.

### Features:
- ✅ **24/7 Automated Responses** - Never miss a message
- ✅ **Keyword-Based Replies** - Smart responses based on message content
- ✅ **Business Hours Mode** - Only reply during working hours (optional)
- ✅ **Rate Limiting** - Avoid spam (max replies per chat per hour)
- ✅ **Group Chat Filtering** - Skip group chats if desired
- ✅ **Natural Delay** - Waits a few seconds before replying (looks human)
- ✅ **Full Logging** - All replies logged to JSON

---

## 📋 How to Run

### Step 1: Open Terminal
```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
```

### Step 2: Run the Auto-Reply Agent
```powershell
python Integrations\WhatsApp\whatsapp_auto_reply.py
```

### Step 3: Log In to WhatsApp Web
- A browser window will open
- Scan the QR code with your phone (first time only)
- Your session is saved for future runs

### Step 4: Let It Run!
- The agent monitors all incoming messages
- Automatically replies based on keywords
- Press **Ctrl+C** to stop

---

## ⚙️ Configuration

The config file is at: `Integrations/WhatsApp/auto_reply_config.json`

### Key Settings:

```json
{
  "enabled": true,                    // Turn auto-reply on/off
  "business_hours_only": false,       // Only reply during business hours
  "business_hours": {
    "start": 9,                       // 9 AM
    "end": 17                         // 5 PM
  },
  "delay_seconds": 3,                 // Wait 3 seconds before replying
  "max_replies_per_chat_per_hour": 5, // Max 5 replies to same person/hour
  "exclude_groups": true              // Don't reply in group chats
}
```

---

## 💬 Default Auto-Replies

| Keyword | Auto-Reply |
|---------|-----------|
| `hello` | "Hello! 👋 Thanks for reaching out. This is an automated response. I'll get back to you soon!" |
| `hi` | "Hi there! 👋 Thanks for your message. I'll respond as soon as possible!" |
| `hey` | "Hey! 👋 Got your message. I'll reply shortly!" |
| `urgent` | "⚡ I see this is urgent. I'll prioritize your message and respond ASAP!" |
| `help` | "🆘 I received your help request. Someone will assist you shortly!" |
| `pricing` | "💰 Thanks for your interest in pricing. I'll send you detailed information soon!" |
| `invoice` | "📄 Invoice request received. I'll process this and get back to you!" |
| `payment` | "💳 Payment inquiry noted. I'll respond with details shortly!" |
| `default` | "Thanks for your message! 🙏 This is an automated reply. I'll respond properly soon!" |

---

## 🔧 Customize Responses

Edit `auto_reply_config.json` to add your own responses:

### Example: Add Custom Keywords

```json
"keywords": {
  "hello": "Your custom hello message",
  "demo": "🎯 Thanks for requesting a demo! I'll schedule one shortly!",
  "contact": "📧 You can reach me at email@example.com",
  "thanks": "😊 You're welcome! Let me know if you need anything else!",
  "default": "Your default message for unmatched keywords"
}
```

### Example: Enable Business Hours Only

```json
{
  "business_hours_only": true,
  "business_hours": {
    "start": 9,
    "end": 18
  }
}
```

---

## 📊 View Logs

All auto-replies are logged to:
```
Logs/whatsapp_replies.json
Logs/whatsapp_auto_reply.log
```

### Log Entry Example:
```json
{
  "timestamp": "2026-02-25T15:30:22",
  "chat_name": "John Doe",
  "original_message": "Hi, I need help with pricing",
  "reply": "💰 Thanks for your interest in pricing. I'll send you detailed information soon!",
  "status": "sent"
}
```

---

## 🛑 How to Stop

Press **Ctrl+C** in the terminal to stop the agent.

---

## ⚠️ Important Notes

### WhatsApp Terms of Service
- ⚠️ **Personal Accounts**: Auto-messaging may violate WhatsApp ToS
- ✅ **Business API**: Consider WhatsApp Business API for production use
- ⚠️ **Use Responsibly**: Don't spam or send unwanted messages

### Rate Limiting
- Default: Max **5 replies per chat per hour**
- Prevents WhatsApp from flagging your account
- Adjust in config if needed

### Session Persistence
- Your WhatsApp session is saved in `whatsapp_session/` folder
- Don't share this folder with others
- If login expires, just re-scan QR code

---

## 🔄 Daily Workflow

### Option 1: Run 24/7
```powershell
# Start the agent and let it run continuously
python Integrations\WhatsApp\whatsapp_auto_reply.py
```

### Option 2: Run During Business Hours Only
```powershell
# Edit config: "business_hours_only": true
# Then run the agent
python Integrations\WhatsApp\whatsapp_auto_reply.py
```

### Option 3: Run as Background Service (Windows)
Create a batch file `start_whatsapp_bot.bat`:
```batch
@echo off
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
python Integrations\WhatsApp\whatsapp_auto_reply.py
```

Use **Task Scheduler** to run it automatically on startup.

---

## 🎯 Example Scenarios

### Scenario 1: Customer Inquiry
```
Customer: "Hi, I need pricing info"
Bot: "💰 Thanks for your interest in pricing. I'll send you detailed information soon!"
```

### Scenario 2: Urgent Request
```
Customer: "This is urgent! Need help now"
Bot: "⚡ I see this is urgent. I'll prioritize your message and respond ASAP!"
```

### Scenario 3: General Message
```
Customer: "Are you available tomorrow?"
Bot: "Thanks for your message! 🙏 This is an automated reply. I'll respond properly soon!"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not replying to messages" | Check if `enabled: true` in config |
| "Replying to group chats" | Set `exclude_groups: true` |
| "Too many replies" | Reduce `max_replies_per_chat_per_hour` |
| "Session expired" | Re-scan QR code when browser opens |
| "Not finding chat input" | Make sure WhatsApp Web is fully loaded |

---

## 📝 Comparison: Watcher vs Auto-Reply

| Feature | WhatsApp Watcher | WhatsApp Auto-Reply |
|---------|-----------------|---------------------|
| **Purpose** | Monitor & save messages | Automatically respond |
| **Output** | Creates .md files in Needs_Action/ | Sends replies in WhatsApp |
| **Action** | Passive (just watches) | Active (replies automatically) |
| **Use Case** | Human reviews later | Instant 24/7 responses |

**You can run both together!** One watches for important messages, the other auto-replies.

---

## 🔗 Related Files

- `whatsapp_watcher.py` - Original watcher (saves to Needs_Action/)
- `whatsapp_auto_reply.py` - New auto-reply agent
- `auto_reply_config.json` - Configuration file
- `Logs/whatsapp_replies.json` - Reply history

---

*Created: February 25, 2026*
*Version: Gold Tier v1.0*
