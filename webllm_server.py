#!/usr/bin/env python3
"""Simple WebLLM HTTP server."""
import http.server
import socketserver
from pathlib import Path

WEBLLM_DIR = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEBLLM_DIR), **kwargs)

PORT = 3000

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"WebLLM server running at http://localhost:{PORT}")
    httpd.serve_forever()
