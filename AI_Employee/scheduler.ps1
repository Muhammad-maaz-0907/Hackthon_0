# AI Employee Silver Tier Scheduler
# Configure scheduled execution of AI Employee tasks

# Example: Register scheduled task for orchestrator
# Run this script as Administrator to create the scheduled task

$taskName = "AI_Employee_Orchestrator"
$taskPath = "\AI_Employee\"
$orchestratorPath = "D:\Hacthon 0\AI_Employee_Vault\AI_Employee\orchestrator.py"
$pythonPath = "python"

# Create scheduled task action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $orchestratorPath

# Create trigger (run every 5 minutes)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the scheduled task
# Uncomment the line below to create the task
# Register-ScheduledTask -TaskName $taskName -TaskPath $taskPath -Action $action -Trigger $trigger -Settings $settings

# To view existing tasks:
# Get-ScheduledTask -TaskPath $taskPath

# To remove the task:
# Unregister-ScheduledTask -TaskName $taskName -TaskPath $taskPath -Confirm:$false

# Example: Run Gmail Watcher
# python Integrations\Gmail\gmail_watcher.py

# Example: Run WhatsApp Watcher
# python Integrations\WhatsApp\whatsapp_watcher.py

# Example: Run Approval Engine
# python Approval\approval_engine.py
