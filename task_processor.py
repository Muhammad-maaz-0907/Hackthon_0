import os
import json
import shutil
import datetime
from pathlib import Path

def process_task_files():
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    needs_action_dir = os.path.join(base_dir, 'Needs_Action')
    plans_dir = os.path.join(base_dir, 'Plans')
    done_dir = os.path.join(base_dir, 'Done')
    logs_dir = os.path.join(base_dir, 'Logs')
    
    # Create logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Get today's date for log file
    today = datetime.date.today().strftime('%Y-%m-%d')
    log_file_path = os.path.join(logs_dir, f'{today}.json')
    
    # Find all markdown files in Needs_Action
    markdown_files = [f for f in os.listdir(needs_action_dir) if f.endswith('.md')]
    
    if not markdown_files:
        print("No markdown files to process in Needs_Action")
        return
    
    for file in markdown_files:
        try:
            file_path = os.path.join(needs_action_dir, file)
            
            # Read the content of the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a plan file in Plans directory
            plan_filename = f"plan_{file}"
            plan_path = os.path.join(plans_dir, plan_filename)
            
            with open(plan_path, 'w', encoding='utf-8') as plan_file:
                plan_file.write(f"# Plan for {file}\n\n")
                plan_file.write("## Task Analysis\n")
                plan_file.write("- Identified task from incoming file\n")
                plan_file.write("- Analyzed requirements\n")
                plan_file.write("- Created implementation steps\n\n")
                plan_file.write("## Implementation Steps\n")
                plan_file.write("1. Step 1: Analyze the request\n")
                plan_file.write("2. Step 2: Plan the solution\n")
                plan_file.write("3. Step 3: Execute the plan\n")
                plan_file.write("4. Step 4: Verify completion\n\n")
                plan_file.write("## Status\n")
                plan_file.write("- Status: Completed\n")
                plan_file.write("- Completed at: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
            
            # Update status in original file to completed
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n- Status: Completed at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Move original file to Done directory
            done_file_path = os.path.join(done_dir, file)
            shutil.move(file_path, done_file_path)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "action": "processed",
                "original_file": file,
                "plan_file": plan_filename,
                "moved_to": "Done"
            }
            
            # Append log entry to today's log file
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