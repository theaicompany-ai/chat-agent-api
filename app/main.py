# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from pydantic import BaseModel
import json
import httpx
import asyncio
import os
# from app.config import SWARM_SETTINGS, OPENAI_SWARM_API_KEY
from app.config import Settings
settings = Settings()
from swarm import Swarm

from .core.security import verify_api_key
from .core.groq_client import chat_with_groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    name: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    tools: Optional[List[Dict]] = None

# Updated tools definition according to Groq's format
EDTECH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_courses",
            "description": "Search for courses on the platform based on query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for courses"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_complaint",
            "description": "Submit a user complaint or feedback to the support system",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "User's email address"
                    },
                    "name": {
                        "type": "string",
                        "description": "User's full name"
                    },
                    "complaint": {
                        "type": "string",
                        "description": "User's complaint or feedback details"
                    }
                },
                "required": ["email", "name", "complaint"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_euron",
            "description": "Query the Euron API for general information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query about Euron"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def extract_course_name(query: str) -> str:
    # List of common phrases that might precede a course name
    prefixes = [
        "tell me about the course",
        "information on the course",
        "details about",
        "what is",
        "course called",
        "course named",
        "course titled",
        "about the",
        "show me",
        "find",
    ]
    
    lower_query = query.lower()
    
    # First try to extract the course name after any prefix
    course_name = lower_query
    for prefix in prefixes:
        if prefix in lower_query:
            course_name = lower_query.split(prefix)[-1].strip()
            break
    
    # Remove common words and clean up the text
    words_to_remove = [
        "course", "class", "program", "training",
        "the", "a", "an", "about", "for", "in"
    ]
    
    # Split into words and filter out unwanted words
    words = course_name.split()
    filtered_words = [
        word.strip() for word in words 
        if word not in words_to_remove
    ]
    
    # Join the remaining words with a hyphen, without adding "-course" suffix
    formatted_name = "-".join(filtered_words)
    
    return formatted_name

async def search_platform_courses(query: str) -> Dict:
    async with httpx.AsyncClient() as client:
        try:
            # Extract and format course name
            course_name = extract_course_name(query)
            print(f"Searching for course: {course_name}")  # Debug print
            
            response = await client.get(
                f"https://dev-api.euron.one/api/v1/courses/{course_name}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"error": "Failed to search platform courses"}

async def query_euron(query: str) -> Dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://dev-api.euron.one/",
                params={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return {"error": str(e)}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"error": "Failed to query Euron API"}

async def submit_complaint(email: str, name: str, complaint: str) -> Dict:
    import httpx  # Use httpx for async HTTP requests

    # Your Freshdesk domain and API key from settings
    domain = settings.FRESHDESK_DOMAIN
    api_key = settings.FRESHDESK_API_KEY

    # Ticket data
    data = {
        "description": complaint,
        "subject": "Support Needed",
        "email": email,
        "priority": 1,
        "status": 2
    }

    # URL and headers
    url = f"https://aicompany.freshdesk.com/api/v2/tickets"
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                auth=(api_key, 'X'),
                json=data,
                headers=headers
            )

        if response.status_code == 201:
            return {
                "status": "success",
                "message": "Ticket created successfully",
                "ticket": response.json()
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to create ticket: {response.status_code}",
                "details": response.json()
            }

    except Exception as e:
        print(f"Error in submit_complaint: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to submit complaint: {str(e)}"
        }

async def main():
    swarm = Swarm(api_key=settings.OPENAI_SWARM_API_KEY, **settings.SWARM_SETTINGS)
    # ... existing initialization ...
    
    # Example tool call using Swarm
    results = await swarm.call_tools([
        {"tool": "tool_name_1", "input": "input_data_1"},
        {"tool": "tool_name_2", "input": "input_data_2"},
    ])
    print(results)
    
    # ... existing code ...

if __name__ == "__main__":
    asyncio.run(main())

@app.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        # Format messages properly based on role
        groq_messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role, "content": msg.content}
            
            # Only include tool-related fields if they exist and for appropriate roles
            if msg.role == "tool" and msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
                if msg.name:
                    message_dict["name"] = msg.name
            
            groq_messages.append(message_dict)
        
        latest_message = request.messages[-1].content.lower()
        
        # Keywords for routing
        course_keywords = ["course", "learn", "study", "class", "program", "training"]
        complaint_keywords = ["complaint", "issue", "problem", "feedback"]
        euron_keywords = ["euron", "cryptocurrency", "blockchain"]
        
        # Check if we need to use tools
        needs_tools = any(
            keyword in latest_message 
            for keywords in [course_keywords, complaint_keywords, euron_keywords] 
            for keyword in keywords
        )
        
        if needs_tools:
            print(f"Using tools for message: {latest_message}")
            
            response = await chat_with_groq(
                messages=groq_messages,
                functions=EDTECH_TOOLS
            )
            
            assistant_message = response["choices"][0]["message"]
            print(f"Assistant message: {json.dumps(assistant_message, indent=2)}")
            
            if "tool_calls" in assistant_message:
                tool_calls = assistant_message["tool_calls"]
                results = []
                
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    
                    print(f"Executing function: {function_name}")
                    print(f"With arguments: {arguments}")
                    
                    if function_name == "search_courses":
                        result = await search_platform_courses(
                            query=arguments.get("query", "")
                        )
                    elif function_name == "submit_complaint":
                        result = await submit_complaint(
                            email=arguments.get("email"),
                            name=arguments.get("name"),
                            complaint=arguments.get("complaint")
                        )
                    elif function_name == "query_euron":
                        result = await query_euron(
                            query=arguments.get("query")
                        )
                    else:
                        print(f"Unknown function called: {function_name}")
                        raise ValueError(f"Unknown function: {function_name}")
                    
                    print(f"Function result: {result}")
                    
                    groq_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                    
                    results.append({
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "arguments": arguments,
                        "result": result
                    })
                
                final_response = await chat_with_groq(messages=groq_messages)
                return {
                    "response": final_response["choices"][0]["message"]["content"],
                    "tool_calls": results
                }
            
            return {
                "response": assistant_message["content"],
                "tool_calls": None
            }
            
        else:
            response = await chat_with_groq(messages=groq_messages)
            return {
                "response": response["choices"][0]["message"]["content"],
                "tool_calls": None
            }

    except Exception as e:
        print(f"Error in chat_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a test endpoint to verify Groq connection
@app.get("/test-groq")
async def test_groq(api_key: str = Depends(verify_api_key)):
    try:
        response = await chat_with_groq([
            {"role": "user", "content": "Hello, how are you?"}
        ])
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
