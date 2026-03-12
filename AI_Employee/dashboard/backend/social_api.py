"""
Social Media API - Manage LinkedIn, Twitter, and Facebook posting
Endpoints to trigger social media posting scripts
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter()

# Base directory for AI Employee scripts
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to AI_Employee folder

# Social poster script paths
SOCIAL_SCRIPTS = {
    "linkedin": BASE_DIR / "Social" / "linkedin_poster.py",
    "twitter": BASE_DIR / "Social" / "x_poster.py",
    "facebook": BASE_DIR / "Social" / "facebook_poster.py",
    "instagram": BASE_DIR / "Social" / "instagram_poster.py",
}

# Logs directory
LOGS_DIR = BASE_DIR / "Logs"


class SocialPostRequest(BaseModel):
    """Request model for social media posts"""
    content: str
    platform: Optional[str] = None
    image_path: Optional[str] = None
    schedule_time: Optional[str] = None
    hashtags: Optional[list[str]] = None


class SocialPostResponse(BaseModel):
    """Response model for social media posts"""
    status: str
    platform: str
    message: str
    post_id: Optional[str] = None
    scheduled: bool = False
    timestamp: str


class ScheduledPost(BaseModel):
    """Model for scheduled posts"""
    platform: str
    content: str
    scheduled_time: str
    status: str


@router.post("/post-linkedin", response_model=SocialPostResponse)
async def post_to_linkedin(request: SocialPostRequest):
    """Post content to LinkedIn"""
    script_path = SOCIAL_SCRIPTS["linkedin"]
    
    try:
        # Prepare post data
        post_data = {
            "content": request.content,
            "hashtags": request.hashtags or [],
            "image_path": request.image_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if script exists
        if script_path.exists():
            # Run the LinkedIn poster script
            process = subprocess.run(
                ["python", str(script_path)],
                cwd=str(BASE_DIR),
                input=json.dumps(post_data),
                text=True,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Log the post
            _log_social_post("linkedin", post_data, "success")
            
            return SocialPostResponse(
                status="success",
                platform="linkedin",
                message="LinkedIn post created successfully",
                post_id=f"li_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
        else:
            # Script doesn't exist, log the post anyway
            _log_social_post("linkedin", post_data, "simulated")
            
            return SocialPostResponse(
                status="simulated",
                platform="linkedin",
                message="LinkedIn post logged (script not found)",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="LinkedIn posting timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to LinkedIn: {str(e)}")


@router.post("/post-twitter", response_model=SocialPostResponse)
async def post_to_twitter(request: SocialPostRequest):
    """Post content to Twitter/X"""
    script_path = SOCIAL_SCRIPTS["twitter"]
    
    try:
        # Prepare post data
        post_data = {
            "content": request.content,
            "hashtags": request.hashtags or [],
            "image_path": request.image_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if script exists
        if script_path.exists():
            # Run the Twitter poster script
            process = subprocess.run(
                ["python", str(script_path)],
                cwd=str(BASE_DIR),
                input=json.dumps(post_data),
                text=True,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Log the post
            _log_social_post("twitter", post_data, "success")
            
            return SocialPostResponse(
                status="success",
                platform="twitter",
                message="Twitter/X post created successfully",
                post_id=f"tw_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
        else:
            # Script doesn't exist, log the post anyway
            _log_social_post("twitter", post_data, "simulated")
            
            return SocialPostResponse(
                status="simulated",
                platform="twitter",
                message="Twitter/X post logged (script not found)",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Twitter posting timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Twitter: {str(e)}")


@router.post("/post-facebook", response_model=SocialPostResponse)
async def post_to_facebook(request: SocialPostRequest):
    """Post content to Facebook"""
    script_path = SOCIAL_SCRIPTS["facebook"]
    
    try:
        # Prepare post data
        post_data = {
            "content": request.content,
            "hashtags": request.hashtags or [],
            "image_path": request.image_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if script exists
        if script_path.exists():
            # Run the Facebook poster script
            process = subprocess.run(
                ["python", str(script_path)],
                cwd=str(BASE_DIR),
                input=json.dumps(post_data),
                text=True,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Log the post
            _log_social_post("facebook", post_data, "success")
            
            return SocialPostResponse(
                status="success",
                platform="facebook",
                message="Facebook post created successfully",
                post_id=f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
        else:
            # Script doesn't exist, log the post anyway
            _log_social_post("facebook", post_data, "simulated")
            
            return SocialPostResponse(
                status="simulated",
                platform="facebook",
                message="Facebook post logged (script not found)",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Facebook posting timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Facebook: {str(e)}")


@router.post("/post-instagram", response_model=SocialPostResponse)
async def post_to_instagram(request: SocialPostRequest):
    """Post content to Instagram"""
    script_path = SOCIAL_SCRIPTS["instagram"]
    
    try:
        # Prepare post data
        post_data = {
            "content": request.content,
            "hashtags": request.hashtags or [],
            "image_path": request.image_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if script exists
        if script_path.exists():
            # Run the Instagram poster script
            process = subprocess.run(
                ["python", str(script_path)],
                cwd=str(BASE_DIR),
                input=json.dumps(post_data),
                text=True,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Log the post
            _log_social_post("instagram", post_data, "success")
            
            return SocialPostResponse(
                status="success",
                platform="instagram",
                message="Instagram post created successfully",
                post_id=f"ig_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
        else:
            # Script doesn't exist, log the post anyway
            _log_social_post("instagram", post_data, "simulated")
            
            return SocialPostResponse(
                status="simulated",
                platform="instagram",
                message="Instagram post logged (script not found)",
                scheduled=False,
                timestamp=datetime.now().isoformat()
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Instagram posting timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Instagram: {str(e)}")


@router.get("/scheduled", response_model=list[ScheduledPost])
async def get_scheduled_posts():
    """Get all scheduled posts"""
    scheduled_file = LOGS_DIR / "scheduled_posts.json"
    
    if not scheduled_file.exists():
        return []
    
    try:
        with open(scheduled_file, 'r') as f:
            data = json.load(f)
            return [
                ScheduledPost(
                    platform=post.get("platform", "unknown"),
                    content=post.get("content", ""),
                    scheduled_time=post.get("scheduled_time", ""),
                    status=post.get("status", "pending")
                )
                for post in data.get("posts", [])
            ]
    except Exception:
        return []


@router.get("/stats")
async def get_social_stats():
    """Get social media posting statistics"""
    social_log = LOGS_DIR / "social.json"
    
    if not social_log.exists():
        return {
            "total_posts": 0,
            "platforms": {}
        }
    
    try:
        with open(social_log, 'r') as f:
            data = json.load(f)
            
        posts = data.get("posts", [])
        platform_stats = {}
        
        for post in posts:
            platform = post.get("platform", "unknown")
            if platform not in platform_stats:
                platform_stats[platform] = {"count": 0, "success": 0, "failed": 0}
            
            platform_stats[platform]["count"] += 1
            if post.get("status") == "success":
                platform_stats[platform]["success"] += 1
            else:
                platform_stats[platform]["failed"] += 1
        
        return {
            "total_posts": len(posts),
            "platforms": platform_stats
        }
    except Exception:
        return {
            "total_posts": 0,
            "platforms": {}
        }


def _log_social_post(platform: str, post_data: Dict[str, Any], status: str):
    """Log social media post to JSON file"""
    LOGS_DIR.mkdir(exist_ok=True)
    social_log = LOGS_DIR / "social.json"
    
    try:
        if social_log.exists():
            with open(social_log, 'r') as f:
                data = json.load(f)
        else:
            data = {"posts": []}
        
        data["posts"].append({
            "platform": platform,
            "content": post_data.get("content", ""),
            "hashtags": post_data.get("hashtags", []),
            "status": status,
            "timestamp": post_data.get("timestamp", datetime.now().isoformat())
        })
        
        with open(social_log, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass  # Silently fail on logging errors
