"""
AI Generation API - Generate text, posts, and replies
Endpoints for AI-powered content generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import random

router = APIRouter()


class TextGenerationRequest(BaseModel):
    """Request model for text generation"""
    prompt: str
    tone: Optional[str] = "professional"
    max_length: Optional[int] = 500
    context: Optional[str] = None


class TextGenerationResponse(BaseModel):
    """Response model for text generation"""
    status: str
    generated_text: str
    tone: str
    length: int
    timestamp: str


class PostGenerationRequest(BaseModel):
    """Request model for social media post generation"""
    topic: str
    platform: str
    tone: Optional[str] = "engaging"
    include_hashtags: bool = True
    key_points: Optional[List[str]] = None


class PostGenerationResponse(BaseModel):
    """Response model for post generation"""
    status: str
    platform: str
    content: str
    hashtags: List[str]
    character_count: int
    timestamp: str


class ReplyGenerationRequest(BaseModel):
    """Request model for reply generation"""
    original_message: str
    context: Optional[str] = None
    tone: Optional[str] = "helpful"
    platform: Optional[str] = "email"


class ReplyGenerationResponse(BaseModel):
    """Response model for reply generation"""
    status: str
    reply: str
    tone: str
    platform: str
    timestamp: str


# Tone templates for generation
TONE_TEMPLATES = {
    "professional": {
        "greeting": "Dear valued stakeholder,",
        "closing": "Best regards",
        "style": "formal and courteous"
    },
    "friendly": {
        "greeting": "Hi there!",
        "closing": "Warm regards",
        "style": "warm and approachable"
    },
    "engaging": {
        "greeting": "Hey everyone!",
        "closing": "Let's connect!",
        "style": "energetic and interactive"
    },
    "helpful": {
        "greeting": "Hello!",
        "closing": "Happy to help",
        "style": "supportive and informative"
    },
    "enthusiastic": {
        "greeting": "Great news!",
        "closing": "Excited to share",
        "style": "positive and energetic"
    }
}


@router.post("/generate-text", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """Generate text based on a prompt"""
    try:
        tone = request.tone.lower() if request.tone else "professional"
        tone_info = TONE_TEMPLATES.get(tone, TONE_TEMPLATES["professional"])
        
        # Generate contextual text based on prompt
        generated = _generate_contextual_text(
            prompt=request.prompt,
            tone=tone_info,
            context=request.context,
            max_length=request.max_length
        )
        
        return TextGenerationResponse(
            status="success",
            generated_text=generated,
            tone=tone,
            length=len(generated),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")


@router.post("/generate-post", response_model=PostGenerationResponse)
async def generate_post(request: PostGenerationRequest):
    """Generate social media post content"""
    try:
        platform = request.platform.lower()
        tone = request.tone.lower() if request.tone else "engaging"
        tone_info = TONE_TEMPLATES.get(tone, TONE_TEMPLATES["engaging"])
        
        # Generate platform-specific content
        content = _generate_platform_post(
            topic=request.topic,
            platform=platform,
            tone=tone_info,
            key_points=request.key_points
        )
        
        # Generate hashtags
        hashtags = _generate_hashtags(request.topic, platform) if request.include_hashtags else []
        
        return PostGenerationResponse(
            status="success",
            platform=platform,
            content=content,
            hashtags=hashtags,
            character_count=len(content),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post generation failed: {str(e)}")


@router.post("/generate-reply", response_model=ReplyGenerationResponse)
async def generate_reply(request: ReplyGenerationRequest):
    """Generate a reply to a message"""
    try:
        tone = request.tone.lower() if request.tone else "helpful"
        tone_info = TONE_TEMPLATES.get(tone, TONE_TEMPLATES["helpful"])
        platform = request.platform.lower() if request.platform else "email"
        
        # Generate contextual reply
        reply = _generate_reply_content(
            original_message=request.original_message,
            context=request.context,
            tone=tone_info,
            platform=platform
        )
        
        return ReplyGenerationResponse(
            status="success",
            reply=reply,
            tone=tone,
            platform=platform,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reply generation failed: {str(e)}")


@router.get("/tones")
async def get_available_tones():
    """Get available tone options"""
    return {
        "tones": list(TONE_TEMPLATES.keys()),
        "descriptions": {
            "professional": "Formal and business-appropriate",
            "friendly": "Warm and approachable",
            "engaging": "Energetic and interactive",
            "helpful": "Supportive and informative",
            "enthusiastic": "Positive and energetic"
        }
    }


@router.get("/platforms")
async def get_supported_platforms():
    """Get supported social media platforms"""
    return {
        "platforms": [
            "linkedin",
            "twitter",
            "facebook",
            "instagram"
        ],
        "character_limits": {
            "linkedin": 3000,
            "twitter": 280,
            "facebook": 63206,
            "instagram": 2200
        }
    }


def _generate_contextual_text(prompt: str, tone: dict, context: Optional[str], max_length: int) -> str:
    """Generate contextual text based on prompt and tone"""
    
    # Template-based generation
    templates = {
        "email": f"""{tone['greeting']}

