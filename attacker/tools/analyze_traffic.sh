#!/bin/bash
# SSH Traffic Analyzer

CAPTURE_FILE=$1

if [ -z "$CAPTURE_FILE" ]; then
    echo "Usage: $0 <capture_file.pcap>"
    exit 1
fi

if [ ! -f "$CAPTURE_FILE" ]; then
    echo "Error: Capture file not found: $CAPTURE_FILE"
    exit 1
fi

echo "=========================================="
echo "SSH Traffic Analysis"
echo "=========================================="
echo ""

echo "[*] Analyzing capture file: $CAPTURE_FILE"
echo ""

# Count total SSH packets
TOTAL_PACKETS=$(tshark -r "$CAPTURE_FILE" tcp.port==22 2>/dev/null | wc -l)
echo "[+] Total SSH packets: $TOTAL_PACKETS"

# Look for SSH handshake
echo ""
echo "[*] SSH Protocol Exchange:"
tshark -r "$CAPTURE_FILE" -Y "ssh" -T fields -e frame.number -e ip.src -e ip.dst -e ssh.protocol 2>/dev/null | head -n 10

# Look for specific SSH messages (if decrypted)
echo ""
echo "[*] Looking for key exchange messages..."
tshark -r "$CAPTURE_FILE" -Y "ssh" -T fields -e frame.number -e ssh.message_code 2>/dev/null | \
    grep -E "20|21|7" | \
    while read frame msg_code; do
        case $msg_code in
            20) echo "  Frame $frame: SSH_MSG_KEXINIT" ;;
            21) echo "  Frame $frame: SSH_MSG_NEWKEYS" ;;
            7)  echo "  Frame $frame: SSH_MSG_EXT_INFO" ;;
        esac
    done

echo ""
echo "[*] Analysis complete"
