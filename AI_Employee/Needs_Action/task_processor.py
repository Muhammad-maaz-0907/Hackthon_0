import os
import json
import shutil
import datetime
import re
from pathlib import Path

def parse_frontmatter(content):
    """Extract frontmatter metadata from markdown file."""
    frontmatter = {}
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter, body
    return {}, content

def process_linkedin_post(file_path, content, frontmatter, body, base_dir):
    """Process LinkedIn post - create draft for approval."""
    approval_dir = os.path.join(base_dir, 'Approval', 'pending_actions')
    os.makedirs(approval_dir, exist_ok=True)
    
    filename = os.path.basename(file_path)
    approval_file = os.path.join(approval_dir, f"draft_{filename}")
    
    draft_content = f"""---
type: linkedin_post
status: pending_approval
created_at: {datetime.datetime.now().isoformat()}
original_file: {filename}
---

# Draft LinkedIn Post

{body.strip()}

---
**Action Required:** Review and approve this post
- To approve: Move to ../Approval/approved/
- To reject: Delete or move back to Needs_Action/
"""
    
    with open(approval_file, 'w', encoding='utf-8') as f:
        f.write(draft_content)
    
    return f"Created draft for approval: {approval_file}"

def process_email(file_path, content, frontmatter, body):
    """Process email - extract info and create action item."""
    email_data = {
        'from': frontmatter.get('from', 'Unknown'),
        'subject': frontmatter.get('subject', 'No Subject'),
        'received': frontmatter.get('received', 'Unknown'),
        'type': frontmatter.get('type', 'email')
    }
    
    action_content = f"""---
type: email_action
status: needs_review
created_at: {datetime.datetime.now().isoformat()}
---

# Email Action Item

**From:** {email_data['from']}  
**Subject:** {email_data['subject']}  
**Received:** {email_data['received']}

## Content
{body.strip()}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to team
- [ ] Archive
- [ ] Create follow-up task
"""
    
    action_file = file_path.replace('.md', '_action.md')
    with open(action_file, 'w', encoding='utf-8') as f:
        f.write(action_content)
    
    return f"Created email action item: {action_file}"

def process_generic_task(file_path, content, frontmatter, body):
    """Process generic task - create plan and move to done."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plans_dir = os.path.join(base_dir, 'Plans')
    os.makedirs(plans_dir, exist_ok=True)
    
    filename = os.path.basename(file_path)
    plan_filename = f"plan_{filename}"
    plan_path = os.path.join(plans_dir, plan_filename)
    
    task_type = frontmatter.get('type', 'generic')
    
    with open(plan_path, 'w', encoding='utf-8') as plan_file:
        plan_file.write(f"# Plan for {filename}\n\n")
        plan_file.write("## Task Analysis\n")
        plan_file.write(f"- Type: {task_type}\n")
        plan_file.write(f"- Identified at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        plan_file.write("## Implementation Steps\n")
        plan_file.write("1. Analyze the request\n")
        plan_file.write("2. Plan the solution\n")
        plan_file.write("3. Execute the plan\n")
        plan_file.write("4. Verify completion\n\n")
        plan_file.write("## Status\n")
        plan_file.write("- Status: Completed\n")
        plan_file.write("- Completed at: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
    
    return f"Created plan: {plan_path}"

def process_task_files():
    # Get the AI_Employee directory (parent of Needs_Action)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)  # Go up to AI_Employee folder
    
    needs_action_dir = os.path.join(script_dir, 'Needs_Action')
    done_dir = os.path.join(base_dir, 'Done')
    logs_dir = os.path.join(base_dir, 'Logs')
    
    # If running from Needs_Action folder, adjust paths
    if os.path.basename(script_dir) == 'Needs_Action':
        needs_action_dir = script_dir
    else:
        needs_action_dir = os.path.join(base_dir, 'Needs_Action')

    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(done_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'Approval', 'pending_actions'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'Approval', 'approved'), exist_ok=True)

    today = datetime.date.today().strftime('%Y-%m-%d')
    log_file_path = os.path.join(logs_dir, f'{today}.json')

    markdown_files = [f for f in os.listdir(needs_action_dir)
                      if f.endswith('.md') and not f.endswith('_metadata.md')]

    if not markdown_files:
        print("No markdown files to process in Needs_Action")
        return

    for file in markdown_files:
        try:
            file_path = os.path.join(needs_action_dir, file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter, body = parse_frontmatter(content)
            task_type = frontmatter.get('type', 'generic')
            
            result = ""
            
            if task_type == 'linkedin_post':
                result = process_linkedin_post(file_path, content, frontmatter, body, base_dir)
            elif task_type == 'email':
                result = process_email(file_path, content, frontmatter, body)
            else:
                result = process_generic_task(file_path, content, frontmatter, body)
                # Move to Done for generic tasks
                done_file_path = os.path.join(done_dir, file)
                shutil.move(file_path, done_file_path)
            
            print(f"Processed {file}: {result}")
            
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "file": file,
                "type": task_type,
                "result": result
            }

            log_data = []
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r', encoding='utf-8') as log_file:
                    try:
                        log_data = json.load(log_file)
                    except json.JSONDecodeError:
                        log_data = []

            log_data.append(log_entry)

            with open(log_file_path, 'w', encoding='utf-8') as log_file:
                json.dump(log_data, log_file, indent=2)

        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")

def main():
    print("Starting task processor...")
    try:
        process_task_files()
        print("Task processing completed.")
    except Exception as e:
        print(f"Error in task processor: {str(e)}")

if __name__ == "__main__":
    main()