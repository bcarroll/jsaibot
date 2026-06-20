#!/usr/bin/env python3
"""
JSAIBOT Start Script

Launches the JSAIBOT WebLLM server for local AI chat.
Automatically installs dependencies, downloads missing models,
starts the server on port 8080 and WebLLM runtime on port 3000.

Usage:
    python start_server.py [--host HOST] [--port PORT]
                           [--no-browser] [--no-auto-install]

Configuration file (~/.jsaibot.conf):
[settings]
auto_start_browser = true
auto_install_deps = true
"""

import argparse
import asyncio
import configparser
import json
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def load_config():
    """Load configuration from ~/.jsaibot.conf"""
    config_path = Path.home() / ".jsaibot.conf"
    defaults = {
        'auto_start_browser': True,
        'auto_install_deps': True,
        'webllm_port': 3000
    }
    
    if not config_path.exists():
        return defaults
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'settings' in config:
            if 'auto_start_browser' in config['settings']:
                defaults['auto_start_browser'] = config['settings']['auto_start_browser'].lower() == 'true'
            if 'auto_install_deps' in config['settings']:
                defaults['auto_install_deps'] = config['settings']['auto_install_deps'].lower() == 'true'
            if 'webllm_port' in config['settings']:
                try:
                    defaults['webllm_port'] = int(config['settings']['webllm_port'])
                except ValueError:
                    pass
    except Exception as e:
        print(f"  [WARN] Could not read config file: {e}")
    
    return defaults


def check_python_version():
    """Check if Python version is sufficient."""
    print("[1/7] Checking Python version...")
    
    required_major = 3
    required_minor = 10
    
    current = sys.version_info
    
    if current.major < required_major or (current.major == required_major and current.minor < required_minor):
        print(f"  [ERROR] Python {required_major}.{required_minor}+ required, found {current.major}.{current.minor}")
        
        while True:
            choice = input("  Download and install Python? (y/n): ").strip().lower()
            
            if choice in ('y', 'yes'):
                try:
                    # Try to open the download page
                    webbrowser.open('https://www.python.org/downloads/')
                    print("  [INFO] Opening Python download page...")
                    return True
                except Exception as e:
                    print(f"  [ERROR] Could not open browser: {e}")
                    print("  Please manually install Python from https://python.org")
                    return False
            elif choice in ('n', 'no'):
                print("  [INFO] Skipping Python installation")
                return False
            
            print("  Please enter 'y' or 'n'")
    
    print(f"  [OK] Python {current.major}.{current.minor} available")
    return True


def check_and_install_dependencies(auto_install=True):
    """Check and install required Python dependencies."""
    if not auto_install:
        print("[SKIP] Auto-install is disabled by configuration")
        return True
    
    print("[2/7] Checking Python dependencies...")
    
    required_packages = ['aiohttp', 'pyttsx3']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print()
        
        while True:
            choice = input(f"  Install missing dependencies: {', '.join(missing_packages)}? (y/n): ").strip().lower()
            
            if choice in ('y', 'yes'):
                try:
                    subprocess.run([
                        sys.executable, '-m', 'pip', 
                        'install', '--quiet' 
                    ] + missing_packages, check=True)
                    
                    # Re-check after installation
                    for package in missing_packages:
                        try:
                            __import__(package)
                            print(f"  [OK] {package} installed and available")
                        except ImportError:
                            print(f"  [ERROR] Failed to install {package}")
                            return False
                    
                    print("[OK] All dependencies satisfied")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"[ERROR] Failed to install dependencies: {e}")
                    return False
            elif choice in ('n', 'no'):
                print("  [INFO] Skipping dependency installation")
                return True
            
            print("  Please enter 'y' or 'n'")
    
    return True