Thank you for your message regarding {prompt}. 

{context if context else 'We appreciate your interest and would be happy to assist you further.'}

Our team is committed to providing you with the best possible service. Please don't hesitate to reach out if you have any additional questions or concerns.

{tone['closing']}""",
        
        "document": f"""# {prompt.title()}

## Overview
{context if context else 'This document provides comprehensive information about the subject.'}

## Key Points
- Detailed analysis and insights
- Actionable recommendations
- Next steps for implementation

## Conclusion
{tone['greeting']} We trust this information will be valuable for your needs.

{tone['closing']}""",
        
        "general": f"""{tone['greeting']}

{prompt}

{context if context else 'This response has been generated to address your inquiry with professionalism and care.'}

We remain at your disposal for any further assistance you may require.

{tone['closing']}"""
    }
    
    # Determine content type based on prompt
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["email", "message", "reply"]):
        content_type = "email"
    elif any(word in prompt_lower for word in ["document", "report", "guide"]):
        content_type = "document"
    else:
        content_type = "general"
    
    generated = templates.get(content_type, templates["general"])
    
    # Truncate if needed
    if len(generated) > max_length:
        generated = generated[:max_length-3] + "..."
    
    return generated


def _generate_platform_post(topic: str, platform: str, tone: dict, key_points: Optional[List[str]]) -> str:
    """Generate platform-specific social media post"""
    
    # Build key points section
    points_section = ""
    if key_points:
        points_section = "\n\n" + "\n".join(f"• {point}" for point in key_points[:5])
    
    templates = {
        "linkedin": f"""{tone['greeting']}

Excited to share insights on: {topic}
{points_section}

In today's professional landscape, staying informed and connected is more important than ever. Let's continue the conversation in the comments!

{tone['closing']}
#ProfessionalNetwork #Industry""",
        
        "twitter": f"""{tone['greeting']}

{topic} {points_section if points_section else ''}

Thoughts? Drop them below! 👇

#Engagement""",
        
        "facebook": f"""{tone['greeting']}

We're thrilled to discuss: {topic}
{points_section}

This is something we're passionate about, and we'd love to hear your perspectives. Share your thoughts in the comments!

{tone['closing']}""",
        
        "instagram": f"""{tone['greeting']}

✨ {topic} ✨
{points_section}

Double-tap if this resonates with you! 💫

#Inspiration #Motivation""",
        
        "default": f"""{tone['greeting']}

{topic}
{points_section}

{tone['closing']}"""
    }
    
    return templates.get(platform, templates["default"])


def _generate_hashtags(topic: str, platform: str) -> List[str]:
    """Generate relevant hashtags based on topic and platform"""
    
    # Extract keywords from topic
    keywords = topic.lower().split()[:5]
    
    # Platform-specific hashtag limits
    limits = {
        "linkedin": 5,
        "twitter": 3,
        "facebook": 5,
        "instagram": 15
    }
    
    limit = limits.get(platform, 5)
    
    # Generate hashtags
    hashtags = []
    
    # Add topic-based hashtags
    for keyword in keywords:
        clean_keyword = ''.join(c for c in keyword if c.isalnum())
        if clean_keyword and len(clean_keyword) > 2:
            hashtags.append(f"#{clean_keyword.capitalize()}")
    
    # Add platform-specific popular hashtags
    popular_tags = {
        "linkedin": ["#Professional", "#Business", "#Networking", "#Career", "#Industry"],
        "twitter": ["#Trending", "#News", "#Update"],
        "facebook": ["#Community", "#Share", "#Connect"],
        "instagram": ["#InstaGood", "#PhotoOfTheDay", "#Explore", "#Viral", "#Trending"]
    }
    
    platform_tags = popular_tags.get(platform, [])
    hashtags.extend(platform_tags)
    
    return hashtags[:limit]


def _generate_reply_content(original_message: str, context: Optional[str], tone: dict, platform: str) -> str:
    """Generate a reply based on the original message"""
    
    templates = {
        "email": f"""{tone['greeting']}

Thank you for your message: "{original_message[:100]}{'...' if len(original_message) > 100 else ''}"

{context if context else 'We appreciate you reaching out and would be happy to assist you.'}

Our team will review your inquiry and get back to you promptly. If this is urgent, please do not hesitate to contact us directly.

{tone['closing']}""",

        "whatsapp": f"""{tone['greeting']}

Thanks for your message!

{context if context else 'We have received your inquiry and will respond shortly.'}

In the meantime, feel free to share any additional details that might help us assist you better.""",

        "social": f"""{tone['greeting']}

Thanks for reaching out!

{context if context else 'We would love to help you with this.'}

Please check your DMs for more details, or feel free to ask any follow-up questions here!""",

        "default": f"""{tone['greeting']}

Thank you for your message.

{context if context else 'We have received your inquiry and will respond as soon as possible.'}

{tone['closing']}"""
    }
    
    return templates.get(platform, templates["default"])
