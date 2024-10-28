from typing import List, Dict, Optional
from ..core.constants import COURSES

async def search_courses(
    query: str,
    skill_level: Optional[str] = None,
    category: Optional[str] = None
) -> Dict:
    filtered_courses = [
        course for course in COURSES
        if (query.lower() in course["title"].lower() or 
            query.lower() in course["description"].lower())
        and (not skill_level or course["skill_level"] == skill_level)
        and (not category or course["category"] == category)
    ]
    
    return {
        "courses": filtered_courses,
        "total": len(filtered_courses)
    }