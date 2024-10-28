# Mock course data
COURSES = [
    {
        "id": "1",
        "title": "Python Programming Fundamentals",
        "description": "Learn Python from scratch with hands-on projects",
        "skill_level": "Beginner",
        "category": "Programming",
        "duration": "8 weeks",
        "rating": 4.5
    },
    {
        "id": "2",
        "title": "Data Science Essentials",
        "description": "Master the basics of data science",
        "skill_level": "Intermediate",
        "category": "Data Science",
        "duration": "10 weeks",
        "rating": 4.8
    },
    # Add more courses...
]

# Mock user progress data
USER_PROGRESS = {
    "user123": {
        "course1": {
            "completion_percentage": 75,
            "modules_completed": 6,
            "total_modules": 8,
            "last_activity": "2024-03-15T10:30:00Z",
            "next_milestone": "Complete Module 7: Advanced Topics"
        }
    }
}

# Mock learning paths
LEARNING_PATHS = {
    "web_development": {
        "beginner": [
            {"course_id": "1", "title": "HTML & CSS Basics", "duration": "2 weeks"},
            {"course_id": "2", "title": "JavaScript Fundamentals", "duration": "4 weeks"},
            {"course_id": "3", "title": "React Basics", "duration": "6 weeks"}
        ]
    },
    "data_science": {
        "beginner": [
            {"course_id": "4", "title": "Python Basics", "duration": "3 weeks"},
            {"course_id": "5", "title": "Data Analysis", "duration": "4 weeks"},
            {"course_id": "6", "title": "Machine Learning Intro", "duration": "6 weeks"}
        ]
    }
}