#!/usr/bin/env python3
"""
Deployment helper script for VivikA Finance.
Provides deployment commands and verification.
"""

import os
import webbrowser
import json
from pathlib import Path

def open_deployment_platforms():
    """Open deployment platforms in browser."""
    print("🚀 Opening deployment platforms...")
    
    # Open Railway
    print("📤 Opening Railway for backend deployment...")
    webbrowser.open("https://railway.app")
    
    # Open Vercel  
    print("🎨 Opening Vercel for frontend deployment...")
    webbrowser.open("https://vercel.com")
    
    print("\n✅ Deployment platforms opened in your browser!")

def show_backend_config():
    """Show backend environment variables for Railway."""
    print("\n🗄️  BACKEND ENVIRONMENT VARIABLES (Railway/Render):")
    print("=" * 60)
    
    env_vars = {
        "ENVIRONMENT": "production",
        "DEBUG": "false", 
        "DATABASE_URL": "sqlite:///./production.db",
        "ALLOWED_ORIGINS": '["https://vivikafinance.vercel.app"]',
        "API_HOST": "0.0.0.0",
        "PORT": "8000"
    }
    
    for key, value in env_vars.items():
        print(f"  {key}={value}")
    
    print("\n📋 Copy these to your Railway dashboard > Variables tab")

def show_frontend_config():
    """Show frontend environment variables for Vercel."""
    print("\n🎨 FRONTEND ENVIRONMENT VARIABLES (Vercel):")
    print("=" * 60)
    
    env_vars = {
        "NEXT_PUBLIC_API_URL": "https://your-railway-app.railway.app",
        "NEXT_PUBLIC_APP_NAME": "VivikA Finance - Life Planning Tool",
        "NEXT_PUBLIC_APP_VERSION": "2.0.0",
        "NEXT_PUBLIC_ENABLE_WEBSOCKETS": "true",
        "NEXT_PUBLIC_ENABLE_MONTE_CARLO": "true", 
        "NEXT_PUBLIC_ENABLE_LIFE_PLANNING": "true"
    }
    
    for key, value in env_vars.items():
        print(f"  {key}={value}")
    
    print("\n📋 Copy these to your Vercel dashboard > Settings > Environment Variables")
    print("⚠️  IMPORTANT: Replace 'your-railway-app' with your actual Railway URL")

def show_deployment_checklist():
    """Show deployment checklist."""
    print("\n🎯 DEPLOYMENT CHECKLIST:")
    print("=" * 40)
    
    checklist = [
        "Backend deployed to Railway/Render",
        "Frontend deployed to Vercel",
        "Environment variables configured", 
        "CORS settings updated",
        "Health checks passing",
        "All features tested in production"
    ]
    
    for i, item in enumerate(checklist, 1):
        print(f"  {i}. [ ] {item}")
    
    print(f"\n📚 See DEPLOY_NOW.md for step-by-step instructions")
    print(f"📖 See DEPLOYMENT_GUIDE.md for detailed documentation")

def verify_readiness():
    """Verify deployment readiness."""
    print("🔍 Verifying deployment readiness...")
    
    checks = []
    
    # Check main files
    if Path("main.py").exists():
        checks.append("✅ Backend main.py found")
    else:
        checks.append("❌ Backend main.py missing")
        
    if Path("requirements.txt").exists():
        checks.append("✅ requirements.txt found")
    else:
        checks.append("❌ requirements.txt missing")
        
    if Path("frontend-modern").exists():
        checks.append("✅ Frontend directory found")
    else:
        checks.append("❌ Frontend directory missing")
        
    if Path("frontend-modern/package.json").exists():
        checks.append("✅ Frontend package.json found")
    else:
        checks.append("❌ Frontend package.json missing")
        
    if Path("Dockerfile").exists():
        checks.append("✅ Docker configuration found")
    else:
        checks.append("⚠️  Docker configuration missing (optional)")
    
    for check in checks:
        print(f"  {check}")
    
    failed = [c for c in checks if c.startswith("❌")]
    if failed:
        print(f"\n❌ {len(failed)} critical issues found. Fix before deploying.")
        return False
    else:
        print("\n✅ All checks passed! Ready for deployment.")
        return True

def main():
    """Main deployment helper menu."""
    print("VivikA Finance - Deployment Helper")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("  1. Open deployment platforms (Railway + Vercel)")
        print("  2. Show backend environment variables")
        print("  3. Show frontend environment variables") 
        print("  4. Show deployment checklist")
        print("  5. Verify deployment readiness")
        print("  6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            open_deployment_platforms()
        elif choice == "2":
            show_backend_config()
        elif choice == "3":
            show_frontend_config()
        elif choice == "4":
            show_deployment_checklist()
        elif choice == "5":
            verify_readiness()
        elif choice == "6":
            print("\n🎉 Happy deploying!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()