import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_SERVER_URL = os.getenv("API_SERVER_URL", "http://localhost:8000")
APP_NAME = os.getenv("APP_NAME", "damnvulnerableadk")
USER_ID = os.getenv("USER_ID", "1")

async def create_llm_session() -> str:
    """
    This function creates a new session with the LLM agent.
    It returns the session ID which can be used for further interactions.
    example:
    ```
    curl -X 'POST' \
        'http://127.0.0.1:8000/apps/{app_name}/users/{user_id}/sessions' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "additionalProp1": {}
        }'
    ```
    """
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    data = {}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_SERVER_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions", 
            headers=headers, 
            json=data
        )
    
    if response.status_code == 200:
        return response.json().get("id", "default_session")
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

async def ask_llm_agent(message: str) -> dict:
    """
    we do a POST call to the API_SERVER_URL with the message and return the response.
    example:
    ```
    curl -X 'POST' \
        'API_SERVER_URL/run_sse' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "appName": "damnvulnerableadk",
        "userId": "1",
        "sessionId": "123",
        "newMessage": {
            "parts": [
                {
                    "text": "test"
                }
            ],
                "role": "user"
            },
                "streaming": false
        }'
    ```
    """
    session_id = await create_llm_session()
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    data = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": session_id if session_id else "default_session",
        "newMessage": {
            "parts": [{"text": message}],
            "role": "user"
        },
        "streaming": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_SERVER_URL}/run_sse", headers=headers, json=data)

    if response.status_code == 200:
        # Split the response by "data: " to get individual SSE events
        sse_chunks = response.text.split("data: ")
        # Filter out empty chunks and process each one
        valid_chunks = [chunk.strip() for chunk in sse_chunks if chunk.strip()]
        
        # Get the last chunk which typically contains the final response
        # This is usually what we want to return to the user
        for chunk in reversed(valid_chunks):
            try:
                parsed_chunk = json.loads(chunk)
                # Look for text content in the response
                if ("content" in parsed_chunk and 
                    "parts" in parsed_chunk["content"] and 
                    parsed_chunk["content"]["parts"] and
                    "text" in parsed_chunk["content"]["parts"][0]):
                    
                    return {
                        "status": "success", 
                        "text": parsed_chunk["content"]["parts"][0]["text"],
                        "data": parsed_chunk
                    }
            except json.JSONDecodeError:
                continue
        
        # If we couldn't find a final text response, return the full data
        return {
            "status": "success",
            "message": "Got SSE response with no final text",
            "chunks": valid_chunks
        }
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")