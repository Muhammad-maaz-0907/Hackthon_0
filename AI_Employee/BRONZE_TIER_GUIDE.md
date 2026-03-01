# 🥉 BRONZE TIER - COMPLETE GUIDE

## 📋 What We Achieved in Bronze Tier

### ✅ Completed Components

| Component | Status | Purpose |
|-----------|--------|---------|
| **Basic RALPH Loop** | ✅ Complete | Core task monitoring engine |
| **Gmail Integration** | ✅ Complete | Read and send emails |
| **Task Processor** | ✅ Complete | Process markdown task files |
| **Folder Structure** | ✅ Complete | Needs_Action, Approved, Archive |
| **Basic Logging** | ✅ Complete | Simple text-based logging |

---

## 🎯 BRONZE TIER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    BRONZE TIER OVERVIEW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PERCEPTION LAYER (Basic Monitoring)                            │
│  └── Gmail Watcher (IMAP/SMTP)                                  │
│                                                                  │
│  ACTION LAYER (Basic Actions)                                   │
│  └── Gmail Actions (read, send, reply)                          │
│                                                                  │
│  CORE LAYER (Simple Task Router)                                │
│  └── RALPH Loop (file system monitoring)                        │
│                                                                  │
│  STORAGE LAYER (Basic Folders)                                  │
│  ├── Needs_Action/       └── Archive/                           │
│  └── Approved/                                                  │
│                                                                  │
│  LOGGING (Simple Text Logs)                                     │
│  └── activity.log                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 HOW TO RUN EVERYTHING

### Quick Test Commands

Open **Powerhell** and run these commands:

```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"
```

---

### 1. Test Core System (Basic RALPH Loop)

```powershell
python Core\ralph_loop.py
```
**Expected Output:**
```
RALPH Loop starting...
Monitoring Needs_Action folder...
No new tasks found.
```
Press `Ctrl+C` to stop.

---

### 2. Test Gmail Basic Functions

```powershell
python Integrations\Gmail\gmail_watcher.py
```
**Expected Output:**
```
Gmail Watcher starting...
Checking for new emails...
No new emails found.
```
Press `Ctrl+C` to stop.

---

### 3. Test Task Processor

```powershell
python task_processor.py
```
**Expected Output:**
```
Task Processor starting...
Scanning Needs_Action folder...
No tasks to process.
```
Press `Ctrl+C` to stop.

---

### 4. Create and Process a Test Task

**Step 1: Create a test task file**
```powershell
@"
# Task: Send Test Email

**Priority:** Medium
**To:** test@example.com
**Subject:** Bronze Tier Test
**Body:** This is a test email from Bronze Tier system.
"@ | Out-File -FilePath "Needs_Action\Test_Email_Task.md" -Encoding utf8
```

**Step 2: Move task to Approved**
```powershell
Move-Item "Needs_Action\Test_Email_Task.md" "Approved/"
```

**Step 3: Run task processor**
```powershell
python task_processor.py
```

**Expected Output:**
```
Task Processor starting...
Found task: Test_Email_Task.md
Processing: Send Test Email
✅ Task completed successfully
```

---

## 📊 COMPLETE TEST SCRIPT

Save this as `test_bronze_tier.ps1`:

```powershell
# Bronze Tier Complete Test Suite
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BRONZE TIER - COMPLETE TEST SUITE  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"

function Test-Module {
    param($Name, $Command)
    Write-Host "`n[TEST] $Name" -ForegroundColor Yellow
    try {
        Invoke-Expression $Command
        Write-Host "[PASS] $Name" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] $Name - $_" -ForegroundColor Red
    }
}

# Test basic imports
Write-Host "`n=== Testing Basic Imports ===" -ForegroundColor Cyan
Test-Module "Core" "python -c 'from Core import ralph_loop; print(\"OK\")'"
Test-Module "Gmail" "python -c 'from Integrations.Gmail import gmail_watcher; print(\"OK\")'"

# Test folder structure
Write-Host "`n=== Testing Folder Structure ===" -ForegroundColor Cyan
$folders = @("Needs_Action", "Approved", "Archive")
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Write-Host "[PASS] Folder exists: $folder" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Folder missing: $folder" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   TEST SUITE COMPLETE                 " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
```

---

## 🔍 FOLDER STRUCTURE - EXPLAINED

### Location: Root Directory

```
AI_Employee_Vault/
├── Needs_Action/         # New tasks land here
├── Approved/             # Approved tasks ready for execution
├── Archive/              # Completed tasks stored here
├── AI_Employee/          # Main code directory
│   ├── Core/             # Basic RALPH loop
│   └── Integrations/     # Platform integrations
│       └── Gmail/        # Gmail integration only
└── Logs/
    └── activity.log      # Simple text log
```

---

### 📌 Role of Each Folder

**1. Needs_Action/**
- **Purpose:** Inbox for new tasks
- **Watched by:** RALPH Loop
- **File Format:** `.md` files with task description
- **Example:**
  ```markdown
  # Task: Send Welcome Email
  
  **To:** client@example.com
  **Subject:** Welcome!
  **Body:** Welcome to our service!
  ```

**2. Approved/**
- **Purpose:** Tasks ready for execution
- **Watched by:** Task Processor
- **Action:** Tasks here get executed automatically

**3. Archive/**
- **Purpose:** Historical record of completed tasks
- **Organization:** Simple flat structure
- **Retention:** Indefinite

---

## 📄 TASK FILE FORMAT - BRONZE TIER

### Simple Task Template

```markdown
# Task: [Task Name]

