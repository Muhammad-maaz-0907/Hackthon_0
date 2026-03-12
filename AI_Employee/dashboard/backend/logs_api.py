"""
Logs API - Read and manage system logs
Endpoints to retrieve logs from the Logs folder
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter()

# Base directory for AI Employee
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to AI_Employee folder
LOGS_DIR = BASE_DIR / "Logs"


class LogEntry(BaseModel):
    """Model for a single log entry"""
    timestamp: Optional[str] = None
    level: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class LogFile(BaseModel):
    """Model for log file info"""
    filename: str
    path: str
    size: int
    modified: str
    entries: Optional[int] = None


class LogsResponse(BaseModel):
    """Response model for logs endpoint"""
    status: str
    logs_directory: str
    files: List[LogFile]
    total_files: int


class LogContentResponse(BaseModel):
    """Response model for log content"""
    status: str
    filename: str
    content: Any
    line_count: int
    size: int


@router.get("/", response_model=LogsResponse)
async def get_logs():
    """Get list of all log files"""
    LOGS_DIR.mkdir(exist_ok=True)
    
    files = []
    
    # Get all JSON and log files
    for ext in ["*.json", "*.log", "*.txt"]:
        for file_path in LOGS_DIR.glob(ext):
            try:
                stat = file_path.stat()
                files.append(LogFile(
                    filename=file_path.name,
                    path=str(file_path),
                    size=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    entries=_count_log_entries(file_path)
                ))
            except Exception:
                continue
    
    # Sort by modified time (newest first)
    files.sort(key=lambda x: x.modified, reverse=True)
    
    return LogsResponse(
        status="success",
        logs_directory=str(LOGS_DIR),
        files=files,
        total_files=len(files)
    )


@router.get("/whatsapp-logs", response_model=LogContentResponse)
async def get_whatsapp_logs(limit: Optional[int] = 100):
    """Get WhatsApp-related logs"""
    whatsapp_logs = []
    
    # Find WhatsApp-related log files
    for file_path in LOGS_DIR.glob("*whatsapp*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                whatsapp_logs.append({
                    "file": file_path.name,
                    "data": data
                })
        except Exception:
            continue
    
    # Also check for general logs mentioning WhatsApp
    for file_path in LOGS_DIR.glob("*.json"):
        if file_path.name not in [f["file"] for f in whatsapp_logs]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "whatsapp" in content.lower():
                        data = json.loads(content)
                        whatsapp_logs.append({
                            "file": file_path.name,
                            "data": data
                        })
            except Exception:
                continue
    
    # Limit entries
    limited_logs = []
    for log in whatsapp_logs:
        if isinstance(log["data"], dict):
            if "messages" in log["data"]:
                log["data"]["messages"] = log["data"]["messages"][:limit]
            if "posts" in log["data"]:
                log["data"]["posts"] = log["data"]["posts"][:limit]
        limited_logs.append(log)
    
    # Calculate total size
    total_size = sum(
        LOGS_DIR.glob(f"*{log['file']}").__next__().stat().st_size
        for log in limited_logs
        if any(LOGS_DIR.glob(f"*{log['file']}"))
    ) if limited_logs else 0
    
    return LogContentResponse(
        status="success",
        filename="whatsapp_logs",
        content={"logs": limited_logs},
        line_count=len(limited_logs),
        size=total_size
    )


@router.get("/email-logs", response_model=LogContentResponse)
async def get_email_logs(limit: Optional[int] = 100):
    """Get Email-related logs"""
    email_logs = []
    
    # Find email-related log files
    for file_path in LOGS_DIR.glob("*email*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                email_logs.append({
                    "file": file_path.name,
                    "data": data
                })
        except Exception:
            continue
    
    # Find Gmail logs
    for file_path in LOGS_DIR.glob("*gmail*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                email_logs.append({
                    "file": file_path.name,
                    "data": data
                })
        except Exception:
            continue
    
    # Limit entries
    for log in email_logs:
        if isinstance(log["data"], dict):
            if "emails" in log["data"]:
                log["data"]["emails"] = log["data"]["emails"][:limit]
            if "messages" in log["data"]:
                log["data"]["messages"] = log["data"]["messages"][:limit]
    
    # Calculate total size
    total_size = sum(
        LOGS_DIR.glob(f"*{log['file']}").__next__().stat().st_size
        for log in email_logs
        if any(LOGS_DIR.glob(f"*{log['file']}"))
    ) if email_logs else 0
    
    return LogContentResponse(
        status="success",
        filename="email_logs",
        content={"logs": email_logs},
        line_count=len(email_logs),
        size=total_size
    )


@router.get("/{filename}", response_model=LogContentResponse)
async def get_log_file(filename: str, lines: Optional[int] = 50):
    """Get content of a specific log file"""
    file_path = LOGS_DIR / filename
    
    if not file_path.exists():
        # Try without extension
        file_path = LOGS_DIR / f"{filename}.json"
        if not file_path.exists():
            file_path = LOGS_DIR / f"{filename}.log"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail=f"Log file not found: {filename}")
    
    try:
        stat = file_path.stat()
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as JSON
        try:
            json_content = json.loads(content)
            
            # Limit array entries if present
            if isinstance(json_content, dict):
                for key in json_content:
                    if isinstance(json_content[key], list):
                        json_content[key] = json_content[key][:lines]
            
            parsed_content = json_content
            line_count = len(str(json_content).split('\n'))
        except json.JSONDecodeError:
            # Not JSON, return as text
            text_lines = content.split('\n')
            parsed_content = text_lines[-lines:] if len(text_lines) > lines else text_lines
            line_count = len(text_lines)
        
        return LogContentResponse(
            status="success",
            filename=filename,
            content=parsed_content,
            line_count=line_count,
            size=stat.st_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")


@router.get("/recent/{count}")
async def get_recent_logs(count: int = 10):
    """Get most recent log entries across all log files"""
    recent_entries = []
    
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Scan all JSON log files
    for file_path in LOGS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract entries based on common structures
                entries = []
                if isinstance(data, dict):
                    if "messages" in data:
                        entries = data["messages"]
                    elif "posts" in data:
                        entries = data["posts"]
                    elif "tasks" in data:
                        entries = data["tasks"]
                    elif "errors" in data:
                        entries = data["errors"]
                
                for entry in entries[:5]:  # Take up to 5 from each file
                    entry_with_source = entry.copy() if isinstance(entry, dict) else {"data": entry}
                    entry_with_source["_source"] = file_path.name
                    recent_entries.append(entry_with_source)
                    
        except Exception:
            continue
    
    # Sort by timestamp if available
    recent_entries.sort(
        key=lambda x: x.get("timestamp", x.get("time", x.get("date", ""))),
        reverse=True
    )
    
    return {
        "status": "success",
        "count": min(count, len(recent_entries)),
        "entries": recent_entries[:count]
    }


@router.get("/search/{keyword}")
async def search_logs(keyword: str):
    """Search logs for a keyword"""
    results = []
    
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Search all JSON log files
    for file_path in LOGS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if keyword.lower() in content.lower():
                    data = json.loads(content)
                    results.append({
                        "file": file_path.name,
                        "matches": _find_matches(data, keyword),
                        "path": str(file_path)
                    })
        except Exception:
            continue
    
    return {
        "status": "success",
        "keyword": keyword,
        "results": results
    }


@router.delete("/{filename}")
async def delete_log_file(filename: str):
    """Delete a specific log file"""
    file_path = LOGS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Log file not found: {filename}")
    
    try:
        file_path.unlink()
        return {
            "status": "success",
            "message": f"Deleted log file: {filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting log file: {str(e)}")


@router.post("/clear")
async def clear_logs(pattern: Optional[str] = None):
    """Clear log files matching pattern"""
    deleted = []
    
    LOGS_DIR.mkdir(exist_ok=True)
    
    if pattern:
        files_to_delete = list(LOGS_DIR.glob(f"*{pattern}*"))
    else:
        files_to_delete = list(LOGS_DIR.glob("*.json")) + list(LOGS_DIR.glob("*.log"))
    
    for file_path in files_to_delete:
        try:
            file_path.unlink()
            deleted.append(file_path.name)
        except Exception:
            continue
    
    return {
        "status": "success",
        "message": f"Cleared {len(deleted)} log files",
        "deleted": deleted
    }


def _count_log_entries(file_path: Path) -> Optional[int]:
    """Count entries in a log file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if isinstance(data, dict):
                # Return the length of the first list found
                for value in data.values():
                    if isinstance(value, list):
                        return len(value)
            elif isinstance(data, list):
                return len(data)
    except Exception:
        pass
    
    return None


def _find_matches(data: Any, keyword: str, max_matches: int = 10) -> List[Dict]:
    """Find matches for keyword in data"""
    matches = []
    keyword_lower = keyword.lower()
    
    def search_recursive(obj: Any, path: str = ""):
        if len(matches) >= max_matches:
            return
            
        if isinstance(obj, dict):
            for key, value in obj.items():
                search_recursive(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                search_recursive(item, f"{path}[{i}]")
        elif isinstance(obj, str):
            if keyword_lower in obj.lower():
                matches.append({
                    "path": path,
                    "value": obj[:200]  # Limit value length
                })
    
    search_recursive(data)
    return matches
