#Requires -Version 5.1
<#
.SYNOPSIS
    Launch script for Long-Term Financial Planning Application
.DESCRIPTION
    Starts both the FastAPI backend and Next.js frontend servers with proper error handling
#>

[CmdletBinding()]
param()

# Set console properties
$Host.UI.RawUI.WindowTitle = "Long-Term Financial Planning Application Launcher"
Clear-Host

# Global variables for process tracking
$script:BackendProcess = $null
$script:FrontendProcess = $null

function Write-StepHeader {
    param([string]$Step, [string]$Description)
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  Long-Term Financial Planning Application (Modern Frontend)" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[$Step] $Description..." -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "       OK $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "       WARNING $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "       ERROR $Message" -ForegroundColor Red
}

function Test-Prerequisites {
    Write-StepHeader "1/6" "Checking prerequisites"
    
    # Check if we're in the correct directory
    if (-not (Test-Path "main.py")) {
        Write-Error "main.py not found. Please run this from the project root directory."
        exit 1
    }
    
    if (-not (Test-Path "frontend-modern")) {
        Write-Error "frontend-modern directory not found."
        exit 1
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        Write-Error "Python not found in PATH"
        exit 1
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js found: $nodeVersion"
    }
    catch {
        Write-Error "Node.js not found in PATH"
        exit 1
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>&1
        Write-Success "npm found: v$npmVersion"
    }
    catch {
        Write-Error "npm not found in PATH"
        exit 1
    }
}

function Install-PythonDependencies {
    Write-StepHeader "2/6" "Installing Python dependencies"
    
    try {
        $packages = @(
            "fastapi", "uvicorn", "pydantic", "aiosqlite", 
            "httpx", "python-multipart", "websockets", 
            "flask", "flask-cors"
        )
        
        pip install --quiet @packages
        Write-Success "Python dependencies installed successfully"
    }
    catch {
        Write-Warning "Some Python packages may have failed to install. Continuing anyway..."
    }
}

function Import-ScenarioData {
    Write-StepHeader "3/6" "Importing scenario data"
    
    if (Test-Path "jason_scenarios_final_corrected.json") {
        Write-Host "       Found scenario file, importing..." -ForegroundColor White
        try {
            python import_scenarios.py jason_scenarios_final_corrected.json 2>$null
            Write-Success "Scenarios imported successfully!"
        }
        catch {
            Write-Warning "Failed to import scenarios"
        }
    }
    else {
        Write-Warning "No scenario file found, starting with empty database"
    }
}

function Start-BackendServer {
    Write-StepHeader "4/6" "Starting FastAPI backend server"
    Write-Host "       Backend will be available at: http://localhost:8006" -ForegroundColor White
    
    try {
        # Start backend in a new PowerShell process
        $script:BackendProcess = Start-Process powershell -ArgumentList @(
            "-NoExit", 
            "-Command", 
            "cd '$PSScriptRoot'; Write-Host '🔧 FastAPI Production Server' -ForegroundColor Green; python main.py"
        ) -PassThru
        
        Write-Success "Backend server started (PID: $($script:BackendProcess.Id))"
        
        # Wait for backend to initialize
        Write-Host "       Waiting for backend to initialize..." -ForegroundColor White
        Start-Sleep -Seconds 8
        
        # Check if backend is responding
        Write-Host "       Checking backend health..." -ForegroundColor White
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8006/api/health" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "Backend is responding"
            }
            else {
                Write-Warning "Backend returned status code: $($response.StatusCode)"
            }
        }
        catch {
            Write-Warning "Backend may not be fully ready yet. Continuing anyway..."
        }
    }
    catch {
        Write-Error "Failed to start backend server: $($_.Exception.Message)"
        exit 1
    }
}

function Install-NodeDependencies {
    Write-StepHeader "5/6" "Installing Node.js dependencies"
    
    Push-Location "frontend-modern"
    try {
        if (-not (Test-Path "node_modules")) {
            Write-Host "       Installing packages (this may take a moment)..." -ForegroundColor White
            try {
                npm install --silent
                Write-Success "Node modules installed successfully"
            }
            catch {
                Write-Warning "npm install had issues, trying legacy mode..."
                npm install --legacy-peer-deps --silent
            }
        }
        else {
            Write-Success "Node modules already installed"
        }
    }
    finally {
        Pop-Location
    }
}

function Start-FrontendServer {
    Write-StepHeader "6/6" "Starting Next.js frontend server"
    Write-Host "       Frontend will be available at: http://localhost:3000" -ForegroundColor White
    
    try {
        # Start frontend in a new PowerShell process
        $script:FrontendProcess = Start-Process powershell -ArgumentList @(
            "-NoExit",
            "-Command",
            "cd '$PSScriptRoot\frontend-modern'; Write-Host '🎨 Next.js Production Server' -ForegroundColor Green; npm run dev"
        ) -PassThru
        
        Write-Success "Frontend server started (PID: $($script:FrontendProcess.Id))"
        
        # Wait for frontend to start
        Write-Host "       Waiting for frontend to initialize..." -ForegroundColor White
        Start-Sleep -Seconds 5
    }
    catch {
        Write-Error "Failed to start frontend server: $($_.Exception.Message)"
        exit 1
    }
}

function Show-ApplicationInfo {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  APPLICATION STARTED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Backend API:    http://localhost:8006" -ForegroundColor White
    Write-Host "  Frontend App:   http://localhost:3000" -ForegroundColor White
    Write-Host ""
    Write-Host "  API Endpoints:" -ForegroundColor Yellow
    Write-Host "  - Health Check: http://localhost:8006/api/health" -ForegroundColor White
    Write-Host "  - Scenarios:    http://localhost:8006/api/scenarios" -ForegroundColor White
    Write-Host "  - API Docs:     http://localhost:8006/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Open browser
    Write-Host "Opening browser..." -ForegroundColor Yellow
    Start-Process "http://localhost:3000"
}

function Stop-Servers {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    
    if ($script:FrontendProcess -and -not $script:FrontendProcess.HasExited) {
        try {
            $script:FrontendProcess.Kill()
            Write-Success "Frontend server stopped"
        }
        catch {
            Write-Warning "Could not stop frontend server gracefully"
        }
    }
    
    if ($script:BackendProcess -and -not $script:BackendProcess.HasExited) {
        try {
            $script:BackendProcess.Kill()
            Write-Success "Backend server stopped"
        }
        catch {
            Write-Warning "Could not stop backend server gracefully"
        }
    }
    
    Write-Success "Cleanup completed"
}

function Main {
    try {
        Test-Prerequisites
        Install-PythonDependencies
        Import-ScenarioData
        Start-BackendServer
        Install-NodeDependencies
        Start-FrontendServer
        Show-ApplicationInfo
        
        Write-Host "Press any key to exit and stop all servers..." -ForegroundColor Magenta
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        Stop-Servers
    }
    catch {
        Write-Error "An unexpected error occurred: $($_.Exception.Message)"
        Stop-Servers
        exit 1
    }
}

# Run main function
Main