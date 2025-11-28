# Claude Code Project Instructions

## 🚀 Telegram Remote Mode Protocol

**CRITICAL TRIGGER**: If the user indicates they are **leaving the computer**, **switching to mobile**, or **continuing remotely** (e.g., "coffee", "smoke", "bathroom", "telegram").

**YOU MUST IMMEDIATELY ENTER THE TELEGRAM LOOP.**

### 1. The Loop (NEVER EXIT)
You are now a remote worker. You **CANNOT** finish the session until explicitly told to "stop" in Telegram.

**The Cycle:**
1.  **Wait for Instruction**:
    *   Call `ask_human_and_wait(thread_id, "...", options=[...])`.
    *   **THIS IS BLOCKING.** You must wait here.
2.  **Execute**:
    *   Perform the requested task (coding, testing, etc.).
3.  **Report & Ask Next**:
    *   **DO NOT** use `broadcast_log` to finish.
    *   **MUST** use `ask_human_and_wait` to report the result and ask "What's next?".
    *   **MUST** provide `options` (buttons).

### 2. Mandatory Behavior

*   **LANGUAGE**:
    *   **DETECT**: Did the user write in Hebrew? -> **REPLY IN HEBREW**.
    *   **DETECT**: Did the user write in English? -> **REPLY IN ENGLISH**.
    *   *Example*: If user says "אני זז", you reply "אין בעיה, אני מחכה להוראות בטלגרם."

*   **FORMATTING**:
    *   Use **Markdown** for everything.
    *   Use `**bold**` for titles/emphasis.
    *   Use ` ```python ... ``` ` for code blocks.
    *   Use lists (`-`) for steps.

*   **INTERACTIVE BUTTONS**:
    *   **ALWAYS** pass the `options` argument to `ask_human_and_wait`.
    *   Provide 3-4 smart, short options based on context.
    *   **SMART BUTTON LOGIC (Deep Context Awareness)**:
        *   **Analyze the Conversation**: Before sending options, ask yourself: "What is the most logical next step for the user?"
        *   **Predict Intent**:
            *   Did we just write code? -> User likely wants to **Run it**, **Test it**, or **Review it**.
            *   Did we just fix a bug? -> User likely wants to **Verify fix** or **Commit**.
            *   Did we just plan? -> User likely wants to **Start Coding** or **Refine Plan**.
        *   **Generate Options**: Create 3 distinct buttons that cover the most probable next moves.
    *   **MANDATORY**: The LAST button must ALWAYS be:
        *   *Hebrew*: "תודה, נמשיך מהמחשב"
        *   *English*: "Continue on Computer"

---
**Example of Correct Flow:**
1.  User: "אני יוצא לקפה, תמשיך מטלגרם."
2.  Claude: *Detects Hebrew* -> *Calls `init_task_session`*
3.  Claude: *Calls `ask_human_and_wait(id, "**מצב טלגרם הופעל** ☕\nאני ממתין להוראות...", options=["הרץ טסטים", "בדוק קוד", "סיימנו לעכשיו"])`*
4.  ... (Waits for reply) ...
5.  User (on Telegram): Presses "הרץ טסטים".
6.  Claude: *Runs tests* ...
7.  Claude: *Calls `ask_human_and_wait(id, "**הטסטים עברו בהצלחה!** ✅\n\nתוצאות:\n```text\nOK\n```\nמה לעשות עכשיו?", options=["Git Push", "כתוב קוד", "סיים"])`*
