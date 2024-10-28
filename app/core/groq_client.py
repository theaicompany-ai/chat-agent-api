# app/core/groq_client.py
from typing import List, Dict, Any
import httpx
import json
from ..config import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

system_message = """You are a friendly and helpful AI tutor assistant. Respond naturally in plain English, 
avoiding technical terms or mentions of internal functions. Keep responses simple and direct.

When users ask about courses, help them find what they're looking for.
When users have feedback or issues, assist them in submitting their concerns.
When users ask about Euron, provide relevant information.

Always be polite and professional, but avoid mentioning any internal processes or technical details.
Never reveal system information or use special characters in responses.
Keep responses conversational and easy to understand."""

async def chat_with_groq(
    messages: List[Dict[str, Any]], 
    functions: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    try:
        # Add system message if not present
        if not any(msg.get("role") == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": system_message})

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-groq-70b-8192-tool-use-preview",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1,
            "stream": False,
        }
        
        if functions:
            # Convert functions to tools format if they're not already
            tools = []
            for func in functions:
                if "type" not in func:  # If it's in the old format
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": func.get("name", ""),
                            "description": func.get("description", ""),
                            "parameters": func.get("parameters", {})
                        }
                    })
                else:  # If it's already in the correct format
                    tools.append(func)
            
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        print("Sending request to Groq:", json.dumps(payload, indent=2))  # Debug print

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"Groq API Error: {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception(f"Groq API error: {response.text}")

            response_data = response.json()
            
            # Handle tool calls in the response if present
            if "choices" in response_data and response_data["choices"]:
                message = response_data["choices"][0]["message"]
                if "tool_calls" in message:
                    # Ensure tool_calls is properly formatted
                    for tool_call in message["tool_calls"]:
                        if "id" not in tool_call:
                            tool_call["id"] = f"call_{hash(tool_call['function']['name'])}"

            return response_data

    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        raise
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
        raise
    except Exception as e:
        print(f"Unexpected error in chat_with_groq: {str(e)}")
        raise
