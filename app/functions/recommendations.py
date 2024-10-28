from typing import List, Dict, Optional
from ..core.constants import COURSES
import random

async def get_recommendations(
    user_id: str,
    interests: Optional[List[str]] = None
) -> Dict:
    # Simple recommendation logic based on interests
    recommended_courses = [
        course for course in COURSES
        if not interests or course["category"] in interests
    ]
    
    # Randomly select up to 5 courses
    recommended_courses = random.sample(
        recommended_courses, 
        min(5, len(recommended_courses))
    )
    
    return {
        "recommendations": recommended_courses,
        "based_on": interests if interests else "general"
    }