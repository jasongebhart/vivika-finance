#!/usr/bin/env powershell
<#
.SYNOPSIS
    Interactive launcher menu for Financial Planning Application
.DESCRIPTION
    Provides a simple menu to choose different startup options
.EXAMPLE
    .\launch.ps1
#>

function Show-Menu {
    Clear-Host
    Write-Host "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓" -ForegroundColor Cyan
    Write-Host "┃                 Financial Planning Application                ┃" -ForegroundColor Cyan  
    Write-Host "┃                     PowerShell Launcher                       ┃" -ForegroundColor Cyan
    Write-Host "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Select a launch option:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] 🚀 Quick Dev Start        - Fast development startup" -ForegroundColor Green
    Write-Host "  [2] 🔧 Full Stack Start       - Full stack with checks" -ForegroundColor Green  
    Write-Host "  [3] 🏭 Complete Setup         - Production-ready setup" -ForegroundColor Green
    Write-Host "  [4] 🔙 Backend Only           - Start only backend" -ForegroundColor Blue
    Write-Host "  [5] 🎨 Frontend Only          - Start only frontend" -ForegroundColor Blue
    Write-Host "  [6] ❓ Help                   - Show all options" -ForegroundColor Magenta
    Write-Host "  [0] 🚪 Exit                   - Quit launcher" -ForegroundColor Red
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
}

function Start-Option {
    param([string]$Option)
    
    switch ($Option) {
        "1" {
            Write-Host "Starting Quick Development Mode..." -ForegroundColor Green
            & ".\start-dev.ps1"
        }
        "2" {
            Write-Host "Starting Full Stack Mode..." -ForegroundColor Green
            & ".\start-full-stack.ps1"
        }
        "3" {
            Write-Host "Starting Complete Setup..." -ForegroundColor Green
            & ".\launch-complete.ps1"
        }
        "4" {
            Write-Host "Starting Backend Only..." -ForegroundColor Blue
            & ".\start-full-stack.ps1" -Backend
        }
        "5" {
            Write-Host "Starting Frontend Only..." -ForegroundColor Blue
            & ".\start-full-stack.ps1" -Frontend
        }
        "6" {
            & ".\start-full-stack.ps1" -Help
            Write-Host ""
            Write-Host "Press any key to return to menu..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "0" {
            Write-Host "Goodbye! 👋" -ForegroundColor Yellow
            exit 0
        }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}

# Main loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Enter your choice (0-6)"
    
    if ($choice -eq "0") {
        Write-Host ""
        Write-Host "Thanks for using Financial Planning Application! 🎯" -ForegroundColor Green
        break
    }
    
    if ($choice -match "^[1-6]$") {
        Start-Option $choice
        
        if ($choice -ne "6") {  # Don't pause after help
            Write-Host ""
            Write-Host "Press any key to return to menu..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        
        continue
    }
    
    # Invalid input
    Write-Host ""
    Write-Host "❌ Invalid choice '$choice'. Please select 0-6." -ForegroundColor Red
    Start-Sleep -Seconds 2
}