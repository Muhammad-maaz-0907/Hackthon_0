# Bronze Tier File System Watcher for AI Employee Project
# Drops files into Needs_Action/ for processing by Claude Code

import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime

class FileHandler(FileSystemEventHandler):
    def __init__(self, drop_dir, needs_action_dir):
        self.drop_dir = drop_dir
        self.needs_action_dir = needs_action_dir

    def on_created(self, event):
        if not event.is_directory:
            self.process_new_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.process_new_file(event.dest_path)

    def process_new_file(self, file_path):
        try:
            # Wait a moment to ensure file is completely written
            time.sleep(0.5)
            
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.needs_action_dir, filename)
                
                # Copy file to Needs_Action
                shutil.copy2(file_path, dest_path)
                
                # Create metadata markdown file
                metadata_filename = f"{os.path.splitext(filename)[0]}_metadata.md"
                metadata_path = os.path.join(self.needs_action_dir, metadata_filename)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                with open(metadata_path, 'w') as meta_file:
                    meta_file.write(f"# Metadata for {filename}\n\n")
                    meta_file.write(f"- Original filename: {filename}\n")
                    meta_file.write(f"- Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    meta_file.write(f"- Size: {file_size} bytes\n")
                    
                print(f"Copied {filename} to Needs_Action and created metadata")
                    
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

def main():
    # Use relative paths from the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = script_dir  # Assuming project root is where script runs
    
    drop_dir = os.path.join(base_dir, 'Drop')
    needs_action_dir = os.path.join(base_dir, 'Needs_Action')
    
    # Ensure directories exist
    os.makedirs(drop_dir, exist_ok=True)
    os.makedirs(needs_action_dir, exist_ok=True)
    
    event_handler = FileHandler(drop_dir, needs_action_dir)
    observer = Observer()
    observer.schedule(event_handler, drop_dir, recursive=False)
    
    observer.start()
    print("Filesystem watcher started, monitoring Drop/ folder...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nFilesystem watcher stopped.")
    
    observer.join()

if __name__ == "__main__":
    main()