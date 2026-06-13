#!/usr/bin/env python3
"""
JSAIBOT Start Script

Launches the JSAIBOT WebLLM server for local AI chat.
Automatically installs dependencies, downloads missing models,
and starts the server with minimal user intervention.

Usage:
    python start_server.py [--host HOST] [--port PORT]
"""

import subprocess
import sys
from pathlib import Path


def check_and_install_dependencies():
    """Check and install required Python dependencies."""
    print("[1/4] Checking dependencies...")
    
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


def initialize_model():
    """Initialize the default model, downloading if necessary."""
    print()
    print("[2/4] Initializing AI model...")
    
    try:
        from src.model_manager import ModelManager
        from src.config import WebLLMConfig
        
        manager = ModelManager(auto_download=True)
        
        # Check if model is installed
        default_model = WebLLMConfig.DEFAULT_MODEL
        if not manager.is_model_installed(default_model):
            print(f"  [INFO] Default model '{default_model}' not found")
            print("  [INFO] Downloading model...")
            
            result = manager.download_model(default_model)
            
            if result.get('downloaded'):
                print(f"  [OK] Model downloaded to {result['path']}")
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"  [WARN] Could not download model: {error_msg}")
                print("  [INFO] Server will start but AI features may be limited")
        else:
            print(f"  [OK] Model '{default_model}' is ready")
        
        return True
        
    except ImportError as e:
        print(f"  [WARN] Could not check models: {e}")
        print("  [INFO] Server will start but AI features may be limited")
        return True
    except Exception as e:
        print(f"  [WARN] Model initialization issue: {e}")
        print("  [INFO] Server will start but AI features may be limited")
        return True


def check_server_files():
    """Verify server files are in place."""
    print()
    print("[3/4] Verifying server files...")
    
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


def start_server(host='localhost', port=8080):
    """Start the aiohttp server."""
    print()
    print("[4/4] Starting JSAIBOT server...")
    
    try:
        import subprocess
        
        script_dir = Path(__file__).parent
        server_path = script_dir / "src" / "server.py"
        
        if not server_path.exists():
            print(f"[ERROR] Server file not found at {server_path}")
            return False
        
        # Start the server with host and port arguments
        cmd = [sys.executable, str(server_path), '--host', host, '--port', str(port)]
        
        process = subprocess.run(cmd)
        return True
        
    except KeyboardInterrupt:
        print("\nServer stopped.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False


def main():
    """Main entry point to start the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='JSAIBOT - Local WebLLM Chat System')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("JSAIBOT - Local WebLLM Chat System")
    print("=" * 50)
    print()
    
    # Step 1: Check and install dependencies
    if not check_and_install_dependencies():
        print("\n[ERROR] Server could not start due to missing dependencies.")
        sys.exit(1)
    
    # Step 2: Initialize model (auto-download if needed)
    initialize_model()
    
    # Step 3: Verify server files
    check_server_files()
    
    # Step 4: Start the server
    print()
    print("=" * 50)
    print("Server Configuration")
    print("=" * 50)
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  Web interface: http://{args.host}:{args.port}")
    print()
    
    start_server(args.host, args.port)


if __name__ == "__main__":
    main()