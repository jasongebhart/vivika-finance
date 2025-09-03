# 🚀 Deployment Guide

This guide explains how to deploy the Long-Term Financial Planning Application for production use.

## 📋 Quick Decision Guide

**Use Development Setup (Git Directory) if:**
- You're actively developing/modifying the code
- You want to test new features
- You're doing one-time analysis
- You don't mind potential interruptions from git operations

**Use Production Deployment if:**
- You want to use this regularly for financial planning
- You have important financial data to protect
- You want a stable, isolated environment
- You prefer optimized performance

## 🏗️ Production Deployment (Recommended)

### Option 1: Automated Deployment

Use the deployment script for a clean, automated setup:

```bash
# Deploy to a production directory
python deploy.py "C:\FinancePlanner" --include-data

# Or on Unix/Mac
python deploy.py ~/FinancePlanner --include-data
```

**What this does:**
- ✅ Creates isolated production environment
- ✅ Builds optimized React frontend
- ✅ Sets up clean Python virtual environment
- ✅ Copies your existing data (if `--include-data` used)
- ✅ Creates startup scripts
- ✅ Configures production settings

### Option 2: Manual Deployment

If you prefer manual control:

```bash
# 1. Create deployment directory
mkdir "C:\FinancePlanner"
cd "C:\FinancePlanner"

# 2. Copy application files
# Copy: main.py, models/, services/, requirements.txt, import_scenarios.py

# 3. Set up virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Unix/Mac

# 4. Install dependencies
pip install -r requirements.txt

# 5. Build frontend (in git directory)
cd path\to\git\vivikafinance\frontend
npm run build
# Copy build/ folder to deployment directory

# 6. Create data directory
mkdir data
```

## 🔧 Development Setup (Git Directory)

If you prefer to run from the git directory:

### Pros:
- ✅ Immediate access to latest code changes
- ✅ Can modify and test features quickly
- ✅ Single location for everything

### Cons:
- ❌ Private data mixed with source code
- ❌ Git operations may interfere
- ❌ Development dependencies included
- ❌ Less secure for sensitive financial data

### Setup:
```bash
# Already set up! Just run:
cd G:\jason\git\DataAndTools\vivikafinance
python main.py

# Frontend in separate terminal:
cd frontend
npm start
```

## 📁 Deployment Directory Structure

### Production Deployment Structure:
```
C:\FinancePlanner\
├── main.py                 # FastAPI application
├── requirements_prod.txt   # Production dependencies
├── import_scenarios.py     # Data import utility
├── models/                 # Data models
├── services/              # Business logic
├── frontend/              # React application (built)
│   └── build/            # Production build
├── data/                  # Your private data
│   ├── scenarios.db      # SQLite database
│   └── *.json           # Private scenario files
├── logs/                  # Application logs
├── backups/              # Data backups
├── config/               # Configuration files
├── venv/                 # Python virtual environment
├── start_production.bat  # Windows startup script
└── start_production.sh   # Unix/Mac startup script
```

### Development Structure (Current):
```
G:\jason\git\DataAndTools\vivikafinance\
├── main.py               # FastAPI application
├── requirements.txt      # All dependencies
├── frontend/            # React development setup
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   └── node_modules/   # Dependencies
├── scenarios.db         # Database (mixed with code)
├── tests/              # Test suites
└── .git/               # Git repository
```

## 🎯 Recommended Workflow

### For Regular Use:
1. **Deploy to production** using `python deploy.py`
2. **Import your data** in the production environment
3. **Use daily** from the clean production setup
4. **Backup regularly** from the production `data/` folder

### For Development:
1. **Keep git directory** for code changes
2. **Test changes** in development environment
3. **Redeploy** when satisfied with changes
4. **Never store private data** in git directory

## 🔐 Data Security Considerations

### Production Deployment:
- ✅ Private data completely separated from source code
- ✅ Database in dedicated `data/` directory
- ✅ Easy to backup just data folder
- ✅ Production configuration separate from code
- ✅ Virtual environment isolation

### Git Directory:
- ⚠️ Private data mixed with source code
- ⚠️ Risk of accidentally committing sensitive data
- ⚠️ Git operations affect running database
- ⚠️ Development tools have access to data

## 🚀 Starting the Application

### Production Deployment:
```bash
# Windows
cd "C:\FinancePlanner"
start_production.bat

# Unix/Mac
cd ~/FinancePlanner
./start_production.sh

# Manual
venv\Scripts\activate  # or source venv/bin/activate
python main.py
```

### Development Setup:
```bash
# Backend
cd G:\jason\git\DataAndTools\vivikafinance
python main.py

# Frontend (separate terminal)
cd frontend
npm start
```

## 📊 Importing Data

### In Production:
```bash
cd "C:\FinancePlanner"
venv\Scripts\activate
python import_scenarios.py my_private_scenarios.json
```

### In Development:
```bash
cd G:\jason\git\DataAndTools\vivikafinance
python import_scenarios.py my_private_scenarios.json
```

## 🔄 Updates and Maintenance

### Updating Production Deployment:
1. **Backup your data**: Copy `data/` folder
2. **Redeploy**: `python deploy.py "C:\FinancePlanner" --include-data`
3. **Test**: Verify everything works
4. **Restore data if needed**: From backup

### Development Updates:
- Simply `git pull` to get latest changes
- Restart the application

## 💾 Backup Strategy

### Production:
```bash
# Backup data directory
xcopy "C:\FinancePlanner\data" "C:\Backups\FinancePlanner\%date%" /E

# Export scenarios via API
curl http://localhost:8000/api/export/scenarios > backup.json
```

### Development:
```bash
# Copy database
copy scenarios.db backup_scenarios.db

# Export via API
curl http://localhost:8000/api/export/scenarios > backup.json
```

## 🆘 Troubleshooting

### Production Issues:
- Check `logs/` directory for error logs
- Verify virtual environment is activated
- Ensure `data/` directory permissions are correct
- Check port 8000 isn't already in use

### Development Issues:
- Check git status doesn't interfere
- Verify both backend and frontend are running
- Check for file permission issues
- Ensure all dependencies are installed

## 📝 Summary Recommendation

**For your use case (personal financial planning with private data):**

🎯 **Use Production Deployment**
- Run: `python deploy.py "C:\FinancePlanner" --include-data`
- Import your private scenarios there
- Use as your daily financial planning tool
- Keep git directory for any code modifications you want to make

This gives you the best of both worlds: a stable production environment for your financial data and a development environment for any customizations.