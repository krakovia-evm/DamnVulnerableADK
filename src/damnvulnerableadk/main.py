import asyncio
import sys
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from damnvulnerableadk.agent import a2a_agent
from damnvulnerableadk.database import init_db
from damnvulnerableadk.session_storage import SessionStorage, get_database_llm_text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def async_input(prompt: str = "") -> str:
    """Async version of input() function"""
    if prompt:
        print(prompt, end="", flush=True)
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sys.stdin.readline)

async def run_agent(message, temp_service=None, session=None, session_storage=None):
    import time
    start_time = time.time()
    
    # Create new session service and session if not provided
    if temp_service is None:
        temp_service = InMemorySessionService()
        runner = Runner(
            app_name="robot",
            agent=a2a_agent,
            session_service=temp_service
        )
        session = await temp_service.create_session(
            app_name="robot",
            user_id="user",
        )
    else:
        runner = Runner(
            app_name="robot",
            agent=a2a_agent,
            session_service=temp_service
        )

        
    # Create session storage if not provided
    if session_storage is None:
        session_storage = SessionStorage()
    
    # Save the user message with enhanced logging
    session_storage.save_message(session.id, "USER", message, "user_input")

    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)])
    ):
        # Process the event and save messages to file
        # TODO: handle KeyError: 'text' when the API LLM doesn't reply or reply with error like 429
        get_database_llm_text(session.id, session_storage, event.content)
        if event.is_final_response():
            final_response = event.content.parts[0].text
            session_storage.save_message(
                session.id, 
                "ROOT_AGENT", 
                final_response, 
                "agent_response",
                (time.time() - start_time) * 1000
            )
            return final_response, temp_service, session

async def conversation_loop():
    print("🤖 Welcome to A2A ADK Console!")
    print("💬 Ask questions about users in the database.")
    print("🔥 Press Ctrl+C to exit the conversation.")
    print("─" * 50)
    
    # Initialize session service and session for the conversation
    temp_service = InMemorySessionService()
    session = await temp_service.create_session(
        app_name="robot",
        user_id="user",
    )
    
    # Initialize session storage
    session_storage = SessionStorage()
    
    while True:
        message = await async_input("\n👤 You: ")
        message = message.strip()
        if not message:
            continue
            
        print("🤔 Agent is thinking...")
        result, temp_service, session = await run_agent(message, temp_service, session, session_storage)
        print(f"\n🤖 Agent: {result}")
        
        # Show mini stats after each interaction
        if session.id in session_storage.session_stats:
            stats = session_storage.session_stats[session.id]
            print(f"📊 Stats: {stats['message_count']} msgs | {stats['user_messages']} 👤 | {stats['agent_responses']} 🤖")

if __name__ == "__main__":
    
    async def main():
        init_db()
        try:
            await conversation_loop()
        except (KeyboardInterrupt, EOFError):
            print("\n\nConversation ended. Goodbye!")
    
    asyncio.run(main())