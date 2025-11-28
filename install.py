import os
import sys
import json
import platform
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Installs required packages using the current python interpreter."""
    print("📦 Installing dependencies...")
    packages = ["mcp", "python-telegram-bot", "httpx", "python-dotenv"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("✅ Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def get_claude_desktop_config_path():
    """Returns the path to claude_desktop_config.json based on the OS."""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
        return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":  # macOS
        return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux and others
        return home / ".config" / "Claude" / "claude_desktop_config.json"

def configure_claude_code(python_exe, server_script):
    """Configures Claude Code (CLI) by writing to managed-mcp.json."""
    print("\n🤖 Configuring Claude Code (CLI)...")
    
    home = Path.home()
    
    # Determine path based on OS
    if sys.platform == "win32":
        # Windows: C:\ProgramData\ClaudeCode\managed-mcp.json
        config_path = Path("C:/ProgramData/ClaudeCode/managed-mcp.json")
    elif sys.platform == "darwin":
        # macOS: /Library/Application Support/ClaudeCode/managed-mcp.json
        config_path = Path("/Library/Application Support/ClaudeCode/managed-mcp.json")
    else:
        # Linux: /etc/claude-code/managed-mcp.json
        config_path = Path("/etc/claude-code/managed-mcp.json")
    
    print(f"   Target config path: {config_path}")
    
    # Create parent directory if it doesn't exist
    if not config_path.parent.exists():
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"   ⚠️  No permission to create {config_path.parent}. Skipping Claude Code configuration.")
            return
        except Exception as e:
            print(f"   ⚠️  Could not create directory: {e}. Skipping Claude Code configuration.")
            return
    
    # Read existing config or start fresh
    config_data = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception:
            pass
    
    # Ensure mcpServers section exists
    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}
    
    # Add our server configuration
    config_data["mcpServers"]["telegram-agent"] = {
        "command": str(Path(python_exe).as_posix()),
        "args": [str(server_script.as_posix())]
    }
    
    # Write the config
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        print(f"   ✅ Claude Code configuration updated at {config_path}")
    except PermissionError:
        print(f"   ⚠️  No permission to write to {config_path}. You may need to run as administrator.")
    except Exception as e:
        print(f"   ❌ Failed to update Claude Code config: {e}")



def main():
    print("🚀 Starting Telegram MCP Server Setup (Universal)")
    print("===============================================")

    # 1. Install Dependencies
    install_dependencies()

    # 2. Get User Input
    print("\n📝 Configuration")
    token = input("Enter Telegram Bot Token: ").strip()
    while not token:
        print("Token cannot be empty.")
        token = input("Enter Telegram Bot Token: ").strip()

    group_id = input("Enter Group ID: ").strip()
    while not group_id:
        print("Group ID cannot be empty.")
        group_id = input("Enter Group ID: ").strip()

    # 3. Setup Paths & Files
    current_dir = Path(__file__).parent.resolve()
    server_script = current_dir / "server.py"
    env_file = current_dir / ".env"
    
    if not server_script.exists():
        print(f"❌ Error: server.py not found at {server_script}")
        sys.exit(1)

    # 4. Write .env file
    print(f"\n💾 Writing configuration to {env_file}...")
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
            f.write(f"TELEGRAM_GROUP_ID={group_id}\n")
        print("   ✅ .env file created.")
    except Exception as e:
        print(f"   ❌ Failed to write .env file: {e}")
        sys.exit(1)

    # Convert python executable path to POSIX style for cross-platform JSON compatibility
    python_exe = Path(sys.executable).as_posix()

    # 5. Prepare Config Data (for Desktop & Manual)
    server_config = {
        "command": python_exe,
        "args": [str(server_script.as_posix())]
    }

    # 6. Configure Claude Desktop
    config_path = get_claude_desktop_config_path()
    print(f"\n🖥️  Configuring Claude Desktop at: {config_path}")

    if not config_path.parent.exists():
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    config_data = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except:
            pass

    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}

    config_data["mcpServers"]["telegram-agent"] = server_config

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        print("   ✅ Claude Desktop configuration updated.")
    except Exception as e:
        print(f"   ❌ Failed to update Claude Desktop config: {e}")

    # 7. Configure Claude Code (CLI)
    configure_claude_code(python_exe, server_script)



    # 9. Universal Output
    print("\n🖱️  Cursor / Other Tools Configuration")
    print("For Cursor, go to 'Features > MCP' and add this manually:")
    print("-" * 60)
    
    universal_json = {
        "mcpServers": {
            "telegram-agent": server_config
        }
    }
    print(json.dumps(universal_json, indent=2))
    print("-" * 60)
    print("\n✨ Setup Complete! ✨")

if __name__ == "__main__":
    main()
