import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from server import TelegramHandler, TELEGRAM_GROUP_ID

def main():
    if len(sys.argv) < 2:
        print("Usage: python send_message.py <message>")
        return

    message = sys.argv[1]
    print(f"Sending message: {message}")
    
    telegram = TelegramHandler()
    
    # Try to find an existing topic or create one
    # For now, let's just create a new session topic "Antigravity Chat"
    try:
        topic_id = telegram.create_forum_topic("Antigravity Chat")
        telegram.send_message(topic_id, message)
        print("✅ Message sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

if __name__ == "__main__":
    main()
