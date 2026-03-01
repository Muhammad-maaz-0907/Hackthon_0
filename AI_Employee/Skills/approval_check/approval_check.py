# Approval Check Skill - Silver Tier

def needs_approval(task_text):
    """Check if task requires approval."""
    text_lower = task_text.lower()
    return "email" in text_lower or "post" in text_lower
