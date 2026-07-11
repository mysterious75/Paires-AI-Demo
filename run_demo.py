#!/usr/bin/env python3
"""
Quick start script for Paires AI Demo
Run this to start both backend and frontend
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("  Paires AI Messaging Agent Demo")
    print("  Applied AI Engineer Role Submission")
    print("=" * 60)
    print()
    
    # Get project root
    root = Path(__file__).parent
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ required")
        sys.exit(1)
    
    print("Starting backend server...")
    print("API will be available at: http://localhost:8000")
    print()
    
    # Start backend
    backend_dir = root / "backend"
    os.chdir(backend_dir)
    
    # Install dependencies if needed
    print("Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    
    # Set demo mode
    os.environ["DEMO_MODE"] = "true"
    
    # Start uvicorn
    print("\nStarting API server...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--reload", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
