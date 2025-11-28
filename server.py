import os
import time
import asyncio
import httpx
import re
import html
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_GROUP_ID:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_GROUP_ID environment variables")

API_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

class TelegramHandler:
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def _make_request(self, method: str, endpoint: str, data: dict = None):
        url = f"{API_BASE_URL}/{endpoint}"
        try:
            response = self.client.request(method, url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error calling Telegram API: {e.response.text}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def create_forum_topic(self, name: str) -> int:
        """Creates a new forum topic in the supergroup and returns the message_thread_id."""
        data = {
            "chat_id": TELEGRAM_GROUP_ID,
            "name": name
        }
        result = self._make_request("POST", "createForumTopic", data)
        if result.get("ok"):
            return result["result"]["message_thread_id"]
        raise Exception(f"Failed to create topic: {result}")

    def _convert_to_html(self, text: str) -> str:
        """
        Converts standard Markdown to Telegram-supported HTML.
        Handles code blocks, inline code, bold, and italic.
        """
        # 1. Split by code blocks to avoid escaping inside code
        parts = re.split(r'(```.*?```)', text, flags=re.DOTALL)
        
        html_parts = []
        for part in parts:
            if part.startswith('```') and part.endswith('```'):
                # Code block: Extract content, escape HTML, wrap in <pre>
                content = part[3:-3].strip()
                # Remove language identifier if present (e.g. ```python)
                first_line_break = content.find('\n')
                if first_line_break > -1 and first_line_break < 20:
                    # Check if the first line looks like a language ID
                    lang_line = content[:first_line_break].strip()
                    if re.match(r'^[a-zA-Z0-9+#]+$', lang_line):
                        content = content[first_line_break+1:]
                
                escaped_content = html.escape(content)
                html_parts.append(f'<pre>{escaped_content}</pre>')
            else:
                # Normal text: Escape HTML first, then apply formatting
                escaped_text = html.escape(part)
                
                # Bold: **text** -> <b>text</b>
                escaped_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', escaped_text)
                # Bold: __text__ -> <b>text</b>
                escaped_text = re.sub(r'__(.*?)__', r'<b>\1</b>', escaped_text)
                
                # Italic: *text* -> <i>text</i> (Be careful with lists)
                # We only match * if it's not at the start of a line (list item)
                # Or just support _text_ for italic to be safe
                escaped_text = re.sub(r'_(.*?)_', r'<i>\1</i>', escaped_text)
                
                # Inline code: `text` -> <code>text</code>
                escaped_text = re.sub(r'`(.*?)`', r'<code>\1</code>', escaped_text)
                
                # Lists: * item or - item -> • item
                # Match start of string or newline, followed by * or - and a space
                escaped_text = re.sub(r'(^|\n)[\*\-]\s+', r'\1• ', escaped_text)
                
                html_parts.append(escaped_text)
        
        return "".join(html_parts)

    def send_message(self, thread_id: int, text: str, parse_mode: str = "HTML", buttons: list[str] = None) -> dict:
        """
        Sends a message to a specific topic. 
        Converts Markdown to HTML by default.
        """
        # Convert text if using HTML and it looks like Markdown
        final_text = text
        if parse_mode == "HTML":
            final_text = self._convert_to_html(text)

        data = {
            "chat_id": TELEGRAM_GROUP_ID,
            "message_thread_id": thread_id,
            "text": final_text,
            "parse_mode": parse_mode
        }

        if buttons:
            # Create inline keyboard (1 column layout for simplicity and long text support)
            keyboard = [[{"text": btn, "callback_data": btn[:64]}] for btn in buttons]
            data["reply_markup"] = {"inline_keyboard": keyboard}
        
        try:
            # Try sending with formatting
            result = self._make_request("POST", "sendMessage", data)
            if result.get("ok"):
                return result["result"]
            else:
                print(f"Telegram API Error: {result}")
        except Exception as e:
            print(f"Failed to send with {parse_mode}: {e}")

        # Fallback: Try plain text if HTML failed
        print("Retrying as plain text...")
        del data["parse_mode"]
        data["text"] = text # Restore original text
        result = self._make_request("POST", "sendMessage", data)
        if result.get("ok"):
            return result["result"]
                
        raise Exception(f"Failed to send message: {result}")

    def get_updates(self, offset: int = None) -> list:
        """Fetches updates from Telegram."""
        data = {
            "timeout": 10,  # Long polling timeout
            "allowed_updates": ["message", "callback_query"]
        }
        if offset:
            data["offset"] = offset
        
        try:
            response = self.client.post(f"{API_BASE_URL}/getUpdates", json=data, timeout=15.0)
            response.raise_for_status()
            result = response.json()
            if result.get("ok"):
                return result["result"]
            return []
        except Exception as e:
            print(f"Error getting updates: {e}")
            return []

    def wait_for_reply(self, thread_id: int) -> str:
        """Blocks until a user replies in the specified thread (text or button click)."""
        print(f"Waiting for reply in thread {thread_id}...")
        
        updates = self.get_updates()
        last_update_id = 0
        if updates:
            last_update_id = updates[-1]["update_id"]

        while True:
            updates = self.get_updates(offset=last_update_id + 1)
            
            for update in updates:
                last_update_id = update["update_id"]
                
                # Handle Text Message
                message = update.get("message")
                if message:
                    msg_thread_id = message.get("message_thread_id")
                    chat_id = str(message.get("chat", {}).get("id"))
                    
                    if chat_id == TELEGRAM_GROUP_ID and msg_thread_id == thread_id:
                        if "text" in message:
                            return message["text"]

                # Handle Button Click (Callback Query)
                callback = update.get("callback_query")
                if callback:
                    message = callback.get("message")
                    # Note: In forums, message_thread_id is inside the message object
                    msg_thread_id = message.get("message_thread_id")
                    chat_id = str(message.get("chat", {}).get("id"))

                    if chat_id == TELEGRAM_GROUP_ID and msg_thread_id == thread_id:
                        # Answer the callback (stop loading animation)
                        try:
                            self._make_request("POST", "answerCallbackQuery", {"callback_query_id": callback["id"]})
                        except:
                            pass
                        
                        selection = callback["data"]
                        # Send a confirmation message so it appears in chat history
                        self.send_message(thread_id, f"🔘 **Selected:** {selection}")
                        
                        return selection
            
            time.sleep(2)

# Initialize MCP Server
mcp = FastMCP("Telegram Human-in-the-Loop")
telegram = TelegramHandler()

@mcp.tool()
def init_task_session(task_name: str) -> str:
    """
    Creates a new Telegram forum topic for a task.
    Returns the thread_id as a string.
    """
    try:
        thread_id = telegram.create_forum_topic(task_name)
        return str(thread_id)
    except Exception as e:
        return f"Error creating task session: {str(e)}"

@mcp.tool()
def broadcast_log(thread_id: str, message: str) -> str:
    """
    Sends a log message to the Telegram topic.
    Returns a confirmation string.
    """
    try:
        telegram.send_message(int(thread_id), message)
        return "Log sent successfully"
    except Exception as e:
        return f"Error broadcasting log: {str(e)}"

@mcp.tool()
def ask_human_and_wait(thread_id: str, question: str, options: list[str] = None) -> str:
    """
    Sends a message to the Telegram topic and WAITS for a user reply.
    Use this to ask for the next instruction or clarification.
    
    Args:
        thread_id: The Telegram topic ID.
        question: The text to send.
        options: Optional list of short strings (max 3-4) to present as buttons.
                 Example: ["Run Tests", "Deploy", "Explain Code"]
    
    Returns the user's reply text (or the button label selected).
    """
    try:
        # 1. Send the question/message with buttons
        telegram.send_message(int(thread_id), question, buttons=options)
        
        # 2. Wait for reply
        answer = telegram.wait_for_reply(int(thread_id))
        
        # 3. No auto-acknowledgement needed for natural chat flow
        # The Agent will reply naturally in the next turn.
        
        return answer
    except Exception as e:
        return f"Error asking human: {str(e)}"

if __name__ == "__main__":
    mcp.run()
