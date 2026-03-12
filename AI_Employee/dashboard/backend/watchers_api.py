"""
Watchers API - Manage Gmail, WhatsApp, and Instagram watchers
Endpoints to start/stop existing automation scripts
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path
from typing import Dict, Optional

router = APIRouter()

# Store for running processes
running_processes: Dict[str, subprocess.Popen] = {}

# Base directory for AI Employee scripts
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to AI_Employee folder

# Script paths
SCRIPTS = {
    "gmail": BASE_DIR / "Integrations" / "Gmail" / "gmail_watcher.py",
    "whatsapp": BASE_DIR / "Integrations" / "WhatsApp" / "whatsapp_watcher.py",
    "instagram": BASE_DIR / "Integrations" / "Instagram" / "instagram_watcher.py",
    "linkedin": BASE_DIR / "Integrations" / "LinkedIn" / "linkedin_scheduler.py",
}


class WatcherStatus(BaseModel):
    """Response model for watcher status"""
    watcher: str
    status: str
    pid: Optional[int] = None
    message: str


class StartWatcherRequest(BaseModel):
    """Request model for starting watchers"""
    watcher: str
    auto_restart: bool = False


class StopWatcherRequest(BaseModel):
    """Request model for stopping watchers"""
    watcher: str


@router.get("/status", response_model=Dict[str, WatcherStatus])
async def get_watchers_status():
    """Get status of all watchers"""
    status = {}
    
    for name, script_path in SCRIPTS.items():
        is_running = name in running_processes and running_processes[name].poll() is None
        
        status[name] = WatcherStatus(
            watcher=name,
            status="running" if is_running else "stopped",
            pid=running_processes[name].pid if is_running else None,
            message=f"{name.capitalize()} watcher is {'running' if is_running else 'stopped'}"
        )
    
    return status


@router.post("/start-gmail", response_model=WatcherStatus)
async def start_gmail_watcher():
    """Start Gmail watcher"""
    script_path = SCRIPTS["gmail"]
    
    if not script_path.exists():
        raise HTTPException(status_code=404, detail=f"Gmail watcher script not found: {script_path}")
    
    # Check if already running
    if "gmail" in running_processes and running_processes["gmail"].poll() is None:
        return WatcherStatus(
            watcher="gmail",
            status="running",
            pid=running_processes["gmail"].pid,
            message="Gmail watcher is already running"
        )
    
    try:
        # Start the script using subprocess
        process = subprocess.Popen(
            ["python", str(script_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        running_processes["gmail"] = process
        
        return WatcherStatus(
            watcher="gmail",
            status="started",
            pid=process.pid,
            message="Gmail watcher started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Gmail watcher: {str(e)}")


@router.post("/start-whatsapp", response_model=WatcherStatus)
async def start_whatsapp_watcher():
    """Start WhatsApp watcher"""
    script_path = SCRIPTS["whatsapp"]
    
    if not script_path.exists():
        raise HTTPException(status_code=404, detail=f"WhatsApp watcher script not found: {script_path}")
    
    # Check if already running
    if "whatsapp" in running_processes and running_processes["whatsapp"].poll() is None:
        return WatcherStatus(
            watcher="whatsapp",
            status="running",
            pid=running_processes["whatsapp"].pid,
            message="WhatsApp watcher is already running"
        )
    
    try:
        # Start the script using subprocess
        process = subprocess.Popen(
            ["python", str(script_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        running_processes["whatsapp"] = process
        
        return WatcherStatus(
            watcher="whatsapp",
            status="started",
            pid=process.pid,
            message="WhatsApp watcher started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start WhatsApp watcher: {str(e)}")


@router.post("/start-instagram", response_model=WatcherStatus)
async def start_instagram_watcher():
    """Start Instagram watcher"""
    script_path = SCRIPTS["instagram"]
    
    if not script_path.exists():
        raise HTTPException(status_code=404, detail=f"Instagram watcher script not found: {script_path}")
    
    # Check if already running
    if "instagram" in running_processes and running_processes["instagram"].poll() is None:
        return WatcherStatus(
            watcher="instagram",
            status="running",
            pid=running_processes["instagram"].pid,
            message="Instagram watcher is already running"
        )
    
    try:
        # Start the script using subprocess
        process = subprocess.Popen(
            ["python", str(script_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        running_processes["instagram"] = process
        
        return WatcherStatus(
            watcher="instagram",
            status="started",
            pid=process.pid,
            message="Instagram watcher started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Instagram watcher: {str(e)}")


@router.post("/start-linkedin", response_model=WatcherStatus)
async def start_linkedin_scheduler():
    """Start LinkedIn scheduler"""
    script_path = SCRIPTS["linkedin"]
    
    if not script_path.exists():
        raise HTTPException(status_code=404, detail=f"LinkedIn scheduler script not found: {script_path}")
    
    # Check if already running
    if "linkedin" in running_processes and running_processes["linkedin"].poll() is None:
        return WatcherStatus(
            watcher="linkedin",
            status="running",
            pid=running_processes["linkedin"].pid,
            message="LinkedIn scheduler is already running"
        )
    
    try:
        # Start the script using subprocess
        process = subprocess.Popen(
            ["python", str(script_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        running_processes["linkedin"] = process
        
        return WatcherStatus(
            watcher="linkedin",
            status="started",
            pid=process.pid,
            message="LinkedIn scheduler started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start LinkedIn scheduler: {str(e)}")


@router.post("/stop-watchers", response_model=Dict[str, str])
async def stop_watchers(request: Optional[StopWatcherRequest] = None):
    """Stop one or all watchers"""
    stopped = []
    
    if request and request.watcher:
        # Stop specific watcher
        watchers_to_stop = [request.watcher]
    else:
        # Stop all watchers
        watchers_to_stop = list(running_processes.keys())
    
    for watcher_name in watchers_to_stop:
        if watcher_name in running_processes:
            process = running_processes[watcher_name]
            
            if process.poll() is None:  # Still running
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    stopped.append(watcher_name)
                    del running_processes[watcher_name]
                except subprocess.TimeoutExpired:
                    process.kill()
                    stopped.append(watcher_name)
                    del running_processes[watcher_name]
                except Exception:
                    pass
    
    return {
        "status": "success",
        "message": f"Stopped watchers: {', '.join(stopped) if stopped else 'none'}",
        "stopped": stopped
    }


@router.post("/stop/{watcher_name}", response_model=WatcherStatus)
async def stop_watcher(watcher_name: str):
    """Stop a specific watcher"""
    if watcher_name not in running_processes:
        raise HTTPException(status_code=400, detail=f"Watcher '{watcher_name}' is not running")
    
    process = running_processes[watcher_name]
    
    if process.poll() is None:  # Still running
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    pid = process.pid
    del running_processes[watcher_name]
    
    return WatcherStatus(
        watcher=watcher_name,
        status="stopped",
        pid=pid,
        message=f"{watcher_name.capitalize()} watcher stopped successfully"
    )


@router.get("/logs/{watcher_name}")
async def get_watcher_logs(watcher_name: str):
    """Get logs for a specific watcher"""
    if watcher_name not in SCRIPTS:
        raise HTTPException(status_code=404, detail=f"Unknown watcher: {watcher_name}")
    
    # Look for log files in the Logs directory
    logs_dir = BASE_DIR / "Logs"
    log_files = []
    
    if logs_dir.exists():
        for file in logs_dir.glob(f"*{watcher_name}*.json"):
            log_files.append(file.name)
        for file in logs_dir.glob(f"*{watcher_name}*.log"):
            log_files.append(file.name)
    
    return {
        "watcher": watcher_name,
        "log_files": log_files,
        "logs_directory": str(logs_dir)
    }
