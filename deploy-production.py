#!/usr/bin/env python3
"""
Production deployment preparation script for VivikA Finance.
This script prepares the application for deployment to Railway and Vercel.
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

class ProductionDeployer:
    """Handles preparation for production deployment."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.frontend_dir = self.root_dir / "frontend-modern"
        
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        print("Checking prerequisites...")
        
        checks = []
        
        # Check if main.py exists
        if (self.root_dir / "main.py").exists():
            checks.append("✅ Backend main.py found")
        else:
            checks.append("❌ Backend main.py not found")
            
        # Check if requirements.txt exists
        if (self.root_dir / "requirements.txt").exists():
            checks.append("✅ requirements.txt found")
        else:
            checks.append("❌ requirements.txt not found")
            
        # Check if frontend exists
        if self.frontend_dir.exists():
            checks.append("✅ Frontend directory found")
        else:
            checks.append("❌ Frontend directory not found")
            
        # Check if package.json exists
        if (self.frontend_dir / "package.json").exists():
            checks.append("✅ Frontend package.json found")
        else:
            checks.append("❌ Frontend package.json not found")
            
        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            checks.append("✅ Docker available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks.append("⚠️  Docker not available (optional)")
            
        for check in checks:
            print(f"  {check}")
            
        failed_checks = [check for check in checks if check.startswith("❌")]
        if failed_checks:
            print(f"\n❌ {len(failed_checks)} critical checks failed. Please fix before deploying.")
            return False
        else:
            print("\n✅ All prerequisites met!")
            return True
    
    def prepare_backend(self):
        """Prepare backend for production deployment."""
        print("\n🗄️  Preparing backend for production...")
        
        # Check if environment variables are configured
        env_vars = [
            "ENVIRONMENT=production",
            "DEBUG=false", 
            "DATABASE_URL=sqlite:///./production.db",
            'ALLOWED_ORIGINS=["https://vivikafinance.vercel.app"]',
            "API_HOST=0.0.0.0"
        ]
        
        print("  📋 Required environment variables for Railway/Render:")
        for var in env_vars:
            print(f"    {var}")
            
        # Test that the app can start
        print("\n  🧪 Testing backend startup...")
        try:
            result = subprocess.run([
                sys.executable, "-c", 
                "import main; print('✅ Backend imports successfully')"
            ], capture_output=True, text=True, cwd=self.root_dir)
            
            if result.returncode == 0:
                print("  ✅ Backend startup test passed")
            else:
                print(f"  ❌ Backend startup test failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ Backend test error: {e}")
            return False
            
        return True
    
    def prepare_frontend(self):
        """Prepare frontend for production deployment."""
        print("\n🎨 Preparing frontend for production...")
        
        # Check if node_modules exists
        if not (self.frontend_dir / "node_modules").exists():
            print("  📦 Installing frontend dependencies...")
            try:
                subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
                print("  ✅ Dependencies installed")
            except subprocess.CalledProcessError:
                print("  ❌ Failed to install dependencies")
                return False
        else:
            print("  ✅ Dependencies already installed")
            
        # Test build
        print("  🔨 Testing production build...")
        try:
            subprocess.run(["npm", "run", "build"], cwd=self.frontend_dir, check=True, capture_output=True)
            print("  ✅ Production build successful")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Production build failed")
            print(f"     Error: {e}")
            return False
            
        # Environment variables
        env_vars = [
            "NEXT_PUBLIC_API_URL=https://your-api-domain.railway.app",
            "NEXT_PUBLIC_APP_NAME=VivikA Finance - Life Planning Tool",
            "NEXT_PUBLIC_APP_VERSION=2.0.0"
        ]
        
        print("\n  📋 Required environment variables for Vercel:")
        for var in env_vars:
            print(f"    {var}")
            
        return True
    
    def generate_deployment_summary(self):
        """Generate deployment summary and next steps."""
        print("\n📋 DEPLOYMENT SUMMARY")
        print("=" * 50)
        
        print("\n🗄️  BACKEND DEPLOYMENT (Railway):")
        print("   1. Go to https://railway.app")
        print("   2. Create new project")
        print("   3. Connect your GitHub repository")
        print("   4. Set environment variables:")
        print("      ENVIRONMENT=production")
        print("      DEBUG=false")
        print("      DATABASE_URL=sqlite:///./production.db")
        print('      ALLOWED_ORIGINS=["https://vivikafinance.vercel.app"]')
        print("   5. Deploy!")
        
        print("\n🎨 FRONTEND DEPLOYMENT (Vercel):")
        print("   1. Go to https://vercel.com")
        print("   2. Import your GitHub repository")
        print("   3. Set Root Directory to 'frontend-modern'")
        print("   4. Set environment variables:")
        print("      NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app")
        print("      NEXT_PUBLIC_APP_NAME=VivikA Finance - Life Planning Tool")
        print("   5. Deploy!")
        
        print("\n🔧 POST-DEPLOYMENT:")
        print("   1. Update ALLOWED_ORIGINS in Railway with your Vercel URL")
        print("   2. Test the application end-to-end")
        print("   3. Configure custom domain (optional)")
        print("   4. Set up monitoring")
        
        print("\n📚 Full guide: DEPLOYMENT_GUIDE.md")
        print("\n🎉 Ready for production deployment!")
    
    def run(self):
        """Run the complete deployment preparation."""
        print("VivikA Finance - Production Deployment Preparation")
        print("=" * 60)
        
        if not self.check_prerequisites():
            return False
            
        if not self.prepare_backend():
            return False
            
        if not self.prepare_frontend():
            return False
            
        self.generate_deployment_summary()
        return True

def main():
    deployer = ProductionDeployer()
    success = deployer.run()
    
    if success:
            sys.exit(0)
    else:
        print("\n❌ Deployment preparation failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()