# 🤖 AI Employee Vault

A multi-tier AI automation system for business operations, featuring Gmail, WhatsApp, Instagram, LinkedIn, and social media integrations.

## 📚 Documentation

| Tier | Description | Guide |
|------|-------------|-------|
| 🥉 **Bronze** | Basic email automation + task processing | [BRONZE_TIER_GUIDE.md](AI_Employee/BRONZE_TIER_GUIDE.md) |
| 🥈 **Silver** | WhatsApp + LinkedIn + Enhanced RALPH | [SILVER_TIER_GUIDE.md](AI_Employee/SILVER_TIER_GUIDE.md) |
| 🏆 **Gold** | Full cross-domain automation + CEO reporting | [GOLD_TIER_GUIDE.md](AI_Employee/GOLD_TIER_GUIDE.md) |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- API credentials for platforms you want to use

### Installation

```bash
cd AI_Employee
pip install -r requirements.txt
```

### Run Bronze Tier (Basic)
```bash
python Core/ralph_loop.py
python task_processor.py
```

### Run Silver Tier (Intermediate)
```bash
python Core/ralph_loop.py
python Integrations/Gmail/gmail_watcher.py
python Integrations/WhatsApp/whatsapp_watcher.py
python Integrations/LinkedIn/linkedin_scheduler.py
```

### Run Gold Tier (Full System)
```bash
python Core/ralph_loop.py
python Integrations/Gmail/gmail_watcher.py
python Integrations/WhatsApp/whatsapp_auto_reply.py
python Integrations/Instagram/instagram_watcher.py
python MCP/*.py
python Skills/*.py
python Audit/weekly_report.py
```

## 📁 Project Structure

```
AI_Employee_Vault/
├── AI_Employee/           # Main code directory
│   ├── Core/              # RALPH loop engine
│   ├── Integrations/      # Platform integrations
│   │   ├── Gmail/
│   │   ├── WhatsApp/
│   │   ├── Instagram/
│   │   └── LinkedIn/
│   ├── MCP/               # MCP Servers
│   ├── Skills/            # Agent skills
│   ├── Social/            # Social media posters
│   ├── Audit/             # Reporting & error handling
│   └── Logs/              # Audit logs
├── Needs_Action/          # New tasks inbox
├── Approved/              # Approved tasks
├── Pending_Review/        # Tasks awaiting review
├── Archive/               # Completed tasks
└── README.md
```

## 🔧 Configuration

1. Copy `.env.example` to `.env` in the `AI_Employee/` folder
2. Add your API credentials:
   - Gmail API credentials
   - WhatsApp Web session
   - Instagram credentials
   - LinkedIn credentials
   - Social media API keys

## 📊 Features

### Bronze Tier
- ✅ Gmail integration (read, send, reply)
- ✅ Basic RALPH task router
- ✅ Task processor with markdown files
- ✅ Simple folder-based workflow

### Silver Tier (adds)
- ✅ WhatsApp message monitoring
- ✅ LinkedIn post scheduling
- ✅ Enhanced RALPH with priority classification
- ✅ JSON logging

### Gold Tier (adds)
- ✅ Instagram DM & notification monitoring
- ✅ Facebook, Instagram, X auto-posting
- ✅ 6 MCP Servers for standardized APIs
- ✅ Agent skills (Marketing, Operations, CEO Briefing)
- ✅ Weekly audit engine
- ✅ CEO briefing generator
- ✅ Centralized error handler with retry logic

## 🧪 Testing

Run the test suite for your tier:

```bash
# Bronze Tier
python -c "from Core import ralph_loop; from Integrations.Gmail import gmail_watcher; print('OK')"

# Silver Tier
python -c "from Core import ralph_loop; from Integrations.Gmail import gmail_watcher; from Integrations.WhatsApp import whatsapp_watcher; print('OK')"

# Gold Tier
python -c "from Core import ralph_loop; from MCP import gmail_mcp; from Skills import MarketingSkill; print('OK')"
```

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**Built for the Hackathon 0** 🚀
