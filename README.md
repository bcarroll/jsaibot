# JSAIBOT

A communication/chat system that integrates a locally downloaded WebLLM model for AI-powered responses.

## Overview

JSAIBOT is designed to leverage locally hosted WebLLM models to provide AI-driven chat functionality within a communication system. This approach ensures data privacy and allows for offline operation while utilizing powerful language models.

**Note:** This project provides the Python client API for communicating with WebLLM, but does not include the WebLLM server itself.

## Prerequisites

Before using JSAIBOT, you need to have a WebLLM instance running:

1. **Install WebLLM** from [mlc-ai/web-llm](https://github.com/mlc-ai/web-llm)
2. **Run the WebLLM server:**
   ```bash
   # After cloning and setting up WebLLM
   python -m web_llm --model <your-model-path> --host 0.0.0.0 --port 3000
   ```

## Features

- Local WebLLM model integration via Python API
- Async HTTP REST client communication
- Streaming response support for real-time output
- Conversation history management
- Health check and model information endpoints

## Project Structure

```
JSAIBOT/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── webllm_client.py     # Main WebLLM client API
│   └── config.py            # Configuration module
├── example_chat.py          # Usage examples
├── requirements.txt         # Python dependencies
└── .env.example            # Environment configuration template
```

## Installation

```bash
# Clone this repository
git clone <your-repo-url>
cd JSAIBOT

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

1. **Start WebLLM server** (separate from this project) on port 3000:
   ```bash
   python -m web_llm --model <your-model> --port 3000
   ```

2. **Test the connection:**
   ```python
   import asyncio
   from src.webllm_client import WebLLMClient

   async def main():
       client = WebLLMClient()
       if await client.health_check():
           response = await client.generate_response("Hello!")
           print(response)
   
   asyncio.run(main())
   ```

3. **Run examples:**
   ```bash
   python example_chat.py
   ```

## Configuration

Copy `.env.example` to `.env` and update with your WebLLM instance settings:

```
WEBLLM_HOST=localhost
WEBLLM_PORT=3000
MODEL_PATH=/path/to/model
MAX_NEW_TOKENS=256
TEMPERATURE=0.7
HISTORY_SIZE=10
```

## API Reference

### WebLLMClient

```python
client = WebLLMClient(host="localhost", port=3000)

# Generate response (non-streaming)
response = await client.generate_response("Your message")

# Stream responses token-by-token
async for token in client.stream_response("Your message"):
    print(token, end="", flush=True)

# Check server health
if await client.health_check():
    print("WebLLM is running!")

# Manage conversation history
client.clear_history()
```

## License

[To be determined]