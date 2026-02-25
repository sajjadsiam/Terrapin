#!/bin/bash
# Start packet capture for SSH traffic

OUTPUT_DIR="/attack/captures"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CAPTURE_FILE="$OUTPUT_DIR/ssh_capture_$TIMESTAMP.pcap"

mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "SSH Packet Capture"
echo "=========================================="
echo ""
echo "[+] Starting capture..."
echo "    Output: $CAPTURE_FILE"
echo "    Filter: port 22"
echo ""
echo "Press Ctrl+C to stop capture"
echo ""

# Start tcpdump
tcpdump -i any -w "$CAPTURE_FILE" port 22

echo ""
echo "[+] Capture saved to: $CAPTURE_FILE"
echo ""
echo "To analyze:"
echo "  ./tools/analyze_traffic.sh $CAPTURE_FILE"
