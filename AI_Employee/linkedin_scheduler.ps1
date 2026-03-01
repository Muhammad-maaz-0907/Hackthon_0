# LinkedIn Poster Scheduler
# Run this script as Administrator to create a scheduled task for LinkedIn posting

$taskName = "AI_Employee_LinkedIn_Poster"
$taskPath = "\AI_Employee\"
$posterPath = "D:\Hacthon 0\AI_Employee_Vault\AI_Employee\Integrations\LinkedIn\linkedin_poster.py"
$pythonPath = "python"

# Create scheduled task action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $posterPath

# Create trigger (run daily at 9 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 9am

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the scheduled task
Register-ScheduledTask -TaskName $taskName -TaskPath $taskPath -Action $action -Trigger $trigger -Settings $settings

Write-Host "LinkedIn Poster scheduled task created successfully!"
Write-Host "Task will run daily at 9:00 AM"

# To view the task:
# Get-ScheduledTask -TaskPath $taskPath

# To remove the task:
# Unregister-ScheduledTask -TaskName $taskName -TaskPath $taskPath -Confirm:$false
