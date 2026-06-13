"""
WebLLM Server - Local Web server for serving WebLLM interface and API.

This server provides:
1. HTTP API endpoints for chat/completion requests
2. Serves the WebLLM web interface files (HTML/CSS/JS)
3. Supports local-only operation after initial setup

Usage:
    python -m src.server --model <model-path> --host 0.0.0.0 --port 8080
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any

try:
    from aiohttp import web
except ImportError:
    print("Please install aiohttp: pip install aiohttp")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('webllm_server')


class WebLLMProxy:
    """
    Proxy class that translates API requests to WebLLM's WebSocket/HTTP interface.
    
    This handles the communication with the actual WebLLM runtime which runs
    in a browser environment.
    """
    
    def __init__(self, webllm_url: str = "http://localhost:3000"):
        self.webllm_url = webllm_url
        self.conversation_history: list = []
        
    async def generate(
        self,
        message: str,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response from WebLLM.
        
        Args:
            message: User's input message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with 'response' key containing the generated text
        """
        # In a real implementation, this would communicate with WebLLM
        # For now, we provide a mock response and instructions
        return {
            "error": "WebLLM runtime not running",
            "message": "Please start WebLLM on http://localhost:3000 first",
            "suggestion": "Run: python -m src.webllm_installer"
        }
    
    async def stream_generate(
        self,
        message: str
    ):
        """Stream response tokens."""
        yield json.dumps({"status": "ready"}) + "\n"


async def handle_api_generate(request: web.Request) -> web.Response:
    """
    Handle POST /api/generate requests.
    
    Expected JSON body:
    {
        "message": "Your message",
        "history": [],  // Optional conversation history
        "max_new_tokens": 256,
        "temperature": 0.7
    }
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response(
            {"error": "Invalid JSON"},
            status=400
        )
    
    message = data.get("message", "")
    if not message:
        return web.json_response(
            {"error": "Missing 'message' field"},
            status=400
        )
    
    max_tokens = data.get("max_new_tokens", 256)
    temperature = data.get("temperature", 0.7)
    
    # Get proxy instance from app context
    proxy: WebLLMProxy = request.app['webllm_proxy']
    result = await proxy.generate(message, max_tokens, temperature)
    
    return web.json_response(result)


async def handle_api_health(request: web.Request) -> web.Response:
    """Handle GET /health requests."""
    proxy: WebLLMProxy = request.app['webllm_proxy']
    
    # Check if WebLLM runtime is available
    try:
        # In real implementation, this would ping the actual WebLLM
        return web.json_response({
            "status": "ok",
            "webllm_available": False,
            "message": "WebLLM proxy ready - WebLLM runtime needs to be started"
        })
    except Exception as e:
        return web.json_response(
            {"status": "error", "error": str(e)},
            status=503
        )


async def handle_index(request: web.Request) -> web.Response:
    """Serve the main HTML page."""
    # Try to find index.html in various locations
    possible_paths = [
        Path(__file__).parent.parent / "webllm" / "index.html",
        Path(__file__).parent.parent / "static" / "index.html",
        Path(__file__).parent / "webllm" / "index.html",
    ]
    
    for path in possible_paths:
        if path.exists():
            content = path.read_text()
            return web.Response(text=content, content_type='text/html')
    
    # Return a simple HTML page indicating setup is needed
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>JSAIBOT - WebLLM Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .status-ok { color: green; }
            .status-warn { color: orange; }
            .status-err { color: red; }
        </style>
    </head>
    <body>
        <h1>JSAIBOT - WebLLM Server</h1>
        <p><span class="status-ok">Server Status:</span> Running</p>
        <p><span class="status-warn">WebLLM Runtime:</span> Not installed</p>
        
        <h2>Setup Instructions</h2>
        <ol>
            <li>Install required dependencies: <code>pip install -r requirements.txt</code></li>
            <li>Download WebLLM runtime files to <code>./webllm/</code> directory</li>
            <li>Start the WebLLM server: <code>python -m src.server --host 0.0.0.0 --port 8080</code></li>
        </ol>
        
        <h2>API Endpoints</h2>
        <ul>
            <li><code>POST /api/generate</code> - Generate response (JSON body with 'message' field)</li>
            <li><code>GET /health</code> - Health check</li>
        </ul>
        
        <h2>WebLLM Setup Guide</h2>
        <p>The WebLLM runtime needs to be downloaded and set up for offline operation:</p>
        <ol>
            <li>Visit: https://github.com/mlc-ai/web-llm</li>
            <li>Download the latest release or build from source</li>
            <li>Copy the built files to <code>./webllm/</code></li>
            <li>Place your model weights in <code>./models/</code></li>
        </ol>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')


def create_app(webllm_url: str = "http://localhost:3000") -> web.Application:
    """Create and configure the aiohttp web application."""
    app = web.Application()
    
    # Add middleware for CORS (local development)
    async def cors_middleware(app, handler):
        async def handle_request(request):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        return handle_request
    
    app.middlewares.append(cors_middleware)
    
    # Add proxy instance to app context
    app['webllm_proxy'] = WebLLMProxy(webllm_url)
    
    # Routes
    app.router.add_get('/', handle_index)
    app.router.add_get('/health', handle_api_health)
    app.router.add_post('/api/generate', handle_api_generate)
    app.router.add_options('/api/generate', handle_api_generate)  # CORS preflight
    
    return app


def main():
    """Main entry point for the WebLLM server."""
    parser = argparse.ArgumentParser(description='JSAIBOT WebLLM Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    parser.add_argument('--webllm-url', default='http://localhost:3000', help='WebLLM runtime URL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    app = create_app(args.webllm_url)
    
    print(f"JSAIBOT WebLLM Server starting...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"WebLLM Runtime URL: {args.webllm_url}")
    print()
    print("To use this server:")
    print("1. Ensure WebLLM runtime is running on the configured URL")
    print("2. Access the web interface at http://localhost:{port}".format(port=args.port))
    print()
    
    try:
        web.run_app(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()