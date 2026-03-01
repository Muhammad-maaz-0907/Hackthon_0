# LinkedIn Poster - Content Generator
# Generates LinkedIn post content and saves to Needs_Action/ for approval

import os
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Go up to AI_Employee (2 levels)
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, 'Needs_Action')


def generate_post_content():
    """Generate LinkedIn post content."""
    posts = [
        "Excited to offer our AI automation services! Boost your business efficiency with smart workflows. DM for details. #AI #Automation #BusinessGrowth",
        "Just completed an amazing AI integration project! The future of work is here. Ready to transform your business? Let's connect! #Innovation #AI #TechSolutions",
        "5 ways AI can transform your business today:\n1. Automate repetitive tasks\n2. Enhance customer service\n3. Analyze data faster\n4. Reduce operational costs\n5. Scale efficiently\n\nWhich one interests you? #AI #BusinessTips",
        "Proud to announce our new AI Employee system! It automates emails, social media, and task management. The workforce of tomorrow is here. #AI #Productivity #Innovation",
        "Monday motivation: Automation isn't about replacing humans—it's about empowering them to do their best work. What's your take? #MondayMotivation #AI #FutureOfWork"
    ]
    
    import random
    return random.choice(posts)


def create_post_file(content=None):
    """Create a markdown file with post content in Needs_Action/."""
    if content is None:
        content = generate_post_content()
    
    # Ensure directory exists
    os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"linkedin_post_{timestamp}.md"
    filepath = os.path.join(NEEDS_ACTION_DIR, filename)
    
    # Create markdown content with frontmatter
    markdown_content = f"""---
type: linkedin_post
status: pending
created_at: {datetime.datetime.now().isoformat()}
---

{content}
"""
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    logger.info(f"Created post file: {filepath}")
    print(f"\n[OK] Post draft created: {filename}")
    print(f"  Location: {NEEDS_ACTION_DIR}")
    print(f"\n  Next step: Review and move to Approved/ folder to publish")
    
    return filepath


def main():
    """Main function to generate a LinkedIn post draft."""
    print("=" * 50)
    print("LinkedIn Post Generator")
    print("=" * 50)
    
    try:
        filepath = create_post_file()
        print("\n[OK] Post generated successfully!")
        print("\nTo publish this post:")
        print(f"  1. Review: {filepath}")
        print(f"  2. Move file to: {os.path.join(BASE_DIR, 'Approved/')}")
        print("  3. approval_engine.py will handle the rest!")
        
    except Exception as e:
        logger.error(f"Error generating post: {e}")
        print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    main()
