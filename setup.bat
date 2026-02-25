@echo off
REM Terrapin Attack Lab - Windows Setup Script

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           TERRAPIN ATTACK - DEMO LAB SETUP                ║
echo ║                   CVE-2023-48795                          ║
echo ║                                                            ║
echo ║              ⚠️  EDUCATIONAL USE ONLY ⚠️                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Docker is not installed
    echo Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)
echo [✓] Docker found

REM Check Docker Compose
docker-compose version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    docker compose version >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Docker Compose is not available
        pause
        exit /b 1
    )
)
echo [✓] Docker Compose found

REM Check Docker daemon
docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Docker daemon is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)
echo [✓] Docker daemon running
echo.

if "%1"=="" goto menu
goto command

:menu
echo What would you like to do?
echo 1) Full setup (build + start + verify)
echo 2) Build only
echo 3) Start lab
echo 4) Check status
echo 5) Verify vulnerability
echo 6) Stop lab
echo 7) Stop and remove lab
echo 8) Exit
echo.
set /p choice="Enter choice [1-8]: "

if "%choice%"=="1" goto fullsetup
if "%choice%"=="2" goto build
if "%choice%"=="3" goto start
if "%choice%"=="4" goto status
if "%choice%"=="5" goto verify
if "%choice%"=="6" goto stop
if "%choice%"=="7" goto down
if "%choice%"=="8" goto end

echo Invalid choice
goto menu

:command
if "%1"=="build" goto build
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="down" goto down
if "%1"=="status" goto status
if "%1"=="verify" goto verify
if "%1"=="setup" goto fullsetup
echo Usage: setup.bat [build^|start^|stop^|down^|status^|verify^|setup]
exit /b 1

:fullsetup
echo [*] Building Docker containers...
docker-compose build
if %ERRORLEVEL% NEQ 0 (
    echo [!] Build failed
    pause
    exit /b 1
)
echo [✓] Build completed

:start
echo [*] Starting containers...
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to start containers
    pause
    exit /b 1
)
echo [✓] Containers started
timeout /t 5 /nobreak >nul

:status
echo [*] Container status:
docker-compose ps
echo.

if "%1"=="setup" goto verify
if "%choice%"=="1" goto verify
if "%1"=="status" goto end
if "%choice%"=="4" pause
goto menu

:verify
echo [*] Verifying vulnerability...
docker exec -it terrapin-attacker python3 /attack/demo/verify_vulnerability.py --host vulnerable-server --port 22
echo.

if "%1"=="setup" goto nextsteps
if "%choice%"=="1" goto nextsteps
if "%1"=="verify" goto end
if "%choice%"=="5" pause
goto menu

:nextsteps
echo ╔════════════════════════════════════════════════════════════╗
echo ║              Lab Setup Complete!                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Next Steps:
echo.
echo 1️⃣  Read the Quick Start Guide:
echo    type QUICKSTART.md
echo.
echo 2️⃣  Or jump right into the attack:
echo.
echo    Terminal 1 (start attack proxy):
echo    docker exec -it terrapin-attacker python3 /attack/poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22 --proxy-port 2222
echo.
echo    Terminal 2 (connect through proxy):
echo    docker exec -it terrapin-client python3 /client/test_client.py --host attacker --port 2222
echo.
echo 3️⃣  For detailed walkthrough:
echo    type LAB_WALKTHROUGH.md
echo.
echo 4️⃣  To stop the lab:
echo    docker-compose down
echo.
echo ⚠️  Remember: Educational use only!
echo.
pause
goto end

:build
echo [*] Building Docker containers...
docker-compose build
if %ERRORLEVEL% NEQ 0 (
    echo [!] Build failed
    pause
    exit /b 1
)
echo [✓] Build completed
if "%1"=="build" goto end
pause
goto menu

:stop
echo [*] Stopping lab...
docker-compose stop
if "%1"=="stop" goto end
pause
goto menu

:down
echo [*] Stopping and removing lab...
docker-compose down
if "%1"=="down" goto end
pause
goto menu

:end
echo.
echo Goodbye!
