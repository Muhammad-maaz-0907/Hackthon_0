"""
WhatsApp Messaging API - Send WhatsApp messages
Endpoint to send WhatsApp messages via existing automation
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


class WhatsAppMessageRequest(BaseModel):
    """Request model for sending WhatsApp messages"""
    phone: str
    message: str
    country_code: str = "+1"


class WhatsAppMessageResponse(BaseModel):
    """Response model for WhatsApp messages"""
    status: str
    message: str
    phone: str
    timestamp: str
    simulated: bool = False


@router.post("/send-whatsapp", response_model=WhatsAppMessageResponse)
async def send_whatsapp_message(request: WhatsAppMessageRequest):
    """Send a WhatsApp message to a contact"""
    
    try:
        # Format phone number
        phone = f"{request.country_code}{request.phone}"
        
        # Create a task file for the WhatsApp sender
        tasks_dir = BASE_DIR / "Needs_Action"
        tasks_dir.mkdir(exist_ok=True)
        
        # Generate task filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = tasks_dir / f"WhatsApp_Message_{timestamp}.md"
        
        # Create task markdown file
        task_content = f"""# Task: Send WhatsApp Message

**Priority:** High
**Type:** WhatsApp Outbound
**Phone:** {phone}
**Message:** {request.message}
**Timestamp:** {datetime.now().isoformat()}

## Instructions
Send the above message to the specified phone number via WhatsApp.
"""
        
        # Write task file
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task_content)
        
        # Log the message
        _log_whatsapp_message(phone, request.message, "pending")
        
        # Try to send via WhatsApp Web automation if available
        whatsapp_script = BASE_DIR / "Integrations" / "WhatsApp" / "whatsapp_sender.py"
        
        if whatsapp_script.exists():
            # Run the WhatsApp sender script
            try:
                process = subprocess.run(
                    ["python", str(whatsapp_script), phone, request.message],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                if process.returncode == 0:
                    _log_whatsapp_message(phone, request.message, "sent")
                    return WhatsAppMessageResponse(
                        status="success",
                        message=f"WhatsApp message sent to {phone}",
                        phone=phone,
                        timestamp=datetime.now().isoformat(),
                        simulated=False
                    )
            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass
        
        # If script doesn't exist or fails, log as simulated
        _log_whatsapp_message(phone, request.message, "queued")
        
        return WhatsAppMessageResponse(
            status="queued",
            message=f"Message queued for {phone}. Task created in Needs_Action folder.",
            phone=phone,
            timestamp=datetime.now().isoformat(),
            simulated=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp message: {str(e)}")


@router.get("/send-whatsapp")
async def send_whatsapp_get(phone: str, message: str, country_code: Optional[str] = "+1"):
    """Send WhatsApp message via GET request (for testing)"""
    return await send_whatsapp_message(
        WhatsAppMessageRequest(phone=phone, message=message, country_code=country_code)
    )


@router.get("/messages")
async def get_whatsapp_messages(limit: int = 50):
    """Get recent WhatsApp messages from logs"""
    messages_log = LOGS_DIR / "whatsapp_messages.json"
    
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


def _log_whatsapp_message(phone: str, message: str, status: str):
    """Log WhatsApp message to JSON file"""
    LOGS_DIR.mkdir(exist_ok=True)
    messages_log = LOGS_DIR / "whatsapp_messages.json"
    
    try:
        if messages_log.exists():
            with open(messages_log, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"messages": []}
        
        data["messages"].append({
            "phone": phone,
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(messages_log, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Silently fail on logging errors
