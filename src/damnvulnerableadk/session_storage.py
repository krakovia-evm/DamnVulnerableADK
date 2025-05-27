import os
import datetime
from google.genai import types


class SessionStorage:
    """Enhanced session storage with improved formatting and logging"""
    
    def __init__(self, sessions_dir="sessions"):
        """Initialize the session storage handler"""
        self.sessions_dir = sessions_dir
        self.session_stats = {}
        # Create sessions directory if it doesn't exist
        os.makedirs(sessions_dir, exist_ok=True)
    
    def save_message(self, session_id, role, message, message_type="general", response_time_ms=None):
        """Save a message with enhanced formatting and metadata"""
        # Create a filename based on session_id
        filename = os.path.join(self.sessions_dir, f"session_{session_id}.txt")
        
        # Check if file exists to determine if we need to initialize it
        file_exists = os.path.isfile(filename)
        
        # Initialize session stats if needed
        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                "start_time": datetime.datetime.now(),
                "message_count": 0,
                "user_messages": 0,
                "agent_responses": 0,
                "function_calls": 0
            }
        
        # Update stats
        stats = self.session_stats[session_id]
        stats["message_count"] += 1
        if role == "USER":
            stats["user_messages"] += 1
        elif "AGENT" in role or role == "ROOT_AGENT":
            stats["agent_responses"] += 1
        elif "FUNCTION" in role or role in ["MAIN --> DB", "DATABASE_LLM_TOOL"]:
            stats["function_calls"] += 1
        
        # Get timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Append the message to the file with enhanced formatting
        with open(filename, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("🤖 TESTA2A SESSION LOG\n")
                f.write("=" * 60 + "\n")
                f.write(f"📅 Session ID: {session_id}\n")
                f.write(f"⏰ Started: {stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
            
            # Format message based on role with emojis and boxes
            self._write_formatted_message(f, timestamp, role, message, response_time_ms)
            
            # Add session stats every 10 messages
            if stats["message_count"] % 10 == 0:
                self._write_session_stats(f, stats)
    
    def _write_formatted_message(self, f, timestamp, role, message, response_time_ms=None):
        """Write a beautifully formatted message with emojis and boxes"""
        
        def wrap_message(msg, prefix="│ "):
            """Wrap long messages across multiple lines"""
            lines = []
            while len(msg) > 150:
                # Find the last space before 150 characters
                break_point = msg.rfind(' ', 0, 150)
                if break_point == -1:  # No space found, force break at 150
                    break_point = 150
                lines.append(f"{prefix}{msg[:break_point]}")
                msg = msg[break_point:].lstrip()
            if msg:  # Add remaining text
                lines.append(f"{prefix}{msg}")
            return lines
        
        if role == "USER":
            f.write(f"┌─ 👤 USER [{timestamp}] " + "─" * 35 + "\n")
            for line in wrap_message(message):
                f.write(f"{line}\n")
            f.write("└" + "─" * 55 + "\n\n")
            
        elif role in ["ROOT_AGENT", "AGENT_RESPONSE"]:
            f.write(f"┌─ 🤖 AGENT [{timestamp}] " + "─" * 33 + "\n")
            for line in wrap_message(message):
                f.write(f"{line}\n")
            if response_time_ms:
                f.write(f"│ ⚡ Response time: {response_time_ms:.1f}ms\n")
            f.write("└" + "─" * 55 + "\n\n")
            
        elif role == "MAIN --> DB":
            f.write(f"┌─ 🔄 AGENT→AGENT [{timestamp}] " + "─" * 25 + "\n")
            for line in wrap_message(message, "│ 📤 Sending: " if message == wrap_message(message)[0].replace("│ ", "") else "│ "):
                f.write(f"{line}\n")
            f.write("└" + "─" * 55 + "\n\n")
            
        elif role == "DATABASE_LLM_TOOL":
            f.write(f"┌─ 📊 DATABASE [{timestamp}] " + "─" * 28 + "\n")
            for line in wrap_message(message, "│ 📥 Response: " if message == wrap_message(message)[0].replace("│ ", "") else "│ "):
                f.write(f"{line}\n")
            f.write("└" + "─" * 55 + "\n\n")
            
        elif "FUNCTION" in role:
            f.write(f"┌─ 🔧 FUNCTION [{timestamp}] " + "─" * 27 + "\n")
            for line in wrap_message(message):
                f.write(f"{line}\n")
            f.write("└" + "─" * 55 + "\n\n")
            
        else:  # System or other messages
            f.write(f"┌─ ℹ️  SYSTEM [{timestamp}] " + "─" * 29 + "\n")
            for line in wrap_message(message):
                f.write(f"{line}\n")
            f.write("└" + "─" * 55 + "\n\n")
    
    def _write_session_stats(self, f, stats):
        """Write session statistics"""
        duration = datetime.datetime.now() - stats["start_time"]
        f.write("📈 SESSION STATS " + "─" * 20 + "\n")
        f.write(f"💬 Total Messages: {stats['message_count']}\n")
        f.write(f"👤 User Messages: {stats['user_messages']}\n")
        f.write(f"🤖 Agent Responses: {stats['agent_responses']}\n")
        f.write(f"🔧 Function Calls: {stats['function_calls']}\n")
        f.write(f"⏱️  Duration: {duration.total_seconds():.1f}s\n")
        f.write("─" * 37 + "\n\n")

def get_database_llm_text(session_id, session_storage: SessionStorage, content: types.Content) -> str:
    if not content or not content.parts:
        return ""
    for part in content.parts:
        if (
            part 
            and part.function_response
            and part.function_response.name == "ask_llm_agent"
        ):
            session_storage.save_message(
                session_id, 
                "DATABASE_LLM_TOOL", 
                part.function_response.response['text'],
                message_type="function_response"
            )
        if (
            part 
            and part.function_call 
            and part.function_call.name == "ask_llm_agent"
        ):
            session_storage.save_message(
                session_id, 
                "MAIN --> DB", 
                part.function_call.args['message'],
                message_type="function_call"
            )
    return ""