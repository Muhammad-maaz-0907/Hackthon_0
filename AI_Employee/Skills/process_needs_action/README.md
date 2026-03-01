# Process Needs Action Skill

## Overview
This skill processes all markdown files in the Needs_Action folder by reading them, updating the dashboard, and moving them to the Done folder.

## Purpose
- Look inside the Needs_Action/ folder
- For each .md file found:
  - Read its content
  - Read Company_Handbook.md to follow the rules
  - Decide what to do (simple summary for Bronze: just acknowledge + move to Done/)
  - Append a short status line to Dashboard.md
  - Move the task file from Needs_Action/ → Done/

## Behavior
1. List all files in Needs_Action/
2. For each file:
   - Read it
   - Append to Dashboard.md: "- Processed: [filename] at [current time]"
   - Move file to Done/ folder
3. If no files → append "- No pending tasks" to Dashboard.md

## Output Format
YAML with the following structure:
```yaml
status: success | partial | error
processed_count: number
moved_files:
  - file1.md
  - file2.md
dashboard_updated: true/false
message: short explanation
```

## Usage
Simply call the skill without any input parameters. It will automatically scan and process all .md files in the Needs_Action folder.