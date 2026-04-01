# ⬡ JARVIS — Just A Rather Very Intelligent System

> A fully functional AI assistant for macOS powered by Google Gemini 2.0 Flash. 
> Understands and speaks all major Indian languages. Controls your Mac with 18+ tools.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange?style=flat-square)
![macOS](https://img.shields.io/badge/Platform-macOS-black?style=flat-square)

---

## ✨ Features

### 🤖 AI Intelligence
- Powered by **Google Gemini 2.0 Flash** — fast, accurate, internet-aware
- Full **agentic tool use** — Jarvis actually performs tasks, not just talks about them
- Multi-turn **conversation memory** within session
- **Image understanding** — upload photos, screenshots for analysis

### 🌏 Indian Language Support
- Understands and responds in: **Hindi, Marathi, Gujarati, Tamil, Telugu, Kannada, Malayalam, Punjabi, Bengali, English**
- **Voice input** in all Indian languages (via Web Speech API)
- **Voice output / TTS** in all Indian languages (via gTTS)
- Automatically detects your language and responds accordingly

### 💻 Mac Control (18 Tools)
| Tool | Action |
|------|--------|
| `list_files` | Browse directories |
| `read_file` | Read any text file |
| `write_file` | Create/edit files |
| `delete_file` | Delete files/folders |
| `move_file` | Move/rename files |
| `copy_file` | Copy files/folders |
| `create_folder` | Create directories |
| `search_files` | Find files by name |
| `run_command` | Execute terminal commands |
| `open_application` | Launch any Mac app |
| `open_url` | Open URLs in browser |
| `get_system_info` | CPU/RAM/Disk/Battery |
| `get_running_processes` | List active apps |
| `set_reminder` | macOS notifications |
| `take_screenshot` | Capture screen |
| `get_clipboard` | Read clipboard |
| `set_clipboard` | Write to clipboard |
| `speak_text` | Text-to-speech output |

### 🎨 HUD Interface
- Iron Man JARVIS-inspired dark HUD design
- Real-time **system monitor** (CPU, RAM, Disk, Battery)
- **Live file browser** — click to navigate/read
- **Tool execution log** — see every action in real time
- **Live clock** with IST time
- Quick action buttons for common tasks

---

## 🚀 Quick Start

### Option 1: One-click Setup (Recommended)
```bash
git clone https://github.com/YOUR_USERNAME/jarvis-ai.git
cd jarvis-ai
bash setup.sh
```

### Option 2: Manual Setup
```bash
# Clone
git clone https://github.com/YOUR_USERNAME/jarvis-ai.git
cd jarvis-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python3 app.py
```

Then open **http://localhost:5000** in your browser.

---

## 🔑 API Key Setup

The Gemini API key is already included in `.env`. To use your own:

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Create an API key
3. Edit `.env`:
```env
GEMINI_API_KEY=your_key_here
```

---

## 💬 Usage Examples

### English
```
"Open Safari and go to YouTube"
"Show my system info"
"Create a file called notes.txt in my Desktop with today's date"
"What files are in my Downloads folder?"
"Take a screenshot and save it to Desktop"
"Set a reminder in 10 minutes to drink water"
```

### Hindi
```
"मेरे Desktop पर कौन-कौन से files हैं?"
"Safari खोलो और YouTube पर जाओ"
"मेरी battery कितनी है?"
```

### Marathi
```
"माझ्या Desktop वर काय files आहेत?"
"एक screenshot घे"
"system info दाखव"
```

### Upload an image
- Click the 📷 button to attach any image
- Ask: "What is in this image?" or "Describe this screenshot"

---

## 🏗 Project Structure

```
jarvis/
├── app.py              # Main Flask app + Gemini + all tools
├── requirements.txt    # Python dependencies
├── setup.sh           # One-click Mac setup script
├── .env               # API keys (add to .gitignore for production)
├── .gitignore
├── README.md
└── templates/
    └── index.html     # HUD-style frontend
```

---

## 🛠 Requirements

- **macOS** 10.15+
- **Python** 3.9+
- Internet connection (for Gemini API + TTS)
- Browser with microphone access for voice input

---

## ⚙️ Configuration

Edit `app.py` to customize:
- `SYSTEM_PROMPT` — Change Jarvis's personality
- `TOOLS` — Add or remove tools
- `HOME_DIR` — Default directory for file operations

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web server |
| `flask-socketio` | Real-time communication |
| `flask-cors` | Cross-origin support |
| `google-generativeai` | Gemini AI API |
| `gtts` | Google Text-to-Speech for Indian languages |
| `psutil` | System monitoring (CPU, RAM, disk) |
| `eventlet` | Async SocketIO workers |

---

## 🔒 Security Note

This assistant has **full access to your Mac filesystem and can run terminal commands**. 
Only run it on your local machine (localhost). Do not expose port 5000 to the internet.

---

## 🧑‍💻 Built by Anand

BBA LLB Student | Marathwada Mitramandal's Shankarro Chavan College of Law, Pune  
Powered by Google Gemini 2.0 Flash
