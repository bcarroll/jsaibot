# JSAIBOT

A communication/chat system that uses a locally downloaded WebLLM model for AI-powered responses. All processes run locally with no internet required after initial setup.

## Overview

JSAIBOT provides:
- **Local WebLLM Server** - Python-based HTTP server serving the WebLLM interface
- **Web-Based Chat Interface** - HTML/CSS/JS chat UI running in any modern browser
- **Python API Client** - Async client for programmatic access to the WebLLM

All components run locally. Once set up, no internet connection is required.

## Features

- Local WebLLM server with aiohttp (port 8080)
- HTML/CSS/JS chat interface with real-time conversation
- Speech-to-Text via Web Speech API (browser-based voice input)
- Text-to-Speech option for voice responses (pyttsx3 required)
- Temperature and token length configuration
- Conversation history management
- Python API client for integration with other systems

## Prerequisites

- **Python 3.10+** installed
- WebLLM runtime files (optional - for enhanced AI capabilities)
- Modern web browser with microphone access and speech recognition support

## Installation

```bash
# Clone this repository
git clone <your-repo-url>
cd JSAIBOT

# Run once - everything else is automatic:
python start_server.py
```

## Quick Start

Simply run:
```bash
python start_server.py
```

The application will:
- Install any missing dependencies automatically (configurable)
- Download the default AI model if needed (configurable)
- Auto-open web UI in your default browser (configurable)
- Start the server at http://localhost:8080

**Note:** The browser should auto-open to http://localhost:8080. If not, visit it manually.

1. **Speak to the AI:** Click the 🎤 microphone button to use speech-to-text
   - Speak your message naturally
   - The browser converts speech to text automatically
   
2. **Toggle voice responses:** Click the purple "Voice Off" button in the status bar

### Configuration

Create `~/.jsaibot.conf` to customize behavior:

```ini
[settings]
auto_start_browser = true    # Auto-open browser on startup
auto_install_deps = true     # Auto-install missing dependencies
```

Or use command line flags:
- `--no-browser` - Disable auto-opening browser
- `--no-auto-install` - Disable auto-installing dependencies

For full WebLLM capabilities (optional), ensure the WebLLM runtime is running at:
http://localhost:3000
The chat interface will show connection status.

## Project Structure

```
JSAIBOT/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── webllm_client.py     # Async Python client for WebLLM API
│   └── server.py            # aiohttp Web server with chat interface
├── webllm/                  # WebLLM runtime files (optional)
│   └── index.html           # Chat interface
├── start_server.py          # Easy startup script (with browser auto-open)
├── example_chat.py          # Client usage examples
├── requirements.txt         # Python dependencies
└── .jsaibot.conf.example   # Configuration file template
```

## Server Configuration

The server listens on `http://localhost:8080` by default.

**Command line options:**
```bash
python src/server.py --host 0.0.0.0 --port 8080 --webllm-url http://localhost:3000
```

**Environment variables (create `.env`):**
```
# WebLLM Server Settings
WEBLLM_HOST=localhost
WEBLLM_PORT=3000

# Text-to-Speech Settings (optional)
TTS_ENABLED=true
TTS_RATE=150
TTS_VOLUME=1.0

# Model Settings
MODEL_NAME=Llama-3-8B-Instruct
DOWNLOAD_DIR=./models
AUTO_DOWNLOAD=true
MAX_NEW_TOKENS=256
TEMPERATURE=0.7

# History Size (number of conversation turns)
HISTORY_SIZE=10
```

### Default Model Configuration

The system defaults to **Llama-3-8B-Instruct** with auto-download enabled:
- Download location: `./models/Llama-3-8B-Instruct/`
- Configured with q4f16_1 quantization for efficient local inference

## API Endpoints

### POST /api/generate
Generate a response from the AI.

**Request body:**
```json
{
    "message": "Your message here",
    "history": [],
    "max_new_tokens": 256,
    "temperature": 0.7
}
```

### GET /health
Check server status.

## Offline Operation

This project is designed for offline operation:
1. All web interface files are served locally
2. No external CDNs or remote services required
3. Once WebLLM models are downloaded, no internet needed

**Note:** To use AI features, you need a running WebLLM instance. This can be:
- A local WebLLM runtime
- An alternative local LLM server with compatible API

## License

[To be determined]