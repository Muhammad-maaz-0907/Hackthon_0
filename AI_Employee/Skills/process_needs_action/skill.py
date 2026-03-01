import os
import yaml
import shutil
import datetime
from pathlib import Path

def process_needs_action():
    """
    Agent Skill: process_needs_action
    Purpose:
    - Look inside the Needs_Action/ folder
    - For each .md file found:
      - Read its content
      - Read Company_Handbook.md to follow the rules
      - Decide what to do (simple summary for Bronze: just acknowledge + move to Done/)
      - Append a short status line to Dashboard.md
      - Move the task file from Needs_Action/ → Done/
    """
    
    # Define paths relative to the script's location (going up twice to reach AI_Employee)
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent  # Go up from Skills/process_needs_action to Skills, then up to AI_Employee
    
    # If we're in the Skills folder, go up once more
    if base_dir.name == 'Skills':
        base_dir = base_dir.parent
    
    needs_action_dir = base_dir / 'Needs_Action'
    done_dir = base_dir / 'Done'
    dashboard_file = base_dir / 'Dashboard.md'
    handbook_file = base_dir / 'Company_Handbook.md'
    
    # Initialize result
    result = {
        'status': 'success',
        'processed_count': 0,
        'moved_files': [],
        'dashboard_updated': False,
        'message': ''
    }
    
    try:
        # Check if Needs_Action directory exists
        if not needs_action_dir.exists():
            result['status'] = 'error'
            result['message'] = 'Needs_Action directory does not exist'
            return result
        
        # Find all .md files in Needs_Action
        md_files = list(needs_action_dir.glob('*.md'))
        
        if not md_files:
            # No files to process
            with open(dashboard_file, 'a') as dash:
                dash.write(f"- No pending tasks at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            result['dashboard_updated'] = True
            result['message'] = 'No pending tasks found'
            return result
        
        # Process each .md file
        for file_path in md_files:
            try:
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Append status to Dashboard.md
                with open(dashboard_file, 'a') as dash:
                    dash.write(f"- Processed: {file_path.name} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Move file to Done directory
                destination = done_dir / file_path.name
                shutil.move(str(file_path), str(destination))
                
                # Track the processed file
                result['moved_files'].append(file_path.name)
                result['processed_count'] += 1
                
            except Exception as e:
                result['status'] = 'partial'
                result['message'] = f'Error processing {file_path.name}: {str(e)}'
                continue
        
        # Update dashboard status
        result['dashboard_updated'] = True
        result['message'] = f'Successfully processed {result["processed_count"]} files'
        
    except Exception as e:
        result['status'] = 'error'
        result['message'] = f'Unexpected error: {str(e)}'
    
    return result

if __name__ == '__main__':
    result = process_needs_action()
    print(yaml.dump(result, default_flow_style=False))