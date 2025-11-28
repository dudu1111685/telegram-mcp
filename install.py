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
    """Configures Claude Code (CLI) globally."""
    print("\n🤖 Configuring Claude Code (CLI)...")
    
    # 1. Try to remove existing server first (to allow updates)
    try:
        subprocess.run(
            ["claude", "mcp", "remove", "telegram-agent"],
            check=False, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("   ⚠️  'claude' command not found. Skipping CLI configuration.")
        return

    # 2. Add the server
    cmd = [
        "claude", "mcp", "add", "telegram-agent",
        "--scope", "user",
        "--", python_exe, str(server_script)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("   ✅ Claude Code configured successfully.")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to configure Claude Code: {e}")

def configure_antigravity(python_exe, server_script):
    """Attempts to configure Antigravity / Gemini IDE automatically."""
    print("\n🌌 Configuring Antigravity (Gemini IDE)...")
    
    home = Path.home()
    
    # Determine path based on OS
    if sys.platform == "win32":
        # Windows: %APPDATA%/Google/Antigravity/mcp_config.json
        appdata = os.getenv("APPDATA")
        if appdata:
             config_path = Path(appdata) / "Google" / "Antigravity" / "mcp_config.json"
        else:
             config_path = home / "AppData" / "Roaming" / "Google" / "Antigravity" / "mcp_config.json"
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/Google/Antigravity/mcp_config.json
        config_path = home / "Library" / "Application Support" / "Google" / "Antigravity" / "mcp_config.json"
    else:
        # Linux: ~/.gemini/antigravity/mcp_config.json (Confirmed by user)
        config_path = home / ".gemini" / "antigravity" / "mcp_config.json"
    
    # Fallback/Alternative check for Linux if the above doesn't exist but ~/.gemini/settings.json does
    if not config_path.parent.exists() and (home / ".gemini" / "settings.json").exists():
         config_path = home / ".gemini" / "settings.json"

    print(f"   Target config path: {config_path}")

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

    # Antigravity config usually follows the same structure
    config_data["mcpServers"]["telegram-agent"] = {
        "command": python_exe,
        "args": [str(server_script)]
    }

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        print(f"   ✅ Antigravity configuration updated at {config_path}")
    except Exception as e:
        print(f"   ❌ Failed to update Antigravity config: {e}")

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

    python_exe = sys.executable

    # 5. Prepare Config Data (for Desktop & Manual)
    server_config = {
        "command": python_exe,
        "args": [str(server_script)]
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

    # 8. Configure Antigravity
    configure_antigravity(python_exe, server_script)

    # 9. Universal Output
    print("\n🌐 Universal Configuration (Other Tools)")
    print("For any other tool, use this MCP configuration:")
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
