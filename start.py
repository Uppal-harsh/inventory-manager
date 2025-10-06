#!/usr/bin/env python3
"""
Startup script for the Autonomous Inventory Orchestrator
"""
import subprocess
import sys
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import numpy
        import pandas
        print("[OK] Python dependencies found")
    except ImportError as e:
        print(f"[ERROR] Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if Node.js is available for React frontend
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Node.js found: {result.stdout.strip()}")
        else:
            print("[ERROR] Node.js not found. Please install Node.js to run the React frontend.")
            return False
    except FileNotFoundError:
        print("[ERROR] Node.js not found. Please install Node.js to run the React frontend.")
        return False
    
    return True

def install_frontend_dependencies():
    """Install React frontend dependencies"""
    print("Installing React frontend dependencies...")
    try:
        result = subprocess.run(["npm", "install"], cwd=Path.cwd(), capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Frontend dependencies installed successfully")
            return True
        else:
            print(f"[ERROR] Failed to install frontend dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Error installing frontend dependencies: {e}")
        return False

def build_frontend():
    """Build the React frontend"""
    print("Building React frontend...")
    try:
        result = subprocess.run(["npm", "run", "build"], cwd=Path.cwd(), capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Frontend built successfully")
            return True
        else:
            print(f"[ERROR] Failed to build frontend: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Error building frontend: {e}")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("Starting FastAPI backend...")
    try:
        # Change to backend directory and start the server
        backend_path = Path(__file__).parent / "backend"
        result = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=backend_path)
        
        print("[OK] Backend server started on http://localhost:8000")
        return result
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")
        return None

def start_frontend_dev():
    """Start the React frontend in development mode"""
    print("Starting React frontend in development mode...")
    try:
        result = subprocess.Popen(["npm", "start"], cwd=Path.cwd())
        print("[OK] Frontend development server starting on http://localhost:3000")
        return result
    except Exception as e:
        print(f"[ERROR] Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("[AI] Autonomous Inventory Orchestrator")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Install frontend dependencies if needed
    if not Path("node_modules").exists():
        if not install_frontend_dependencies():
            print("\n❌ Failed to install frontend dependencies.")
            sys.exit(1)
    
    # Build frontend
    if not build_frontend():
        print("\n❌ Failed to build frontend.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend.")
        sys.exit(1)
    
    # Wait a moment for backend to start
    print("\n⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start frontend in development mode
    frontend_process = start_frontend_dev()
    if not frontend_process:
        print("\n❌ Failed to start frontend.")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🚀 System started successfully!")
    print("\n📊 Dashboard: http://localhost:3000")
    print("🔧 API Docs: http://localhost:8000/docs")
    print("📡 WebSocket: ws://localhost:8000/ws")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print("\n❌ Backend process stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("\n❌ Frontend process stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✓ All services stopped")
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
