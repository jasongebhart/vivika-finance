#!/usr/bin/env python3
"""
Production deployment preparation script for VivikA Finance.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_backend():
    """Check backend readiness."""
    print("Checking backend...")
    
    # Check main files exist
    if not Path("main.py").exists():
        print("ERROR: main.py not found")
        return False
        
    if not Path("requirements.txt").exists():
        print("ERROR: requirements.txt not found") 
        return False
        
    # Test backend import
    try:
        result = subprocess.run([
            sys.executable, "-c", "import main; print('Backend OK')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Backend startup: OK")
            return True
        else:
            print(f"Backend startup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Backend check error: {e}")
        return False

def check_frontend():
    """Check frontend readiness."""
    print("Checking frontend...")
    
    frontend_dir = Path("frontend-modern")
    if not frontend_dir.exists():
        print("ERROR: frontend-modern directory not found")
        return False
        
    if not (frontend_dir / "package.json").exists():
        print("ERROR: package.json not found")
        return False
        
    print("Frontend structure: OK")
    return True

def main():
    print("VivikA Finance - Deployment Readiness Check")
    print("=" * 50)
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    
    if backend_ok and frontend_ok:
        print("\nSUCCESS: Ready for production deployment!")
        print("\nNext steps:")
        print("1. Deploy backend to Railway:")
        print("   - Go to railway.app")
        print("   - Connect GitHub repo")
        print("   - Set environment variables")
        print("2. Deploy frontend to Vercel:")
        print("   - Go to vercel.com") 
        print("   - Import GitHub repo")
        print("   - Set root directory to 'frontend-modern'")
        print("3. See DEPLOYMENT_GUIDE.md for full instructions")
        return True
    else:
        print("\nFAILED: Fix the errors above before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)