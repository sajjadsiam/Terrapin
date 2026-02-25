@echo off
REM Terrapin Attack - Packet Capture with Wireshark

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║      TERRAPIN ATTACK - WIRESHARK PACKET CAPTURE         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [*] This script will:
echo     1. Start packet capture on attacker container
echo     2. Run the attack
echo     3. Save pcap file for Wireshark analysis
echo.

REM Start packet capture
echo [*] Starting packet capture...
docker exec -d terrapin-attacker tcpdump -i eth0 -w /attack/captures/terrapin_attack.pcap tcp port 22
timeout /t 2 /nobreak >nul
echo [+] Capture started

REM Start attack proxy
echo.
echo [*] Starting MITM proxy...
echo [*] Press Ctrl+C after attack completes to stop capture
echo.
start /min cmd /c "timeout /t 5 /nobreak >nul && docker exec -it terrapin-client ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 testuser@attacker"

REM Run attack
docker exec -it terrapin-attacker python3 /attack/manual_attack_demo.py

REM Stop capture
echo.
echo [*] Stopping packet capture...
docker exec terrapin-attacker pkill tcpdump 2>nul
timeout /t 2 /nobreak >nul

REM Copy pcap file
echo [*] Copying pcap file to captures\ folder...
if not exist "captures" mkdir captures
docker cp terrapin-attacker:/attack/captures/terrapin_attack.pcap captures\

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                  CAPTURE COMPLETE!                       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo [+] Packet capture saved to: captures\terrapin_attack.pcap
echo.
echo [*] To analyze:
echo     1. Install Wireshark: https://www.wireshark.org/
echo     2. Open: captures\terrapin_attack.pcap
echo     3. Apply filter: ssh
echo     4. Look for missing SSH_MSG_EXT_INFO (type 7)
echo.
echo [*] Opening captures folder...
start captures

pause
