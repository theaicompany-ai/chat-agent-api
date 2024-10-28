from typing import Dict
from ..core.constants import USER_PROGRESS

async def get_course_progress(
    course_id: str,
    user_id: str
) -> Dict:
    user_data = USER_PROGRESS.get(user_id, {})
    course_progress = user_data.get(course_id, {
        "completion_percentage": 0,
        "modules_completed": 0,
        "total_modules": 0,
        "last_activity": None,
        "next_milestone": "Start the course"
    })
    
    return course_progress
