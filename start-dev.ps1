#!/usr/bin/env powershell
<#
.SYNOPSIS
    Development launcher for Financial Planning Application
.DESCRIPTION
    Quick development startup with minimal configuration checks
.EXAMPLE
    .\start-dev.ps1
#>

Write-Host "🛠️  Development Mode - Financial Planning App" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Services:" -ForegroundColor Yellow
Write-Host "   🔧 Backend:  http://localhost:8006" -ForegroundColor Cyan
Write-Host "   🎨 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 Starting backend server..." -ForegroundColor Yellow
$backendJob = Start-Process powershell -ArgumentList @(
    "-NoExit", 
    "-Command", 
    "cd '$PSScriptRoot'; Write-Host '🔧 FastAPI Development Server' -ForegroundColor Green; python main.py"
) -PassThru

Write-Host "   Backend PID: $($backendJob.Id)" -ForegroundColor DarkGray
Start-Sleep -Seconds 3

Write-Host "🚀 Starting frontend server..." -ForegroundColor Yellow
$frontendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PSScriptRoot\frontend-modern'; Write-Host '🎨 Next.js Development Server' -ForegroundColor Green; npm run dev"
) -PassThru

Write-Host "   Frontend PID: $($frontendJob.Id)" -ForegroundColor DarkGray

Write-Host ""
Write-Host "✅ Development servers started!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Open in browser:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")