#!/usr/bin/env python3
"""
JSAIBOT Start Script

Launches the JSAIBOT WebLLM server for local AI chat.
Automatically installs dependencies, downloads missing models,
and starts the server with minimal user intervention.

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
import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def load_config():
    """Load configuration from ~/.jsaibot.conf"""
    config_path = Path.home() / ".jsaibot.conf"
    defaults = {
        'auto_start_browser': True,
        'auto_install_deps': True
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
    except Exception as e:
        print(f"  [WARN] Could not read config file: {e}")
    
    return defaults


def check_and_install_dependencies(auto_install=True):
    """Check and install required Python dependencies."""
    if not auto_install:
        print("[SKIP] Auto-install is disabled by configuration")
        return True
    
    print("[1/5] Checking dependencies...")
    
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
        print("[INFO] Installing missing dependencies...")
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
    
    return True


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
            
            if auto_download:
                print("  [INFO] Downloading model...")
                
                result = await manager.download_model(default_model)
                
                if result.get('downloaded'):
                    print(f"  [OK] Model downloaded to {result['path']}")
                    return True
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"  [WARN] Could not download model: {error_msg}")
                    return False
            else:
                print("  [INFO] Auto-download disabled - model must be installed manually")
                return True
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
    index_path = script_dir / "webllm" / "index.html"
    
    issues = []
    
    if not server_path.exists():
        issues.append(f"Server file missing: {server_path}")
    
    if not index_path.exists():
        issues.append(f"Web interface missing: {index_path}")
    
    if issues:
        for issue in issues:
            print(f"  [WARN] {issue}")
        return False
    
    print("  [OK] All server files present")
    return True


def open_browser(host, port):
    """Open the web UI in the default browser."""
    url = f"http://{host}:{port}"
    
    try:
        # Give the server a moment to start
        import time
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


def start_server(host='localhost', port=8080, no_browser=False):
    """Start the aiohttp server."""
    script_dir = Path(__file__).parent
    server_path = script_dir / "src" / "server.py"
    
    if not server_path.exists():
        print(f"[ERROR] Server file not found at {server_path}")
        return False
    
    # Start the server with host and port arguments
    cmd = [sys.executable, str(server_path), '--host', host, '--port', str(port)]
    
    process = subprocess.run(cmd)
    return True


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
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    parser.add_argument('--no-browser', action='store_true', help='Disable auto-opening browser')
    parser.add_argument('--no-auto-install', action='store_true', help='Disable auto-installing dependencies')
    
    args = parser.parse_args()
    
    # Load configuration file
    config = load_config()
    
    # Determine settings (command line overrides config)
    auto_start_browser = not args.no_browser and config.get('auto_start_browser', True)
    auto_install_deps = not args.no_auto_install and config.get('auto_install_deps', True)
    
    print("=" * 50)
    print("JSAIBOT - Local WebLLM Chat System")
    print("=" * 50)
    print()
    
    # Step 1: Check and install dependencies
    if not check_and_install_dependencies(auto_install_deps):
        print("\n[ERROR] Server could not start due to missing dependencies.")
        sys.exit(1)
    
    # Step 2: Initialize model (auto-download if needed)
    initialize_model(auto_download=True)
    
    # Step 3: Verify server files
    check_server_files()
    
    # Step 4: Start the server in background
    print()
    print("[4/5] Starting JSAIBOT server...")
    
    script_dir = Path(__file__).parent
    server_path = script_dir / "src" / "server.py"
    
    try:
        import time
        
        # Start server subprocess
        cmd = [sys.executable, str(server_path), '--host', args.host, '--port', str(args.port)]
        
        server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        print(f"  [OK] Server process started (PID: {server_process.pid})")
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Open browser if enabled
        if auto_start_browser:
            open_browser(args.host, args.port)
        
        print()
        print("=" * 50)
        print("Server Running!")
        print("=" * 50)
        print(f"  Host: {args.host}")
        print(f"  Port: {args.port}")
        print(f"  Web interface: http://{args.host}:{args.port}")
        print()
        print("Press Ctrl+C to stop the server")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping server...")
            server_process.terminate()
            server_process.wait()
            
    except FileNotFoundError:
        print(f"[ERROR] Server file not found at {server_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()