#!/bin/bash
# Setup script for vulnerable SSH server

echo "=========================================="
echo "Terrapin Attack - Vulnerable SSH Server"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This is a deliberately vulnerable SSH server"
echo "    for educational purposes only!"
echo ""

# Display available users
echo "Available test accounts:"
echo "  - Username: testuser, Password: password123"
echo "  - Username: root, Password: rootpassword"
echo ""

# Display server configuration
echo "Server configuration:"
echo "  - Port: 22"
echo "  - Vulnerable ciphers enabled: chacha20-poly1305@openssh.com"
echo "  - Extension info enabled"
echo ""

# Check OpenSSH version
OPENSSH_VERSION=$(ssh -V 2>&1)
echo "OpenSSH version: $OPENSSH_VERSION"
echo ""

# Display host keys
echo "Host keys generated:"
ls -la /etc/ssh/ssh_host_*_key.pub | awk '{print "  - " $NF}'
echo ""

# Start SSH daemon
echo "Starting SSH daemon..."
/usr/sbin/sshd -D -e
