#!/usr/bin/env powershell
<#
.SYNOPSIS
    Start the Full Stack Financial Planning Application
.DESCRIPTION
    Launches both the FastAPI backend (port 8006) and Next.js frontend (port 3000)
.EXAMPLE
    .\start-full-stack.ps1
#>

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Help
)

if ($Help) {
    Write-Host "Financial Planning App Launcher" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start-full-stack.ps1           # Start both backend and frontend"
    Write-Host "  .\start-full-stack.ps1 -Backend  # Start only backend"
    Write-Host "  .\start-full-stack.ps1 -Frontend # Start only frontend"
    Write-Host "  .\start-full-stack.ps1 -Help     # Show this help"
    Write-Host ""
    Write-Host "URLs:" -ForegroundColor Cyan
    Write-Host "  Backend:  http://localhost:8006"
    Write-Host "  Frontend: http://localhost:3000"
    exit
}

Write-Host "Financial Planning Application Launcher" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is available for frontend
if (-not $Backend) {
    try {
        $nodeVersion = node --version 2>&1
        Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "Node.js not found! Please install Node.js 16+" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Start Backend
if (-not $Frontend) {
    Write-Host "Starting FastAPI Backend (Port 8006)..." -ForegroundColor Yellow
    $backendJob = Start-Process powershell -ArgumentList @(
        "-NoExit", 
        "-WindowStyle", "Normal",
        "-Command", 
        "cd '$PSScriptRoot'; Write-Host 'FastAPI Backend Starting...' -ForegroundColor Yellow; python main.py"
    ) -PassThru
    
    Write-Host "   Backend PID: $($backendJob.Id)" -ForegroundColor DarkGray
    Start-Sleep -Seconds 3
}

# Start Frontend  
if (-not $Backend) {
    Write-Host "Starting Next.js Frontend (Port 3000)..." -ForegroundColor Yellow
    $frontendJob = Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-WindowStyle", "Normal", 
        "-Command",
        "cd '$PSScriptRoot\frontend-modern'; Write-Host 'Next.js Frontend Starting...' -ForegroundColor Yellow; npm run dev"
    ) -PassThru
    
    Write-Host "   Frontend PID: $($frontendJob.Id)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Services Started Successfully!" -ForegroundColor Green
Write-Host ""

if (-not $Frontend) {
    Write-Host "Backend API:  http://localhost:8006" -ForegroundColor Cyan
    Write-Host "Health Check: http://localhost:8006/api/health" -ForegroundColor DarkCyan
}

if (-not $Backend) {
    Write-Host "Frontend App: http://localhost:3000" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "   - Both services will open in separate PowerShell windows"
Write-Host "   - Close those windows to stop the services"
Write-Host "   - Check the service windows for logs and errors"
Write-Host ""
Write-Host "Press any key to exit this launcher..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")