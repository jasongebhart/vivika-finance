#!/usr/bin/env python3
"""
Production deployment script for Long-Term Financial Planning Application.
This script creates a clean production deployment separate from the git directory.
"""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
import argparse

class FinancePlannerDeployer:
    """Handles deployment of the financial planning application."""
    
    def __init__(self, source_dir=None, target_dir=None):
        self.source_dir = Path(source_dir or os.getcwd())
        self.target_dir = Path(target_dir) if target_dir else None
        
    def deploy(self, target_directory, include_data=False):
        """Deploy the application to a target directory."""
        self.target_dir = Path(target_directory).resolve()
        
        print(f"🚀 Deploying Financial Planning Application")
        print(f"📂 Source: {self.source_dir}")
        print(f"📁 Target: {self.target_dir}")
        print()
        
        # Create target directory
        if self.target_dir.exists():
            print(f"⚠️  Target directory exists: {self.target_dir}")
            response = input("Continue and overwrite? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Deployment cancelled")
                return False
            
            # Backup existing data if it exists
            if include_data and (self.target_dir / "scenarios.db").exists():
                backup_file = self.target_dir / f"scenarios_backup_{self._get_timestamp()}.db"
                shutil.copy2(self.target_dir / "scenarios.db", backup_file)
                print(f"💾 Backed up existing data to: {backup_file}")
        
        try:
            # Create deployment structure
            self._create_deployment_structure()
            
            # Copy application files
            self._copy_application_files()
            
            # Build frontend for production
            self._build_frontend()
            
            # Create production configuration
            self._create_production_config()
            
            # Copy data if requested
            if include_data:
                self._copy_data_files()
            
            # Create startup scripts
            self._create_startup_scripts()
            
            # Set up virtual environment
            self._setup_virtual_environment()
            
            print()
            print("✅ Deployment completed successfully!")
            print()
            self._print_usage_instructions()
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            return False
    
    def _create_deployment_structure(self):
        """Create the deployment directory structure."""
        print("📁 Creating deployment structure...")
        
        self.target_dir.mkdir(parents=True, exist_ok=True)
        (self.target_dir / "data").mkdir(exist_ok=True)
        (self.target_dir / "logs").mkdir(exist_ok=True)
        (self.target_dir / "backups").mkdir(exist_ok=True)
        (self.target_dir / "config").mkdir(exist_ok=True)
    
    def _copy_application_files(self):
        """Copy necessary application files."""
        print("📋 Copying application files...")
        
        # Python backend files
        backend_files = [
            "main.py",
            "requirements.txt",
            "models/",
            "services/",
            "tests/",
            "import_scenarios.py"
        ]
        
        for item in backend_files:
            source = self.source_dir / item
            target = self.target_dir / item
            
            if source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                print(f"  ✓ {item}")
            elif source.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(source, target)
                print(f"  ✓ {item}/")
        
        # Copy documentation
        docs = ["README.md", "API_DOCUMENTATION.md", "IMPORT_GUIDE.md"]
        for doc in docs:
            source = self.source_dir / doc
            if source.exists():
                shutil.copy2(source, self.target_dir / doc)
                print(f"  ✓ {doc}")
    
    def _build_frontend(self):
        """Build the React frontend for production."""
        print("⚛️  Building React frontend...")
        
        frontend_source = self.source_dir / "frontend"
        frontend_target = self.target_dir / "frontend"
        
        if not frontend_source.exists():
            print("  ⚠️  Frontend source not found, skipping...")
            return
        
        # Copy frontend source
        if frontend_target.exists():
            shutil.rmtree(frontend_target)
        shutil.copytree(frontend_source, frontend_target)
        
        # Install dependencies and build
        try:
            subprocess.run(["npm", "install"], cwd=frontend_target, check=True, capture_output=True)
            subprocess.run(["npm", "run", "build"], cwd=frontend_target, check=True, capture_output=True)
            print("  ✓ Frontend built successfully")
            
            # Clean up development files
            dev_dirs = ["node_modules", "src", "public"]
            for dev_dir in dev_dirs:
                dev_path = frontend_target / dev_dir
                if dev_path.exists():
                    if dev_dir == "node_modules":
                        shutil.rmtree(dev_path)  # Remove node_modules
                    # Keep src and public for debugging if needed
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Frontend build failed: {e}")
            print("  📝 You may need to build manually later")
    
    def _create_production_config(self):
        """Create production configuration files."""
        print("⚙️  Creating production configuration...")
        
        # Production environment file
        env_content = """# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Database
DATABASE_PATH=data/scenarios.db

# Server
HOST=127.0.0.1
PORT=8000
WORKERS=1

# CORS (adjust as needed)
CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key-change-this
"""
        
        with open(self.target_dir / "config" / "production.env", "w") as f:
            f.write(env_content)
        
        # Production requirements (lighter than development)
        prod_requirements = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0", 
            "pydantic==2.5.0",
            "aiosqlite==0.19.0",
            "httpx==0.25.2",
            "python-multipart==0.0.6",
            "websockets==12.0"
        ]
        
        with open(self.target_dir / "requirements_prod.txt", "w") as f:
            f.write("\n".join(prod_requirements))
        
        print("  ✓ Configuration files created")
    
    def _copy_data_files(self):
        """Copy existing data files if they exist."""
        print("💾 Copying data files...")
        
        data_files = ["scenarios.db"]
        for data_file in data_files:
            source = self.source_dir / data_file
            if source.exists():
                shutil.copy2(source, self.target_dir / "data" / data_file)
                print(f"  ✓ {data_file}")
            else:
                print(f"  ℹ️  {data_file} not found (will be created on first run)")
    
    def _create_startup_scripts(self):
        """Create startup scripts for the deployment."""
        print("🔧 Creating startup scripts...")
        
        # Windows batch script
        batch_script = """@echo off
echo Starting Financial Planning Application (Production)
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\\Scripts\\activate.bat

echo Starting backend server...
set DATABASE_PATH=data/scenarios.db
python main.py

pause
"""
        
        with open(self.target_dir / "start_production.bat", "w") as f:
            f.write(batch_script)
        
        # Linux/Mac shell script
        shell_script = """#!/bin/bash
echo "Starting Financial Planning Application (Production)"
echo

cd "$(dirname "$0")"

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting backend server..."
export DATABASE_PATH=data/scenarios.db
python main.py
"""
        
        with open(self.target_dir / "start_production.sh", "w") as f:
            f.write(shell_script)
        
        # Make shell script executable on Unix systems
        try:
            os.chmod(self.target_dir / "start_production.sh", 0o755)
        except:
            pass  # Windows doesn't support chmod
        
        print("  ✓ Startup scripts created")
    
    def _setup_virtual_environment(self):
        """Set up a clean virtual environment for production."""
        print("🐍 Setting up virtual environment...")
        
        venv_path = self.target_dir / "venv"
        
        try:
            # Create virtual environment
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            
            # Determine pip path
            if os.name == 'nt':  # Windows
                pip_path = venv_path / "Scripts" / "pip.exe"
            else:  # Unix
                pip_path = venv_path / "bin" / "pip"
            
            # Install production requirements
            subprocess.run([
                str(pip_path), "install", "-r", "requirements_prod.txt"
            ], cwd=self.target_dir, check=True)
            
            print("  ✓ Virtual environment created and configured")
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Virtual environment setup failed: {e}")
            print("  📝 You may need to set up manually")
    
    def _get_timestamp(self):
        """Get current timestamp for backup files."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _print_usage_instructions(self):
        """Print instructions for using the deployed application."""
        print("📋 Usage Instructions:")
        print()
        print("1. Navigate to deployment directory:")
        print(f"   cd \"{self.target_dir}\"")
        print()
        print("2. Start the application:")
        print("   Windows: start_production.bat")
        print("   Linux/Mac: ./start_production.sh")
        print()
        print("3. Access the application:")
        print("   Backend API: http://localhost:8000")
        print("   Frontend: Served by backend (production build)")
        print()
        print("4. Import your private data:")
        print("   python import_scenarios.py your_scenarios.json")
        print()
        print("📁 Directory Structure:")
        print("   data/          - Database and private data")
        print("   logs/          - Application logs")
        print("   backups/       - Data backups")
        print("   config/        - Configuration files")
        print("   venv/          - Python virtual environment")
        print()
        print(f"🔒 Your private data will be stored in: {self.target_dir}/data/")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy Financial Planning Application for production use"
    )
    parser.add_argument("target_dir", help="Target deployment directory")
    parser.add_argument("--include-data", action="store_true",
                       help="Copy existing database and data files")
    parser.add_argument("--source", help="Source directory (default: current directory)")
    
    args = parser.parse_args()
    
    deployer = FinancePlannerDeployer(source_dir=args.source)
    success = deployer.deploy(args.target_dir, include_data=args.include_data)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())