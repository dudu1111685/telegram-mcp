# 🤖 Telegram MCP Agent

> **Turn your AI into a Remote Worker.**  
> Control Claude or Cursor directly from Telegram with a continuous, interactive loop.

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Hebrew](https://img.shields.io/badge/Language-עברית-green.svg)](README.he.md)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Enabled-green.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)

## ✨ Features

*   **🔄 Infinite Remote Loop**: The AI doesn't just send a message and quit. It enters a "Telegram Mode" loop where it waits for your commands, executes them, and reports back—indefinitely.
*   **🔘 Smart Interactive Buttons**: Every message comes with context-aware buttons (e.g., "Run Tests", "Fix Bug") for quick 1-tap replies.
*   **🗣️ Multi-Language Support**: Speaks your language! If you write in Hebrew, it replies in Hebrew.
*   **🎨 Rich Formatting**: Sends beautiful Markdown messages with bold text, code blocks, and lists.
*   **🔌 Universal Support**: Optimized for **Claude Desktop**, **Claude Code**, and **Cursor**.

---

## 🚀 Quick Start

### 1. Prerequisites: Setting up Telegram 📱
Before installing, you need to set up your Telegram environment:

1.  **Create a Bot**:
    *   Open [@BotFather](https://t.me/BotFather) in Telegram.
    *   Send `/newbot` and follow the instructions to get your **Bot Token**.
2.  **Create a Supergroup**:
    *   Create a new Group.
    *   **Enable Topics**: Go to Group Settings > Chat History > Enable "Topics" (or "Forum"). *This is critical!*
3.  **Add Bot as Admin**:
    *   Add your new bot to the group.
    *   Promote it to **Admin** with full permissions (specifically "Manage Topics").
4.  **Initialize**:
    *   Send a dummy message in the "General" topic of the group (e.g., "Init").
    *   *This ensures the group ID is accessible.*
5.  **Get Group ID**:
    *   Forward a message from the group to [@RawDataBot](https://t.me/RawDataBot) (or use another method) to find the **Chat ID** (usually starts with `-100`).

### 2. Installation
We provide an automated installer that sets up everything for you.

```bash
python install.py
```

This script will:
1.  Install Python dependencies.
2.  Ask for your **Telegram Bot Token** and **Group ID**.
3.  Configure **Claude Desktop** and **Claude Code** automatically.
4.  Output the configuration needed for **Cursor**.

### 2. Activate "Telegram Mode"
To start the remote worker loop, just tell your AI agent:

> **"I'm leaving. Switch to Telegram."**
> *Or in Hebrew:* **"אני יוצא לקפה, תמשיך מטלגרם."**

The AI will:
1.  Open a new topic in your Telegram Group.
2.  Send you a message: *"I am ready. What should I do?"*
3.  **Wait** for your reply (blocking execution).

### 3. Stop the Session
To exit the loop, simply click the **"Done for now"** (or **"סיימנו לעכשיו"**) button in Telegram.

---

## 📂 Configuration Files

*   **`CLAUDE.md`**: Strict rules for Claude Code to enforce the loop and formatting.
*   **`.cursorrules`**: Auto-detection rules for Cursor and other agents.
*   **`TELEGRAM_MODE.md`**: A system prompt you can paste manually if needed.

## 🛠️ Manual Configuration (Cursor)
To configure **Cursor**:
1.  Open Settings (`Ctrl+,` or `Cmd+,`).
2.  Navigate to **Features** > **MCP**.
3.  Add a new MCP server with the following details:

```json
{
  "name": "telegram-agent",
  "type": "stdio",
  "command": "python",
  "args": ["/absolute/path/to/telegram-mcp/server.py"]
}
```
*(Note: Use the full absolute path to your python executable and the server.py file)*

---
*Built with ❤️ for the MCP Community.*
