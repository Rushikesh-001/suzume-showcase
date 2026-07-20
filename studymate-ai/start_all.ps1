# StudyMate AI — One-Click Startup
# Run this script to start everything:
#   1. Backend server (API + Admin Dashboard)
#   2. Open browser to admin dashboard
#   3. Show connection info

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🚀 StudyMate AI - STARTING ALL         ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Server  →  Python Backend (port 8765)      ║" -ForegroundColor Cyan
Write-Host "║  Admin   →  http://localhost:8765/admin     ║" -ForegroundColor Cyan
Write-Host "║  App     →  Connect to YOUR_IP:8765         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Kill any existing python server
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Get local IP
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "Loopback|VMware|Virtual|Bluetooth" -and $_.PrefixOrigin -eq "Dhcp" } | Select-Object -First 1).IPAddress
if (-not $ip) { $ip = "127.0.0.1" }

Write-Host "📡 Your IP for phone connection: " -NoNewline -ForegroundColor Yellow
Write-Host "$ip`:8765" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""

# Start the backend server
$env:PYTHONIOENCODING = 'utf-8'
$serverDir = Join-Path $PSScriptRoot "backend"
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-X utf8 `"$serverDir\server.py`""

Start-Sleep -Seconds 3

# Open browser to admin dashboard
Write-Host "🌐 Opening admin dashboard..." -ForegroundColor Green
Start-Process "http://localhost:8765/admin"

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host "──────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "📊 Admin:       http://localhost:8765/admin" -ForegroundColor White
Write-Host "🔑 Login:       admin / admin123" -ForegroundColor White
Write-Host "📱 Phone:       http://$ip`:8765" -ForegroundColor White
Write-Host "📁 DB:          $serverDir\studymate.db" -ForegroundColor White
Write-Host "──────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Press any key to stop all services..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup on exit
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "Services stopped." -ForegroundColor Yellow
