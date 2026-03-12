"""
Instagram Messaging API - Send Instagram DMs
Endpoint to send Instagram direct messages via automation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

router = APIRouter()

# Base directory for AI Employee scripts
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to AI_Employee folder
LOGS_DIR = BASE_DIR / "Logs"


class InstagramDMRequest(BaseModel):
    """Request model for sending Instagram DMs"""
    username: str
    message: str


class InstagramDMResponse(BaseModel):
    """Response model for Instagram DMs"""
    status: str
    message: str
    username: str
    timestamp: str
    simulated: bool = False


@router.post("/send-dm", response_model=InstagramDMResponse)
async def send_instagram_dm(request: InstagramDMRequest):
    """Send an Instagram direct message"""
    
    try:
        # Create a task file for the Instagram sender
        tasks_dir = BASE_DIR / "Needs_Action"
        tasks_dir.mkdir(exist_ok=True)
        
        # Generate task filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = tasks_dir / f"Instagram_DM_{timestamp}.md"
        
        # Create task markdown file
        task_content = f"""# Task: Send Instagram DM

**Priority:** High
**Type:** Instagram Direct Message
**Username:** {request.username}
**Message:** {request.message}
**Timestamp:** {datetime.now().isoformat()}

## Instructions
Send the above message to @{request.username} via Instagram Direct Message.
"""
        
        # Write task file
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task_content)
        
        # Try to send via Instagram automation
        instagram_script = BASE_DIR / "Integrations" / "Instagram" / "instagram_sender.py"
        
        if instagram_script.exists():
            # Run the Instagram sender script
            try:
                process = subprocess.run(
                    ["python", str(instagram_script), request.username, request.message],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                if process.returncode == 0:
                    _log_instagram_dm(request.username, request.message, "sent")
                    return InstagramDMResponse(
                        status="success",
                        message=f"Instagram DM sent to @{request.username}",
                        username=request.username,
                        timestamp=datetime.now().isoformat(),
                        simulated=False
                    )
            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass
        
        # If script doesn't exist or fails, log as queued
        _log_instagram_dm(request.username, request.message, "queued")
        
        return InstagramDMResponse(
            status="queued",
            message=f"DM queued for @{request.username}. Task created in Needs_Action folder.",
            username=request.username,
            timestamp=datetime.now().isoformat(),
            simulated=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Instagram DM: {str(e)}")


@router.get("/send-dm")
async def send_instagram_dm_get(username: str, message: str):
    """Send Instagram DM via GET request (for testing)"""
    return await send_instagram_dm(InstagramDMRequest(username=username, message=message))


@router.get("/messages")
async def get_instagram_messages(limit: int = 50):
    """Get recent Instagram DMs from logs"""
    messages_log = LOGS_DIR / "instagram_dms.json"
    
    if not messages_log.exists():
        return {"messages": [], "total": 0}
    
    try:
        with open(messages_log, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get("messages", [])
        
        # Return most recent first, limited
        recent = messages[-limit:][::-1]
        
        return {
            "messages": recent,
            "total": len(messages)
        }
    except Exception:
        return {"messages": [], "total": 0}


def _log_instagram_dm(username: str, message: str, status: str):
    """Log Instagram DM to JSON file"""
    LOGS_DIR.mkdir(exist_ok=True)
    messages_log = LOGS_DIR / "instagram_dms.json"
    
    try:
        if messages_log.exists():
            with open(messages_log, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"messages": []}
        
        data["messages"].append({
            "username": username,
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(messages_log, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Silently fail on logging errors
