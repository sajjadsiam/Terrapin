# Terrapin Attack - POC & Demo Lab

![Terrapin Attack](https://img.shields.io/badge/CVE-2023--48795-critical)
![SSH Protocol](https://img.shields.io/badge/Protocol-SSH-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ⚠️ Educational Purpose Only

This repository contains a proof-of-concept implementation and demonstration lab for the **Terrapin Attack** (CVE-2023-48795). This is strictly for educational and research purposes only.

## 🎯 What is the Terrapin Attack?

The Terrapin attack is a prefix truncation attack targeting the SSH protocol's integrity. It exploits weaknesses in SSH's handshake sequence number handling, specifically when using ChaCha20-Poly1305 or CBC with Encrypt-then-MAC.

### Attack Vector

The attack works by:
1. **Man-in-the-Middle Position**: Attacker sits between client and server
2. **Sequence Number Manipulation**: Drops specific packets during handshake
3. **Extension Downgrade**: Forces removal of security extensions
4. **Integrity Bypass**: SSH continues without detecting the manipulation

### CVE-2023-48795 Details

- **Discovery Date**: December 2023
- **Affected**: SSH protocol implementations using specific encryption modes
- **Impact**: Integrity compromise, security extension downgrade
- **CVSS Score**: 5.9 (Medium)

## 🏗️ Repository Structure

```
terrapin/
├── README.md                    # This file
├── ATTACK_DETAILS.md           # Technical deep-dive
├── docker-compose.yml          # Lab environment setup
├── poc_exploit/                # Proof of concept code
│   ├── terrapin_exploit.py     # Main exploit script
│   ├── packet_interceptor.py   # Network packet manipulation
│   └── requirements.txt        # Python dependencies
├── vulnerable_server/          # Vulnerable SSH server
│   ├── Dockerfile
│   ├── sshd_config            # Vulnerable configuration
│   └── setup.sh
├── attacker/                   # Attacker machine tools
│   ├── Dockerfile
│   ├── mitm_setup.sh          # MITM configuration
│   └── tools/
├── client/                     # SSH client setup
│   ├── Dockerfile
│   └── test_client.py
└── demo/                       # Demonstration scripts
    ├── run_attack.sh
    ├── verify_vulnerability.py
    └── capture_analysis.py
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Root/Administrator privileges (for network manipulation)

### Setup Lab Environment

1. **Clone and navigate to repository**:
```bash
cd terapin
```

2. **Build the lab environment**:
```bash
docker-compose build
```

3. **Start the lab**:
```bash
docker-compose up -d
```

4. **Verify containers are running**:
```bash
docker-compose ps
```

### Running the Attack

1. **Start the vulnerable server** (already running from docker-compose)

2. **Position as MITM**:
```bash
docker exec -it terrapin-attacker /bin/bash
cd /attack
./mitm_setup.sh
```

3. **Execute the Terrapin attack**:
```bash
python3 poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22
```

4. **Observe the attack**:
```bash
# In another terminal
docker exec -it terrapin-attacker tcpdump -i any -w /tmp/attack.pcap
```

## 🔬 Technical Details

### Vulnerable Configurations

The attack affects SSH when using:
- **ChaCha20-Poly1305** (`chacha20-poly1305@openssh.com`)
- **CBC with Encrypt-then-MAC** (e.g., `aes128-cbc` with `hmac-sha2-256`)

### Attack Mechanism

```
Client                  Attacker (MITM)              Server
  |                           |                         |
  |-------- SSH_MSG_KEXINIT ------->|                  |
  |                           |-------- (Modified) ---->|
  |                           |                         |
  |                           |<------- SSH_MSG_KEXINIT -|
  |<------- (Drop EXT_INFO) --|                         |
  |                           |                         |
  |-- SSH_MSG_NEWKEYS ------->|                         |
  |                           |-- (Sequence Reset) ---->|
  |                           |                         |
  | Connection established with downgraded security     |
```

### Impact

1. **Extension Downgrade**: Removes `ext-info-c` and `ext-info-s`
2. **Security Feature Bypass**: Disables newer SSH security features
3. **Rogue Session**: Potential for injecting commands in async mode

## 📊 Lab Components

### 1. Vulnerable Server
- OpenSSH with vulnerable configuration
- ChaCha20-Poly1305 encryption enabled
- No strict key exchange enforcement

### 2. Attacker Machine
- Packet manipulation tools (Scapy)
- MITM positioning (iptables/nftables)
- Traffic capture and analysis

### 3. Client Machine
- Standard SSH client
- Connection monitoring tools

## 🧪 Testing & Verification

### Check if Server is Vulnerable

```bash
python3 demo/verify_vulnerability.py --host vulnerable-server --port 22
```

### Capture and Analyze Traffic

```bash
# Start capture
tcpdump -i any -w attack_capture.pcap port 22

# Analyze
python3 demo/capture_analysis.py attack_capture.pcap
```

## 🛡️ Mitigation

### For System Administrators

1. **Update SSH Software**:
   - OpenSSH 9.6+ includes fixes
   - Update all SSH clients and servers

2. **Disable Vulnerable Algorithms**:
```
# In sshd_config
Ciphers -chacha20-poly1305@openssh.com
```

3. **Use Strict Key Exchange**:
```
# Add to sshd_config (OpenSSH 9.6+)
StrictHostKeyChecking yes
```

4. **Monitor Connections**:
   - Look for unusual key exchange patterns
   - Monitor for dropped packets during handshake

### Detection

```bash
# Check OpenSSH version
ssh -V

# Test server configuration
./demo/verify_vulnerability.py --host your-server --port 22
```

## 📚 Learning Resources

- [Original Terrapin Attack Paper](https://terrapin-attack.com)
- [CVE-2023-48795 Details](https://nvd.nist.gov/vuln/detail/CVE-2023-48795)
- [SSH Protocol RFC 4253](https://tools.ietf.org/html/rfc4253)

## ⚖️ Legal Notice

This software is provided for **educational and research purposes only**. 

⚠️ **WARNING**: Unauthorized access to computer systems is illegal. Only use this tool on:
- Systems you own
- Systems you have explicit written permission to test
- Isolated lab environments

The authors assume NO responsibility for misuse or damage caused by this software.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Credits

- **Terrapin Attack Discovery**: Fabian Bäumer, Marcus Brinkmann, Jörg Schwenk
- **Research Institution**: Ruhr University Bochum

## 📮 Contact

For questions or research collaboration:
- Open an issue on GitHub
- Security concerns: Please report responsibly

---

**Remember**: With great power comes great responsibility. Use this knowledge ethically.