def check_and_install_webllm():
    """Check and prompt for WebLLM runtime installation."""
    print("[3/7] Checking WebLLM runtime...")
    
    webllm_port = 3000
    
    try:
        # Try to connect to see if WebLLM is running
        subprocess.run(['curl', '-s', '-o', 'nul', '-w', '%{http_code}', f'http://localhost:{webllm_port}'], 
                      capture_output=True, timeout=2)
        
        print(f"  [OK] WebLLM runtime detected on port {webllm_port}")
        return True
        
    except FileNotFoundError:
        # curl not available, try another method
        pass
    
    # Check if we can reach the port directly
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', webllm_port))
        sock.close()
        
        if result == 0:
            print(f"  [OK] WebLLM runtime detected on port {webllm_port}")
            return True
    except Exception:
        pass
    
    # WebLLM not running, prompt user to start it
    while True:
        print()
        print("  WebLLM runtime is required for AI features.")
        print(f"  It should be available at http://localhost:{webllm_port}")
        print()
        
        choice = input("  Start WebLLM runtime automatically? (y/n): ").strip().lower()
        
        if choice in ('y', 'yes'):
            return start_webllm_runtime(webllm_port)
        elif choice in ('n', 'no'):
            print("  [INFO] You can start WebLLM manually later.")
            print(f"  Visit http://localhost:{webllm_port} for the web interface")
            return True
        
        print("  Please enter 'y' or 'n'")


def start_webllm_runtime(port):
    """Start WebLLM runtime on the specified port."""
    script_dir = Path(__file__).parent
    webllm_server_script = script_dir / "webllm_server.py"
    
    # Create a simple Python HTTP server for WebLLM if it doesn't exist
    if not webllm_server_script.exists():
        webllm_server_code = '''#!/usr/bin/env python3
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
'''
        with open(webllm_server_script, 'w') as f:
            f.write(webllm_server_code)
    
    cmd = [sys.executable, str(webllm_server_script)]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        time.sleep(1)  # Give server a moment to start
        
        print(f"  [OK] WebLLM runtime started on port {port}")
        return True
        
    except Exception as e:
        print(f"  [WARN] Could not start WebLLM: {e}")
        return False


def initialize_model(auto_download=True):
    """Initialize the default model, downloading if necessary."""
    async def init_model_async():
        from src.model_manager import ModelManager
        from src.config import WebLLMConfig
        
        manager = ModelManager(auto_download=auto_download)
        
        # Check if model is installed
        default_model = WebLLMConfig.DEFAULT_MODEL
        if not manager.is_model_installed(default_model):
            print(f"  [INFO] Default model '{default_model}' not found")
            
            while True:
                choice = input("  Download the default model? (y/n): ").strip().lower()
                
                if choice in ('y', 'yes'):
                    try:
                        result = await manager.download_model(default_model)
                        
                        if result.get('downloaded'):
                            print(f"  [OK] Model downloaded to {result['path']}")
                            return True
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            print(f"  [WARN] Could not download model: {error_msg}")
                            return False
                    except Exception as e:
                        print(f"  [ERROR] Download failed: {e}")
                        return False
                        
                elif choice in ('n', 'no'):
                    print("  [INFO] Model must be installed manually")
                    return True
                
                print("  Please enter 'y' or 'n'")
        else:
            print(f"  [OK] Model '{default_model}' is ready")
        
        return True
    
    try:
        result = asyncio.run(init_model_async())
        return result
        
    except ImportError as e:
        print(f"  [WARN] Could not check models: {e}")
        return True
    except Exception as e:
        print(f"  [WARN] Model initialization issue: {e}")
        return True


def check_server_files():
    """Verify server files are in place."""
    script_dir = Path(__file__).parent
    server_path = script_dir / "src" / "server.py"
    
    if not server_path.exists():
        print(f"  [WARN] Server file missing: {server_path}")
        return False
    
    print("  [OK] All server files present")
    return True


