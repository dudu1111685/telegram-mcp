# Telegram MCP Server

A Model Context Protocol (MCP) server that connects your AI agent to a Telegram group.
Allows the agent to send messages, create topics, and wait for human feedback via Telegram buttons.

## Features
- **Send Messages**: Broadcast logs or questions to a Telegram group.
- **Task Sessions**: Automatically creates a new forum topic for each task.
- **Human-in-the-Loop**: Ask questions with buttons (e.g., "Approve", "Reject") and wait for the user's click.

## Prerequisites
- Python 3.10+
- A Telegram Bot Token (from @BotFather)
- A Telegram Group ID (ensure the group has "Topics" enabled)

## Installation

1.  **Run the installer**:
    ```bash
    python install.py
    ```
    This will install dependencies and configure **Claude Code** automatically.

2.  **Follow the prompts**:
    - Enter your Bot Token.
    - Enter your Group ID.

## Configuration

### Claude Code (CLI)
The installer automatically configures Claude Code. You can verify it in:
- Windows: `C:\ProgramData\ClaudeCode\managed-mcp.json`
- macOS: `/Library/Application Support/ClaudeCode/managed-mcp.json`

### Cursor
1.  Open Cursor Settings (`Ctrl+,` or `Cmd+,`).
2.  Go to **Features** > **MCP**.
3.  Click **+ Add New MCP Server**.
4.  Use the configuration output by the `install.py` script. It looks like this:
    - **Name**: `telegram-agent`
    - **Type**: `stdio`
    - **Command**: `python` (use the full path to your python executable)
    - **Args**: `C:/path/to/telegram-mcp/server.py`

### Claude Desktop
The installer automatically configures Claude Desktop if it is installed.

## Usage
Once connected, the agent will have access to tools like:
- `init_task_session(task_name)`: Create a new topic.
- `broadcast_log(thread_id, message)`: Send a log.
- `ask_human_and_wait(thread_id, question, options)`: Ask for input.