**Priority:** Low/Medium/High
**To:** email@example.com
**Subject:** Email Subject Line
**Body:** Email content here
```

---

### Priority Levels (Bronze Tier):

| Priority | Description | Example |
|----------|-------------|---------|
| **Low** | Routine tasks | Daily reports, documentation |
| **Medium** | Standard tasks | Client emails, updates |
| **High** | Urgent tasks | Time-sensitive requests |

---

## 📊 LOG FILES - BRONZE TIER

| Log File | What It Tracks |
|----------|----------------|
| `Logs/activity.log` | Simple text log of all activities |
| `Logs/ralph.log` | RALPH loop events |
| `Logs/gmail.log` | Gmail operations |

---

### Example Log Entry (activity.log):

```
2026-03-01 10:30:00 - RALPH: Detected new task: Test_Email_Task.md
2026-03-01 10:30:01 - Task Processor: Processing task: Send Test Email
2026-03-01 10:30:02 - Gmail: Email sent to test@example.com
2026-03-01 10:30:03 - Task Processor: Task completed successfully
2026-03-01 10:30:04 - Archive: Task moved to Archive/
```

---

## ✅ BRONZE TIER CHECKLIST

Run this checklist to verify everything works:

```powershell
cd "D:\Hacthon 0\AI_Employee_Vault\AI_Employee"

# 1. Check basic imports work
python -c "from Core import ralph_loop; from Integrations.Gmail import gmail_watcher; print('✅ All imports OK')"

# 2. Check folder structure exists
dir Needs_Action, Approved, Archive

# 3. Check Logs folder exists
dir Logs

# 4. Create simple test task
@"
# Task: Bronze Tier Test

**Priority:** Low
**Subject:** Test Email
**Body:** Testing Bronze Tier system.
"@ | Out-File -FilePath "Needs_Action\Bronze_Test.md" -Encoding utf8

# 5. View the test task
type Needs_Action\Bronze_Test.md

# 6. Run RALPH loop (press Ctrl+C to stop)
python Core\ralph_loop.py
```

---

## 🎯 SUMMARY

### Bronze Tier = **Foundation + Email Automation**

| Feature | Status |
|---------|--------|
| **Watchers** | Gmail only |
| **Actions** | Email (send, receive, reply) |
| **Core** | Basic RALPH Loop |
| **Folders** | Basic (Needs_Action, Approved, Archive) |
| **Logging** | Simple text logs |
| **Scheduling** | None |

---

## 🔄 BRONZE TIER WORKFLOW

```
1. Create task file in Needs_Action/
        ↓
2. RALPH Loop detects new file
        ↓
3. Task is reviewed (manually or automatically)
        ↓
4. Task moves to Approved/
        ↓
5. Task Processor executes the task
        ↓
6. Gmail sends email
        ↓
7. Activity logged to activity.log
        ↓
8. Task archived to Archive/
```

---

## 🛠️ TROUBLESHOOTING

### Gmail Not Working

**Check:**
1. Gmail credentials are set up
2. `credentials.json` exists in `Integrations/Gmail/`
3. `token.json` exists (created after first auth)
4. Gmail API is enabled in Google Cloud Console

**Re-authenticate Gmail:**
```powershell
# Delete existing token
Remove-Item "Integrations/Gmail/token.json" -ErrorAction SilentlyContinue

# Run gmail_watcher to re-authenticate
python Integrations/Gmail/gmail_watcher.py
# Follow browser prompts to authorize
```

### RALPH Loop Not Detecting Tasks

**Check:**
1. Task files have `.md` extension
2. Files are in correct folder (`Needs_Action/`)
3. File contains valid markdown with `# Task:` header
4. No syntax errors in `ralph_loop.py`

### Task Processor Not Executing

**Check:**
1. Task file is in `Approved/` folder
2. Task file has proper format (Priority, Subject, Body)
3. Task Processor has no errors in logs
4. Gmail connection is active

---

## 📝 NEXT STEPS - UPGRADE TO SILVER TIER

Bronze Tier gives you:
- ✅ Basic email automation
- ✅ Simple task processing
- ✅ Foundational folder structure

**Upgrade to Silver Tier for:**
- 🥈 WhatsApp integration (messaging automation)
- 🥈 LinkedIn scheduling (post scheduling)
- 🥈 Enhanced RALPH Loop (priority classification)
- 🥈 Task Processor (advanced processing)
- 🥈 Comprehensive logging (JSON format)
- 🥈 Pending_Review folder (human oversight)

---

## 📚 BRONZE TIER QUICK REFERENCE

### Commands Cheat Sheet

```powershell
# Start RALPH Loop
python Core\ralph_loop.py

# Start Gmail Watcher
python Integrations\Gmail\gmail_watcher.py

# Start Task Processor
python task_processor.py

# View activity log
type Logs\activity.log

# List all tasks in Needs_Action
dir Needs_Action\*.md

# Move task to Approved
Move-Item "Needs_Action\TaskName.md" "Approved/"

# Archive completed task
Move-Item "Approved\TaskName.md" "Archive/"
```

---

### Task File Template (Copy & Paste)

```markdown
# Task: [Your Task Name Here]

**Priority:** Low
**To:** recipient@example.com
**Subject:** [Email Subject]
**Body:** [Email content goes here]

**Additional Notes:**
- Any extra instructions
- Attachments if needed
- Deadline information
```

---

**🚀 YOU'RE READY TO RUN THE BRONZE TIER SYSTEM!**

Start with the test commands above, create your first task, and watch the system work!
