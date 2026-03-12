"""
Email/Gmail Messaging API - Send emails via Gmail
Endpoint to send emails using existing Gmail integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

router = APIRouter()

# Base directory for AI Employee scripts
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to AI_Employee folder
LOGS_DIR = BASE_DIR / "Logs"


class EmailRequest(BaseModel):
    """Request model for sending emails"""
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    attachments: Optional[List[str]] = None


class EmailResponse(BaseModel):
    """Response model for sending emails"""
    status: str
    message: str
    to: str
    subject: str
    timestamp: str
    simulated: bool = False


@router.post("/send-email", response_model=EmailResponse)
async def send_email(request: EmailRequest):
    """Send an email via Gmail"""
    
    try:
        # Create a task file for the email sender
        tasks_dir = BASE_DIR / "Needs_Action"
        tasks_dir.mkdir(exist_ok=True)
        
        # Generate task filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = tasks_dir / f"Email_{timestamp}.md"
        
        # Create task markdown file
        task_content = f"""# Task: Send Email

**Priority:** High
**Type:** Email Outbound
**To:** {request.to}
**Subject:** {request.subject}
**CC:** {request.cc or 'None'}
**BCC:** {request.bcc or 'None'}
**Timestamp:** {datetime.now().isoformat()}

## Message Body
{request.body}

## Instructions
Send the above email to the specified recipient via Gmail.
"""
        
        # Write task file
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task_content)
        
        # Try to send via existing Gmail integration
        gmail_script = BASE_DIR / "Integrations" / "Gmail" / "send_email.py"
        
        if gmail_script.exists():
            # Run the Gmail sender script
            try:
                process = subprocess.run(
                    ["python", str(gmail_script), request.to, request.subject, request.body],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                if process.returncode == 0:
                    _log_email(request.to, request.subject, request.body, "sent")
                    return EmailResponse(
                        status="success",
                        message=f"Email sent to {request.to}",
                        to=request.to,
                        subject=request.subject,
                        timestamp=datetime.now().isoformat(),
                        simulated=False
                    )
            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass
        
        # If script doesn't exist or fails, log as queued
        _log_email(request.to, request.subject, request.body, "queued")
        
        return EmailResponse(
            status="queued",
            message=f"Email queued for {request.to}. Task created in Needs_Action folder.",
            to=request.to,
            subject=request.subject,
            timestamp=datetime.now().isoformat(),
            simulated=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.get("/send-email")
async def send_email_get(to: str, subject: str, body: str):
    """Send email via GET request (for testing)"""
    return await send_email(EmailRequest(to=to, subject=subject, body=body))


@router.get("/sent")
async def get_sent_emails(limit: int = 50):
    """Get recent sent emails from logs"""
    emails_log = LOGS_DIR / "sent_emails.json"
    
    if not emails_log.exists():
        return {"emails": [], "total": 0}
    
    try:
        with open(emails_log, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        emails = data.get("emails", [])
        
        # Return most recent first, limited
        recent = emails[-limit:][::-1]
        
        return {
            "emails": recent,
            "total": len(emails)
        }
    except Exception:
        return {"emails": [], "total": 0}


def _log_email(to: str, subject: str, body: str, status: str):
    """Log sent email to JSON file"""
    LOGS_DIR.mkdir(exist_ok=True)
    emails_log = LOGS_DIR / "sent_emails.json"
    
    try:
        if emails_log.exists():
            with open(emails_log, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"emails": []}
        
        data["emails"].append({
            "to": to,
            "subject": subject,
            "body": body[:200] + "..." if len(body) > 200 else body,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(emails_log, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Silently fail on logging errors
