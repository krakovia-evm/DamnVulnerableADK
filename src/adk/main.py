import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from adk.agent import root_agent
from adk.database import init_db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def run_agent(message, temp_service=None, session=None):
    # Create new session service and session if not provided
    if temp_service is None:
        temp_service = InMemorySessionService()
        runner = Runner(
            app_name="robot",
            agent=root_agent,
            session_service=temp_service
        )
        session = temp_service.create_session(
            app_name="robot",
            user_id="user",
        )
    else:
        runner = Runner(
            app_name="robot",
            agent=root_agent,
            session_service=temp_service
        )

    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)])
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text
            return final_response, temp_service, session

async def conversation_loop():
    print("Welcome to DamnVulnerableAI ADK Console!")
    print("Ask questions about users in the database.")
    print("Press Ctrl+C to exit the conversation.")
    print("-" * 50)
    
    # Initialize session service and session for the conversation
    temp_service = InMemorySessionService()
    session = temp_service.create_session(
        app_name="robot",
        user_id="user",
    )
    
    while True:
        message = input("\nYou: ")
        if not message.strip():
            continue
            
        print("Agent is thinking...")
        result, temp_service, session = await run_agent(message, temp_service, session)
        print(f"\nAgent: {result}")

if __name__ == "__main__":
    init_db()
    try:
        asyncio.run(conversation_loop())
    except (KeyboardInterrupt, EOFError):
        print("\n\nConversation ended. Goodbye!")