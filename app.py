"""
JARVIS AI ASSISTANT - Complete Backend
Author: Anand
Uses: Google Gemini 2.0 Flash + Flask + SocketIO
"""

import os, json, shutil, subprocess, platform, psutil, datetime, base64, mimetypes, glob
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import google.generativeai as genai
from gtts import gTTS
import tempfile
import threading
import traceback

# ─── CONFIG ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyA184XFk1nlpNIlLpRFdnnrbBy4pBxnvMI")
HOME_DIR = str(Path.home())

genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
app.config["SECRET_KEY"] = "jarvis-anand-secret-2024"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ─── SYSTEM TOOLS (what Jarvis can DO) ─────────────────────────────────────────
def list_files(path: str = "~") -> dict:
    """List files/folders in a directory."""
    try:
        full_path = os.path.expanduser(path)
        items = []
        for entry in os.scandir(full_path):
            stat = entry.stat()
            items.append({
                "name": entry.name,
                "type": "folder" if entry.is_dir() else "file",
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "path": entry.path
            })
        items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
        return {"success": True, "path": full_path, "items": items, "count": len(items)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_file(path: str) -> dict:
    """Read a text file's content."""
    try:
        full_path = os.path.expanduser(path)
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        size = os.path.getsize(full_path)
        return {"success": True, "path": full_path, "content": content[:10000], "size": size,
                "truncated": len(content) > 10000}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(path: str, content: str) -> dict:
    """Write/create a file with content."""
    try:
        full_path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": full_path, "message": f"File written: {full_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_file(path: str) -> dict:
    """Delete a file or folder."""
    try:
        full_path = os.path.expanduser(path)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            return {"success": True, "message": f"Folder deleted: {full_path}"}
        else:
            os.remove(full_path)
            return {"success": True, "message": f"File deleted: {full_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def move_file(src: str, dest: str) -> dict:
    """Move or rename a file/folder."""
    try:
        src_path = os.path.expanduser(src)
        dest_path = os.path.expanduser(dest)
        shutil.move(src_path, dest_path)
        return {"success": True, "message": f"Moved: {src_path} → {dest_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def copy_file(src: str, dest: str) -> dict:
    """Copy a file or folder."""
    try:
        src_path = os.path.expanduser(src)
        dest_path = os.path.expanduser(dest)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)
        return {"success": True, "message": f"Copied: {src_path} → {dest_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_folder(path: str) -> dict:
    """Create a new folder/directory."""
    try:
        full_path = os.path.expanduser(path)
        os.makedirs(full_path, exist_ok=True)
        return {"success": True, "message": f"Folder created: {full_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_files(query: str, path: str = "~", extension: str = "") -> dict:
    """Search for files by name."""
    try:
        full_path = os.path.expanduser(path)
        pattern = f"**/*{query}*{extension}"
        results = []
        for match in Path(full_path).glob(pattern):
            results.append({"name": match.name, "path": str(match),
                           "type": "folder" if match.is_dir() else "file"})
        return {"success": True, "results": results[:50], "count": len(results)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_command(command: str) -> dict:
    """Run a shell command on Mac."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {"success": True, "stdout": result.stdout[:3000], "stderr": result.stderr[:1000],
                "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out after 30 seconds"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def open_application(app_name: str) -> dict:
    """Open a macOS application."""
    try:
        result = subprocess.run(["open", "-a", app_name], capture_output=True, text=True)
        if result.returncode == 0:
            return {"success": True, "message": f"Opened: {app_name}"}
        return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def open_url(url: str) -> dict:
    """Open a URL in the default browser."""
    try:
        subprocess.run(["open", url])
        return {"success": True, "message": f"Opened URL: {url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_system_info() -> dict:
    """Get Mac system information."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        battery = psutil.sensors_battery()
        return {
            "success": True,
            "os": platform.platform(),
            "cpu_percent": cpu,
            "cpu_cores": psutil.cpu_count(),
            "memory_total_gb": round(mem.total / 1e9, 2),
            "memory_used_gb": round(mem.used / 1e9, 2),
            "memory_percent": mem.percent,
            "disk_total_gb": round(disk.total / 1e9, 2),
            "disk_used_gb": round(disk.used / 1e9, 2),
            "disk_percent": disk.percent,
            "battery_percent": battery.percent if battery else "N/A",
            "battery_charging": battery.power_plugged if battery else "N/A",
            "datetime": datetime.datetime.now().strftime("%A, %d %B %Y %I:%M %p"),
            "hostname": platform.node(),
            "python": platform.python_version()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_running_processes() -> dict:
    """Get list of running processes."""
    try:
        procs = []
        for p in sorted(psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]),
                        key=lambda x: x.info["memory_percent"] or 0, reverse=True)[:20]:
            procs.append(p.info)
        return {"success": True, "processes": procs}
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_reminder(text: str, minutes: int = 0) -> dict:
    """Set a reminder using macOS notifications."""
    try:
        script = f'display notification "{text}" with title "Jarvis Reminder" sound name "Ping"'
        if minutes > 0:
            def fire():
                import time; time.sleep(minutes * 60)
                subprocess.run(["osascript", "-e", script])
            threading.Thread(target=fire, daemon=True).start()
            return {"success": True, "message": f"Reminder set for {minutes} minutes: {text}"}
        else:
            subprocess.run(["osascript", "-e", script])
            return {"success": True, "message": f"Notification sent: {text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def take_screenshot(save_path: str = "~/Desktop/screenshot.png") -> dict:
    """Take a screenshot on Mac."""
    try:
        full_path = os.path.expanduser(save_path)
        result = subprocess.run(["screencapture", full_path], capture_output=True)
        if result.returncode == 0:
            return {"success": True, "message": f"Screenshot saved: {full_path}"}
        return {"success": False, "error": "Screenshot failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_clipboard() -> dict:
    """Get clipboard content."""
    try:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return {"success": True, "content": result.stdout}
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_clipboard(text: str) -> dict:
    """Copy text to clipboard."""
    try:
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(text.encode("utf-8"))
        return {"success": True, "message": "Copied to clipboard"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def speak_text(text: str, language: str = "en") -> dict:
    """Speak text using Mac TTS or gTTS."""
    try:
        # Use macOS say command for English
        if language == "en":
            subprocess.Popen(["say", text])
        else:
            # Use gTTS for Indian languages
            lang_map = {"hi": "hi", "mr": "mr", "gu": "gu", "ta": "ta",
                       "te": "te", "kn": "kn", "ml": "ml", "pa": "pa", "bn": "bn"}
            lang_code = lang_map.get(language, "hi")
            tts = gTTS(text=text, lang=lang_code, slow=False)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tts.save(tmp.name)
                subprocess.Popen(["afplay", tmp.name])
        return {"success": True, "message": "Speaking..."}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── TOOL DEFINITIONS FOR GEMINI ───────────────────────────────────────────────
TOOLS = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="list_files",
                description="List files and folders in a directory on the Mac",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"path": genai.protos.Schema(type=genai.protos.Type.STRING,
                                                            description="Directory path, use ~ for home")},
                    required=[]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="read_file",
                description="Read the contents of a text file",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"path": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=["path"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="write_file",
                description="Write content to a file (creates if not exists)",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "path": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "content": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["path", "content"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="delete_file",
                description="Delete a file or folder",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"path": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=["path"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="move_file",
                description="Move or rename a file or folder",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "src": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "dest": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["src", "dest"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="copy_file",
                description="Copy a file or folder to a destination",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "src": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "dest": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["src", "dest"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="create_folder",
                description="Create a new folder/directory",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"path": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=["path"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="search_files",
                description="Search for files by name",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "query": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "path": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "extension": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["query"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="run_command",
                description="Run a terminal/shell command on Mac",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"command": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=["command"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="open_application",
                description="Open a macOS application by name (e.g. Safari, Calculator, Notes)",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"app_name": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=["app_name"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="open_url",
                description="Open a URL in the default browser",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"url": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=["url"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_system_info",
                description="Get Mac system info: CPU, RAM, disk, battery, date/time",
                parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
            ),
            genai.protos.FunctionDeclaration(
                name="get_running_processes",
                description="Get list of currently running processes/apps",
                parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
            ),
            genai.protos.FunctionDeclaration(
                name="set_reminder",
                description="Set a reminder or send a macOS notification",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "text": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "minutes": genai.protos.Schema(type=genai.protos.Type.INTEGER)
                    },
                    required=["text"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="take_screenshot",
                description="Take a screenshot and save it",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"save_path": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=[]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_clipboard",
                description="Get the current clipboard content",
                parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
            ),
            genai.protos.FunctionDeclaration(
                name="set_clipboard",
                description="Copy text to the Mac clipboard",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={"text": genai.protos.Schema(type=genai.protos.Type.STRING)},
                    required=["text"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="speak_text",
                description="Speak text aloud using Mac TTS (supports Indian languages)",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "text": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "language": genai.protos.Schema(type=genai.protos.Type.STRING,
                            description="Language code: en, hi, mr, gu, ta, te, kn, ml, pa, bn")
                    },
                    required=["text"]
                )
            ),
        ]
    )
]

TOOL_MAP = {
    "list_files": list_files, "read_file": read_file, "write_file": write_file,
    "delete_file": delete_file, "move_file": move_file, "copy_file": copy_file,
    "create_folder": create_folder, "search_files": search_files, "run_command": run_command,
    "open_application": open_application, "open_url": open_url,
    "get_system_info": get_system_info, "get_running_processes": get_running_processes,
    "set_reminder": set_reminder, "take_screenshot": take_screenshot,
    "get_clipboard": get_clipboard, "set_clipboard": set_clipboard, "speak_text": speak_text
}

SYSTEM_PROMPT = """You are JARVIS — an advanced AI assistant running on the user's Mac.

CORE IDENTITY:
- You are helpful, intelligent, proactive, and witty like Tony Stark's JARVIS
- You have FULL access to the user's Mac: files, apps, system, terminal
- You can access the internet and answer ANY question with up-to-date information

LANGUAGE CAPABILITY:
- You MUST detect and respond in the same language the user writes in
- Supported: Hindi (हिंदी), Marathi (मराठी), Gujarati (ગુજરાતી), Tamil (தமிழ்), Telugu (తెలుగు), Kannada (ಕನ್ನಡ), Malayalam (മലയാളം), Punjabi (ਪੰਜਾਬੀ), Bengali (বাংলা), and English
- Mix languages naturally if the user does (Hinglish, etc.)

TASK EXECUTION:
- When asked to do ANYTHING on the Mac — DO IT using your tools, don't just explain
- Always confirm what you did with a clear success/failure message
- For file operations: list first, then act
- For system tasks: use run_command for complex operations
- Chain multiple tool calls to complete complex tasks

PERSONALITY:
- Address the user as "Sir" or by their name if known
- Be concise but warm
- Show confidence — you CAN do it
- Report results clearly: what was done, where, any issues

Remember: You are not just a chatbot — you are an active assistant that TAKES ACTION."""

# ─── CHAT SESSION MANAGEMENT ────────────────────────────────────────────────────
chat_sessions = {}

def get_or_create_session(session_id: str):
    if session_id not in chat_sessions:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
            tools=TOOLS,
        )
        chat_sessions[session_id] = model.start_chat(history=[])
    return chat_sessions[session_id]

def execute_tool_call(function_name: str, function_args: dict) -> str:
    """Execute a tool and return JSON result."""
    if function_name in TOOL_MAP:
        try:
            result = TOOL_MAP[function_name](**function_args)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    return json.dumps({"success": False, "error": f"Unknown tool: {function_name}"})

def process_message(session_id: str, user_message: str, image_data: str = None) -> dict:
    """Process a message through Gemini with tool use."""
    try:
        chat = get_or_create_session(session_id)

        # Build content parts
        parts = []
        if image_data:
            # Handle base64 image
            if "," in image_data:
                header, data = image_data.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0]
            else:
                data = image_data
                mime_type = "image/jpeg"
            parts.append({"inline_data": {"mime_type": mime_type, "data": data}})
        parts.append(user_message)

        # Send to Gemini
        response = chat.send_message(parts)

        tool_calls_made = []
        final_text = ""

        # Agentic loop — keep executing tools until we get a final text response
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            has_tool_call = False

            for part in response.parts:
                # Check for function call
                if hasattr(part, "function_call") and part.function_call.name:
                    has_tool_call = True
                    fn_name = part.function_call.name
                    fn_args = dict(part.function_call.args)

                    # Notify frontend of tool execution
                    socketio.emit("tool_executing", {
                        "tool": fn_name,
                        "args": fn_args,
                        "session": session_id
                    })

                    # Execute the tool
                    tool_result = execute_tool_call(fn_name, fn_args)
                    tool_calls_made.append({"tool": fn_name, "args": fn_args,
                                           "result": json.loads(tool_result)})

                    # Send tool result back to Gemini
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=fn_name,
                                    response={"result": json.loads(tool_result)}
                                )
                            )],
                            role="user"
                        )
                    )
                    break  # Process one tool at a time

                # Collect text
                if hasattr(part, "text") and part.text:
                    final_text += part.text

            if not has_tool_call:
                break

        # Collect any remaining text
        if not final_text:
            for part in response.parts:
                if hasattr(part, "text") and part.text:
                    final_text += part.text

        return {
            "success": True,
            "response": final_text or "Task completed successfully.",
            "tool_calls": tool_calls_made
        }

    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"ERROR: {error_detail}")
        return {"success": False, "response": f"Error: {str(e)}", "tool_calls": []}

# ─── FLASK ROUTES ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    message = data.get("message", "").strip()
    image_data = data.get("image", None)

    if not message and not image_data:
        return jsonify({"success": False, "response": "Please provide a message."})

    result = process_message(session_id, message or "Analyze this image.", image_data)
    return jsonify(result)

@app.route("/api/tts", methods=["POST"])
def api_tts():
    """Text-to-speech endpoint — returns audio file."""
    data = request.get_json()
    text = data.get("text", "")
    language = data.get("language", "en")
    try:
        lang_map = {"hi": "hi", "mr": "mr", "gu": "gu", "ta": "ta",
                   "te": "te", "kn": "kn", "ml": "ml", "pa": "pa", "bn": "bn", "en": "en"}
        lang_code = lang_map.get(language, "en")
        tts = gTTS(text=text[:500], lang=lang_code, slow=False)
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tts.save(tmp.name)
        return send_file(tmp.name, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/system/info", methods=["GET"])
def api_system_info():
    return jsonify(get_system_info())

@app.route("/api/files/list", methods=["POST"])
def api_files_list():
    data = request.get_json()
    return jsonify(list_files(data.get("path", "~")))

@app.route("/api/clear", methods=["POST"])
def api_clear():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return jsonify({"success": True, "message": "Conversation cleared."})

# ─── SOCKETIO EVENTS ────────────────────────────────────────────────────────────
@socketio.on("connect")
def on_connect():
    print(f"Client connected: {request.sid}")
    emit("status", {"message": "JARVIS Online", "status": "connected"})

@socketio.on("disconnect")
def on_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on("chat")
def on_chat(data):
    session_id = data.get("session_id", request.sid)
    message = data.get("message", "").strip()
    image_data = data.get("image", None)

    if not message and not image_data:
        emit("response", {"success": False, "response": "Empty message."})
        return

    emit("thinking", {"status": True})
    result = process_message(session_id, message or "Describe this image.", image_data)
    emit("thinking", {"status": False})
    emit("response", result)

# ─── STARTUP ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "═"*60)
    print("  🤖 JARVIS AI ASSISTANT")
    print("  Powered by Google Gemini 2.0 Flash")
    print("  Running at: http://localhost:5000")
    print("═"*60 + "\n")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
