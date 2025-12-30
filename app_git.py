import os
import gradio as gr
from openai import OpenAI
import base64
from pathlib import Path

# 配置 API
api_key = "在这里填入你的api"
client = OpenAI(
    base_url="在这里填入你的url",
    api_key=api_key,
)

#注意！上面的信息需自己填写！
#注意！上面的信息需自己填写！
#注意！上面的信息需自己填写！
#注意！上面的信息需自己填写！
#注意！上面的信息需自己填写！
#注意！上面的信息需自己填写！
#剩下的不用管
# 支持的图片和文本文件扩展名
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
TEXT_EXTS = {'.py', '.c', '.cpp', '.h', '.hpp', '.yml', '.yaml', '.json', '.txt', '.md', 
             '.js', '.ts', '.java', '.go', '.rs', '.rb', '.php', '.sh', '.bat', '.xml', 
             '.html', '.css', '.sql', '.r', '.m', '.swift', '.kt', '.scala', '.lua'}

def get_image_mime(ext):
    """根据扩展名获取MIME类型"""
    mime_map = {'.jpg': 'jpeg', '.jpeg': 'jpeg', '.png': 'png', '.gif': 'gif', 
                '.bmp': 'bmp', '.webp': 'webp'}
    return mime_map.get(ext.lower(), 'jpeg')

def encode_image(image_path):
    """将图片转换为 base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def read_text_file(file_path):
    """读取文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            return f"[读取失败: {os.path.basename(file_path)}]"

def collect_files(path):
    """收集文件或文件夹中的所有支持的文件"""
    files = []
    p = Path(path)
    if p.is_file():
        ext = p.suffix.lower()
        if ext in IMAGE_EXTS or ext in TEXT_EXTS:
            files.append(str(p))
    elif p.is_dir():
        for item in p.rglob('*'):
            if item.is_file():
                ext = item.suffix.lower()
                if ext in IMAGE_EXTS or ext in TEXT_EXTS:
                    files.append(str(item))
    return files

def chat(message, history):
    """处理对话"""
    content = []
    file_contents = []
    file_list = []
    
    # 处理多模态输入
    if isinstance(message, dict):
        # 处理文件
        if "files" in message and message["files"]:
            for file_obj in message["files"]:
                try:
                    file_path = file_obj if isinstance(file_obj, str) else file_obj.name
                    all_files = collect_files(file_path)
                    for f in all_files:
                        ext = Path(f).suffix.lower()
                        file_name = os.path.basename(f)
                        if ext in IMAGE_EXTS:
                            mime = get_image_mime(ext)
                            content.append({
                                "type": "input_image",
                                "image_url": f"data:image/{mime};base64,{encode_image(f)}"
                            })
                            file_list.append(f"🖼️ {file_name}")
                        elif ext in TEXT_EXTS:
                            file_content = read_text_file(f)
                            if file_content:
                                file_contents.append(f"文件: {file_name}\n```\n{file_content}\n```")
                                file_list.append(f"📄 {file_name}")
                except Exception as e:
                    file_list.append(f"❌ {os.path.basename(file_path)}: {str(e)}")
        # 添加文本
        text = message.get("text", "")
    else:
        text = message
    
    # 组合文件内容和用户文本
    full_text = ""
    if file_contents:
        full_text = "\n\n".join(file_contents) + "\n\n"
    if text:
        full_text += text
    
    if full_text:
        content.append({
            "type": "input_text",
            "text": full_text
        })
    
    if not content:
        return "请输入消息或上传文件", file_list
    
    # 构建完整的对话历史
    messages = []
    for msg in history:
        role = msg["role"]
        msg_content = msg["content"]
        messages.append({
            "role": role,
            "content": [{"type": "input_text", "text": msg_content}]
        })
    
    # 添加当前用户消息
    messages.append({"role": "user", "content": content})
    
    try:
        response = client.responses.create(
            model="doubao-seed-1-6-vision-250815",
            input=messages
        )
        message = response.output[1]
        return message.content[0].text, file_list
    except Exception as e:
        return f"❌ API调用失败: {str(e)}", file_list

# 创建 Gradio 界面
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 你看你吗呢？")
    
    chatbot = gr.Chatbot(
        height=500,
        type="messages",
        avatar_images=(None, "🤖"),
        latex_delimiters=[
            {"left": "$$", "right": "$$", "display": True},
            {"left": "\\[", "right": "\\]", "display": True},
            {"left": "$", "right": "$", "display": False},
            {"left": "\\(", "right": "\\)", "display": False}
        ],
        render_markdown=True
    )
    
    msg = gr.MultimodalTextbox(
        placeholder="输入消息... (Enter发送，Shift+Enter换行)",
        show_label=False,
        file_count="multiple",
        file_types=["image", ".py", ".c", ".cpp", ".h", ".hpp", ".yml", ".yaml", ".json", ".txt", ".md", ".js", ".ts", ".java", ".go", ".rs", ".rb", ".php", ".sh", ".bat", ".xml", ".html", ".css", ".sql", ".r", ".m", ".swift", ".kt", ".scala", ".lua"]
    )
    
    with gr.Row():
        clear = gr.Button("清空")
    
    def respond(message, chat_history):
        # 验证输入
        if not message:
            return None, chat_history
        
        text = message.get("text", "") if isinstance(message, dict) else message
        files = message.get("files", []) if isinstance(message, dict) else []
        
        if not text.strip() and not files:
            gr.Warning("请输入消息或上传文件")
            return None, chat_history
        
        # 构建消息对象
        msg_obj = {"text": text or "", "files": files or []}
        
        bot_message, file_list = chat(msg_obj, chat_history)
        
        # 构建用户消息显示
        user_display = text or ""
        if file_list:
            user_display = "\n".join(file_list) + ("\n\n" + text if text else "")
        
        chat_history.append({"role": "user", "content": user_display})
        chat_history.append({"role": "assistant", "content": bot_message})
        
        return None, chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: (None, []), None, [msg, chatbot])

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
