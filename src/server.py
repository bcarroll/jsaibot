"""
WebLLM Server - Local Web server for serving WebLLM interface and API.

This server provides:
1. HTTP API endpoints for chat/completion requests
2. Serves the WebLLM web interface files (HTML/CSS/JS)
3. Supports local-only operation after initial setup

Usage:
    python src/server.py --host 0.0.0.0 --port 8080
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

# Import local modules (use relative imports for embedded mode)
try:
    from .config import WebLLMConfig, default_config
    from .model_manager import ModelManager
except ImportError:
    from config import WebLLMConfig, default_config
    from model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('webllm_server')


class WebLLMProxy:
    """
    Proxy class that translates API requests to WebLLM's WebSocket/HTTP interface.
    
    This handles communication with the actual WebLLM runtime and manages
    model installation using ModelManager.
    """
    
    def __init__(self, webllm_url: str = "http://localhost:3000", config: WebLLMConfig = None):
        self.webllm_url = webllm_url
        self.conversation_history: list = []
        
        # Initialize model manager with auto-download enabled
        self.config = config or default_config
        self.model_manager = ModelManager(
            download_dir=self.config.download_dir,
            auto_download=True
        )
    
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
        # Ensure model is installed before attempting generation
        try:
            await self.model_manager.ensure_model_installed(self.config.model_name)
            
            # In a real implementation, this would communicate with WebLLM
            # For now, we provide a mock response and instructions
            return {
                "response": f"[AI Response Mode]\n\nThis JSAIBOT instance is running but the WebLLM runtime (required for AI generation) is not connected.\n\nTo use full AI features:\n1. Install WebLLM from https://github.com/mlc-ai/web-llm\n2. Start WebLLM on {self.webllm_url}\n3. Return here to chat with the AI!\n\nFor now, this serves as a demo of the JSAIBOT interface.",
                "model_configured": self.config.model_name,
                "webllm_required": True
            }
        except Exception as e:
            return {
                "response": f"[AI Response Mode]\n\nError: {str(e)}\n\nThis instance is running but WebLLM runtime is not connected.",
                "model_configured": self.config.model_name,
                "webllm_required": True
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
            "model_configured": proxy.config.model_name,
            "message": f"WebLLM proxy ready - WebLLM runtime needs to be started at {proxy.webllm_url}"
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
        <meta charset="UTF-8">
        <title>JSAIBOT - WebLLM Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }
            h1 { color: #2c3e50; }
            .status-ok { color: green; font-weight: bold; }
            .status-warn { color: orange; font-weight: bold; }
            .status-err { color: red; font-weight: bold; }
            code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
            ul { line-height: 1.8; }
        </style>
    </head>
    <body>
        <h1>JSAIBOT - WebLLM Server</h1>
        <p>A local AI chat system using WebLLM</p>
        
        <div style="padding: 15px; background-color: #f9f9f9; border-radius: 8px; margin-top: 20px;">
            <p><span class="status-ok">Server Status:</span> Running on http://localhost:{port}</p>
            <p><span class="status-warn">WebLLM Runtime:</span> Not running</p>
            <p><span class="status-warn">Model Status:</span> Auto-download enabled (Llama-3-8B-Instruct)</p>
        </div>
        
        <h2>Quick Start</h2>
        <ol>
            <li>Install dependencies: <code>pip install -r requirements.txt</code></li>
            <li>Start the server: <code>python src/server.py --host 0.0.0.0 --port 8080</code></li>
            <li>Open your browser to <a href="http://localhost:8080">http://localhost:8080</a></li>
            <li>For full AI capabilities, download WebLLM from <a href="https://github.com/mlc-ai/web-llm" target="_blank">mlc-ai/web-llm</a></li>
        </ol>
        
        <h2>API Endpoints</h2>
        <ul>
            <li><code>GET /health</code> - Server health status</li>
            <li><code>POST /api/generate</code> - Send message for AI response</li>
        </ul>
        
        <h3>/api/generate Request:</h3>
        <pre>{
    "message": "Your question here",
    "max_new_tokens": 256,
    "temperature": 0.7
}</pre>
        
        <h2>Configuration</h2>
        <p>Create a <code>.env</code> file to customize settings:</p>
        <pre>WEBLLM_HOST=localhost
WEBLLM_PORT=3000
MODEL_NAME=Llama-3-8B-Instruct
AUTO_DOWNLOAD=true</pre>
    </body>
    </html>
    """.format(port=request.app.get('config', {}).get('port', 8080))
    
    return web.Response(text=html_content, content_type='text/html')


async def handle_api_models(request: web.Request) -> web.Response:
    """Handle GET /api/models to list installed models."""
    proxy: WebLLMProxy = request.app['webllm_proxy']
    models = proxy.model_manager.get_installed_models()
    return web.json_response({"models": models, "default": proxy.config.model_name})


def create_app(config: WebLLMConfig = None) -> web.Application:
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
    
    # Add config and proxy to app context
    app['config'] = config or default_config
    app['webllm_proxy'] = WebLLMProxy(
        webllm_url="http://localhost:3000",  # WebLLM runtime runs on port 3000 (not server port)
        config=config
    )
    
    # Routes
    app.router.add_get('/', handle_index)
    app.router.add_get('/health', handle_api_health)
    app.router.add_post('/api/generate', handle_api_generate)
    app.router.add_get('/api/models', handle_api_models)
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
    
    # Create config with command-line options
    config = WebLLMConfig(host=args.host, port=args.port)
    
    app = create_app(config)
    
    print(f"JSAIBOT WebLLM Server starting...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"WebLLM Runtime URL: {args.webllm_url}")
    print()
    print("To use this server:")
    print("1. Ensure WebLLM runtime is running on the configured URL")
    print("2. Access the web interface at http://localhost:{port}".format(port=args.port))
    print(f"3. Default model: {config.model_name}")
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