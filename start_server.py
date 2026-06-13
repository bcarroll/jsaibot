#!/usr/bin/env python3
"""
JSAIBOT Start Script

Launches the JSAIBOT WebLLM server for local AI chat.

Usage:
    python start_server.py [--host HOST] [--port PORT]
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Main entry point to start the server."""
    print("=" * 50)
    print("JSAIBOT - Local WebLLM Chat System")
    print("=" * 50)
    print()
    
    # Check if aiohttp is installed
    try:
        import aiohttp
        print("[OK] aiohttp is installed")
    except ImportError:
        print("[ERROR] aiohttp is not installed!")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    print("Starting JSAIBOT server...")
    print("- Server will be available at http://localhost:8080")
    print("- Chat interface will load in your browser")
    print("- WebLLM runtime should be running on http://localhost:3000")
    print()
    
    # Get the script directory
    script_dir = Path(__file__).parent
    server_path = script_dir / "src" / "server.py"
    
    if not server_path.exists():
        print(f"[ERROR] Server file not found at {server_path}")
        sys.exit(1)
    
    # Start the server
    try:
        subprocess.run([sys.executable, str(server_path)])
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()