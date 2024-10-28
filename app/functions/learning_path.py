from typing import Dict, Optional, List
from ..core.constants import LEARNING_PATHS

async def generate_learning_path(
    goal: str,
    current_level: str,
    timeline: Optional[str] = None
) -> Dict:
    path = LEARNING_PATHS.get(goal, {}).get(current_level, [])
    
    return {
        "learning_path": path,
        "estimated_duration": sum(
            int(item["duration"].split()[0]) for item in path
        ),
        "skill_level_target": "intermediate"
    }