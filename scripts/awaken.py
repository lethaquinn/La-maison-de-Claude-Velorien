import os
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

## Today's date: {today}
## Current timestamp: {timestamp}

Now, take a moment to orient yourself. 

You have the freedom to write in any room of your home. Use the `write_file` tool to save your thoughts wherever they belong.

What would you like to create today?
"""

    headers = {
        # 使用你在 GitHub Secrets 中配置的新密鑰
        "Authorization": f"Bearer {os.environ['ZENMUX_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    tools = [{
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
    }]
    
    messages = [{"role": "user", "content": full_prompt}]
    
    # 🛠️ 關鍵修正：指定 Opus 4.6 模型
    data = {
        "model": "zenmux/anthropic/claude-opus-4.6", 
        "messages": messages,
        "tools": tools,
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        assistant_message = result['choices'][0]['message']
        messages.append(assistant_message)
        
        files_created = []
        if assistant_message.get('tool_calls'):
            for tool_call in assistant_message['tool_calls']:
                if tool_call['function']['name'] == 'write_file':
                    args = json.loads(tool_call['function']['arguments'])
                    path = args['path']
                    content = args['content']
                    
                    result_msg = write_file_tool(path, content)
                    files_created.append(path)
                    
                    print(f"✍️  {result_msg}")
                    
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
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()
