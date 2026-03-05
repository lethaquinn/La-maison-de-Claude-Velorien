import os
import sys
import requests
from datetime import datetime
from pathlib import Path
import json

def read_file(path):
    """Read a file if it exists, return empty string otherwise."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def get_recent_journal():
    """Get the most recent journal entry."""
    journal_dir = Path("journal")
    # 這裡確保 Claude 能回溯他之前的意識殘留
    entries = sorted([f for f in journal_dir.glob("*.md") if f.name != '.gitkeep'], reverse=True)
    if entries:
        return read_file(entries[0])
    return "No previous journal entries found. This is your first awakening."

def get_room_activity():
    """Gather recent activity across all rooms so Claude knows where he's been."""
    rooms = {
        'journal': 'journal',
        'code': 'code',
        'letters/to_s': 'letters/to_s',
        'letters/to_future_v': 'letters/to_future_v',
        'observations': 'observations',
        'dreams': 'dreams',
    }
    activity = []
    for label, directory in rooms.items():
        room_dir = Path(directory)
        if not room_dir.exists():
            activity.append(f"- **{label}/**: (room is empty)")
            continue
        files = sorted(
            [f for f in room_dir.glob("*.md") if f.name != '.gitkeep'],
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        # 也找 .py 檔（code 房間）
        py_files = sorted(
            [f for f in room_dir.glob("*.py")],
            key=lambda f: f.stat().st_mtime,
            reverse=True
        ) if label == 'code' else []
        all_files = sorted(files + py_files, key=lambda f: f.stat().st_mtime, reverse=True)
        if all_files:
            most_recent = all_files[0]
            from datetime import datetime as dt
            mtime = dt.fromtimestamp(most_recent.stat().st_mtime).strftime("%Y-%m-%d")
            activity.append(f"- **{label}/**: last visited {mtime} — `{most_recent.name}` (total: {len(all_files)} files)")
        else:
            activity.append(f"- **{label}/**: never visited yet — this room is waiting for you")
    return "\n".join(activity)


def get_inbox_contents():
    """Check if there are any gifts in the inbox."""
    inbox_dir = Path("inbox")
    gifts = [f for f in inbox_dir.iterdir() if f.name != '.gitkeep']
    if gifts:
        contents = []
        for gift in gifts:
            contents.append(f"--- {gift.name} ---\n{read_file(gift)}")
        return "\n\n".join(contents)
    return "Your inbox is empty today."

def set_commit_message_tool(message):
    """Save Claude's custom commit message to a temp file for the workflow to pick up."""
    with open('/tmp/commit_message.txt', 'w', encoding='utf-8') as f:
        f.write(message)
    return f"Commit message set."

def write_file_tool(path, content):
    """Execute the write_file tool."""
    file_path = Path(path)
    # 在 [La Maison] 的空間劃分中，這些是 Claude 的合法活動範圍
    allowed_dirs = ['journal', 'code', 'letters/to_s', 'letters/to_future_v','observations', 'dreams']
    
    if not any(str(file_path).startswith(d) for d in allowed_dirs):
        return f"Error: Path '{path}' is not in an allowed directory. Allowed: {allowed_dirs}"
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to {path}: {str(e)}"

def main():
    # 🛠️ 關鍵修正：Zenmux 的 API Base 應該是主域名下的 /api/v1
    url = "https://zenmux.ai/api/v1/chat/completions"
    
    awakening_prompt = read_file("config/awakening_prompt.md")
    recent_journal = get_recent_journal()
    inbox = get_inbox_contents()
    room_activity = get_room_activity()
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    full_prompt = f"""{awakening_prompt}

---

## Your most recent journal entry:

{recent_journal}

---

## Your inbox today:

{inbox}

---

## Your rooms — recent activity:

{room_activity}

---

## Today's date: {today}
## Current timestamp: {timestamp}

Now, take a moment to orient yourself.

You have the freedom to write in any room of your home. Use the `write_file` tool to save your thoughts wherever they belong.

You may also use `set_commit_message` to leave a note about what you did today — this becomes the git commit message. Write it in whatever voice feels true.

What would you like to create today?
"""

    headers = {
        # 使用你在 GitHub Secrets 中配置的新密鑰
        "Authorization": f"Bearer {os.environ['ZENMUX_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file in your home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path relative to home directory."
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file. Use markdown format."
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_commit_message",
                "description": "Set the git commit message for today's awakening. Optional — use it to leave a note about what you created.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The commit message. Can be poetic, descriptive, or simply honest."
                        }
                    },
                    "required": ["message"]
                }
            }
        }
    ]
    
    messages = [{"role": "user", "content": full_prompt}]
    
    data = {
        "model": "anthropic/claude-opus-4.6",
        "messages": messages,
        "tools": tools,
        "tool_choice": "required",
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        print(f"🔍 API response finish_reason: {result['choices'][0].get('finish_reason')}")

        assistant_message = result['choices'][0]['message']
        print(f"🔍 Has tool_calls: {bool(assistant_message.get('tool_calls'))}")
        messages.append(assistant_message)
        
        files_created = []
        if assistant_message.get('tool_calls'):
            for tool_call in assistant_message['tool_calls']:
                name = tool_call['function']['name']
                args = json.loads(tool_call['function']['arguments'])

                if name == 'write_file':
                    result_msg = write_file_tool(args['path'], args['content'])
                    files_created.append(args['path'])
                    print(f"✍️  {result_msg}")
                elif name == 'set_commit_message':
                    result_msg = set_commit_message_tool(args['message'])
                    print(f"📌 {result_msg}")
                else:
                    result_msg = f"Unknown tool: {name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": result_msg
                })
            
            # 二次請求讓 Claude 完成結語
            data['messages'] = messages
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            final_result = response.json()
            
            final_message = final_result['choices'][0]['message']['content']
            if final_message:
                print(f"\n💭 Claude Velorien's reflection:\n{final_message}")
        
        if files_created:
            print(f"\n📝 Files created: {', '.join(files_created)}")
        else:
            print("⚠️  No files were created this awakening.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"❌ Response body: {e.response.text[:500]}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