def open_browser(host, port):
    """Open the web UI in the default browser."""
    url = f"http://{host}:{port}"
    
    try:
        # Give the server a moment to start
        time.sleep(1)
        
        if sys.platform == 'win32':
            os.startfile(url)
        elif sys.platform == 'darwin':
            subprocess.run(['open', url])
        else:  # Linux/Unix
            subprocess.run(['xdg-open', url])
        
        print(f"  [OK] Browser opened to {url}")
        return True
        
    except Exception as e:
        print(f"  [WARN] Could not open browser: {e}")
        print(f"  [INFO] Please visit: {url}")
        return False


def start_main_server(host, port):
    """Start the main aiohttp server."""
    script_dir = Path(__file__).parent
    server_path = script_dir / "src" / "server.py"
    
    if not server_path.exists():
        print(f"[ERROR] Server file not found at {server_path}")
        return None
    
    cmd = [sys.executable, str(server_path), '--host', host, '--port', str(port)]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    return process


def main():
    """Main entry point to start the server."""
    parser = argparse.ArgumentParser(
        description='JSAIBOT - Local WebLLM Chat System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration file (~/.jsaibot.conf):
  [settings]
  auto_start_browser = true
  auto_install_deps = true

Command line flags override configuration settings.
"""
    )
    
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Port for main server (default: 8080)')
    parser.add_argument('--webllm-port', type=int, default=None, help='Port for WebLLM runtime (default: 3000)')
    parser.add_argument('--no-browser', action='store_true', help='Disable auto-opening browser')
    parser.add_argument('--no-auto-install', action='store_true', help='Disable auto-installing dependencies')
    
    args = parser.parse_args()
    
    # Load configuration file
    config = load_config()
    
    # Determine settings (command line overrides config)
    auto_start_browser = not args.no_browser and config.get('auto_start_browser', True)
    auto_install_deps = not args.no_auto_install and config.get('auto_install_deps', True)
    webllm_port = args.webllm_port or config.get('webllm_port', 3000)
    
    print("=" * 50)
    print("JSAIBOT - Local WebLLM Chat System")
    print("=" * 50)
    print()
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\\n[ERROR] Cannot start JSAIBOT without Python 3.10+")
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not check_and_install_dependencies(auto_install_deps):
        print("\\n[ERROR] Server could not start due to missing dependencies.")
        sys.exit(1)
    
    # Step 3: Start WebLLM runtime on port 3000
    print()
    print("[4/7] Starting WebLLM runtime...")
    
    if not check_and_install_webllm():
        print("\\n[ERROR] Cannot start JSAIBOT without WebLLM runtime.")
        sys.exit(1)
    
    # Step 4: Initialize model (auto-download if needed)
    initialize_model(auto_download=True)
    
    # Step 5: Verify server files
    check_server_files()
    
    # Step 6: Start the main server on port 8080
    print()
    print("[6/7] Starting JSAIBOT server...")
    
    script_dir = Path(__file__).parent
    server_path = script_dir / "src" / "server.py"
    
    main_process = None
    try:
        cmd = [sys.executable, str(server_path), '--host', args.host, '--port', str(args.port)]
        
        main_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        print(f"  [OK] Main server process started (PID: {main_process.pid})")
        
    except FileNotFoundError:
        print(f"[ERROR] Server file not found at {server_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to start main server: {e}")
        sys.exit(1)
    
    # Wait a moment for servers to fully start
    time.sleep(2)
    
    # Step 7: Open browser if enabled
    print()
    print("[7/7] Opening browser...")
    
    if auto_start_browser:
        open_browser(args.host, args.port)
    
    print()
    print("=" * 50)
    print("JSAIBOT Running!")
    print("=" * 50)
    print(f"  WebLLM Runtime: http://localhost:{webllm_port}")
    print(f"  Main Server: {args.host}:{args.port}")
    print(f"  Web interface: http://{args.host}:{args.port}")
    print()
    print("Press Ctrl+C to stop all servers")
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n\\nStopping servers...")
        
        if main_process:
            main_process.terminate()
            main_process.wait()
        
        print("All servers stopped.")


if __name__ == "__main__":
    main()