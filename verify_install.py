import os
import sys
import time
from dotenv import load_dotenv

# Load env vars from current directory (where .env was created by install.py)
load_dotenv()

# Add current dir to path to import server
sys.path.append(os.getcwd())

try:
    from server import init_task_session, broadcast_log
    print("✅ Successfully imported server module.")
except ImportError as e:
    print(f"❌ Failed to import server: {e}")
    sys.exit(1)

def verify_server():
    print("--- Verifying Server Functionality ---")
    
    # Check Env Vars
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    group_id = os.getenv("TELEGRAM_GROUP_ID")
    
    if not token or not group_id:
        print("❌ Missing environment variables in .env")
        return

    print(f"✅ Loaded configuration (Token: ...{token[-5:]}, Group: {group_id})")

    # Test 1: Init Session
    print("1. Testing init_task_session...")
    try:
        thread_id = init_task_session("Installation Verification")
        print(f"   ✅ Success! Created topic with Thread ID: {thread_id}")
    except Exception as e:
        print(f"   ❌ Failed to create session: {e}")
        return

    # Test 2: Broadcast
    print("2. Testing broadcast_log...")
    try:
        res = broadcast_log(thread_id, "Installation verified successfully by Antigravity Agent.")
        print(f"   ✅ Broadcast result: {res}")
    except Exception as e:
        print(f"   ❌ Failed to broadcast: {e}")

if __name__ == "__main__":
    verify_server()
