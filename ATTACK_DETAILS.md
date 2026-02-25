# Terrapin Attack - Technical Deep Dive

## Overview

The Terrapin attack (CVE-2023-48795) is a sophisticated prefix truncation attack against the SSH protocol. It exploits a fundamental weakness in how SSH handles sequence numbers during the key exchange phase.

## SSH Protocol Background

### Normal SSH Handshake

```
1. TCP Connection Established
2. Protocol Version Exchange (SSH-2.0-...)
3. Key Exchange Init (SSH_MSG_KEXINIT)
4. Key Exchange (Diffie-Hellman)
5. New Keys (SSH_MSG_NEWKEYS)
6. Service Request (ssh-userauth)
7. Authentication
8. Channel Open
9. Encrypted Communication
```

### Sequence Numbers in SSH

SSH maintains sequence numbers for integrity:
- Each side maintains independent sequence counters
- Counters start at 0 after SSH_MSG_NEWKEYS
- Used for replay protection and ordering

## The Vulnerability

### Root Cause

The vulnerability exists because:

1. **Implicit vs Explicit Reset**: SSH resets sequence numbers after `SSH_MSG_NEWKEYS` without explicit acknowledgment
2. **No Transcript Hash**: Some messages aren't included in the key exchange hash
3. **Timing Window**: Between sending NEWKEYS and receiving encrypted data

### Affected Algorithms

#### ChaCha20-Poly1305
```
Cipher: chacha20-poly1305@openssh.com
Problem: Uses length-encrypted packets
Attack: Trivial to identify and drop specific packets
```

#### CBC with Encrypt-then-MAC
```
Cipher: aes{128,192,256}-cbc
MAC: hmac-sha2-{256,512}
Problem: Predictable packet structure
Attack: Can identify extension negotiation packets
```

## Attack Mechanics

### Phase 1: MITM Positioning

```python
# Attacker positions between client and server
[Client] <----> [Attacker] <----> [Server]

# Uses ARP spoofing or network positioning
```

### Phase 2: Handshake Interception

The attacker monitors for:
- `SSH_MSG_KEXINIT` (message type 20)
- Extension negotiation fields (`ext-info-c`, `ext-info-s`)

### Phase 3: Packet Manipulation

**Critical: Drop SSH_MSG_EXT_INFO**

```
Client sends:
├── SSH_MSG_KEXINIT (contains ext-info-c)
├── SSH_MSG_KEX_ECDH_INIT
├── SSH_MSG_NEWKEYS
└── SSH_MSG_EXT_INFO ← ATTACKER DROPS THIS

Server perspective:
- Sees NEWKEYS
- Resets sequence counter to 0
- Expects sequence 0 next
- Never receives EXT_INFO (was sequence 0)
- Next packet becomes sequence 0
```

### Phase 4: Sequence Number Confusion

```
Without Attack:
Seq 0: SSH_MSG_EXT_INFO
Seq 1: SSH_MSG_SERVICE_REQUEST
Seq 2: ...

With Attack (after dropping EXT_INFO):
Seq 0: SSH_MSG_SERVICE_REQUEST (was seq 1)
Seq 1: ... (was seq 2)

Result: Server never realizes a packet was dropped
```

## Exploitation Scenarios

### Scenario 1: Extension Downgrade

**Goal**: Remove security extensions

```python
# Extensions that can be removed:
- server-sig-algs
- publickey-hostbound@openssh.com
- rsa-sha2-256
- rsa-sha2-512
```

**Impact**:
- Forces use of weaker algorithms
- Disables security features
- May enable other attacks

### Scenario 2: Async Protocol Attacks

**Goal**: Inject rogue packets in async messages

For protocols using SSH for transport but with async messages:
```
1. Establish SSH connection via Terrapin
2. During async message exchange
3. Inject malicious packets
4. Victim accepts due to sequence confusion
```

### Scenario 3: Command Injection (Theoretical)

In specific configurations:
```python
# If attacker can predict traffic patterns
# And async mode is used
# Potentially inject commands
```

## Proof of Concept Structure

### Detection Phase

```python
def detect_vulnerable_server(host, port):
    """
    Check if server uses vulnerable configurations
    """
    # Connect and capture KEXINIT
    # Check for:
    # 1. chacha20-poly1305@openssh.com
    # 2. CBC with encrypt-then-mac
    # 3. ext-info-s in kex algorithms
    pass
```

### Attack Phase

```python
def execute_terrapin_attack():
    """
    Main attack flow
    """
    # 1. Position as MITM
    setup_mitm()
    
    # 2. Forward initial handshake
    forward_packets(until=SSH_MSG_KEXINIT)
    
    # 3. Wait for NEWKEYS
    wait_for_newkeys()
    
    # 4. Drop EXT_INFO packet
    drop_ext_info_packet()
    
    # 5. Continue forwarding
    forward_remaining_traffic()
```

### Verification Phase

```python
def verify_attack_success():
    """
    Confirm the attack worked
    """
    # Check:
    # 1. Connection established
    # 2. EXT_INFO not acknowledged
    # 3. Sequence numbers misaligned
    # 4. Extensions not active
    pass
```

## Technical Implementation Details

### Packet Identification

#### ChaCha20-Poly1305 Encrypted Packet Structure

```
+-----------+------------------+-----------+
| Length    | Encrypted        | MAC Tag   |
| (4 bytes) | (variable)       | (16 bytes)|
+-----------+------------------+-----------+
           ^
           Encrypted with packet sequence number
```

#### Identifying SSH_MSG_EXT_INFO

```python
# Before encryption (plaintext)
packet = {
    'length': 4,           # Packet length
    'padding_length': 1,   # Padding
    'msg_type': 7,         # SSH_MSG_EXT_INFO
    'payload': ...,        # Extensions
    'padding': ...         # Random padding
}

# After NEWKEYS, this is packet with sequence 0
# Length is predictable based on extensions
```

### Timing Considerations

```
Critical Timing Window:
T0: Server sends SSH_MSG_NEWKEYS
T1: Server resets sequence to 0
T2: Server sends SSH_MSG_EXT_INFO (seq 0)
T3: Client receives NEWKEYS
T4: Client resets sequence to 0
T5: Client sends SSH_MSG_EXT_INFO (seq 0)

Attack Window: Between T2-T3 or T5-T6
Duration: ~1-10ms depending on network
```

### Network Requirements

For successful attack:
```
- Round-trip time: < 100ms (ideal)
- Packet loss: < 0.1%
- Attacker latency: < 5ms from both parties
- No duplicate packet detection
```

## Countermeasures

### Protocol Level

**Strict KEX (RFC Draft)**:
```
kex-strict-c-v00@openssh.com
kex-strict-s-v00@openssh.com

Changes:
- Track if unexpected sequence number
- Terminate on missing packets
- Explicit sequence validation
```

### Implementation Level

1. **Bind Extensions to KEX Hash**:
```python
kex_hash = hash(
    V_C || V_S || I_C || I_S ||  # Original
    K_S || e || f || K ||        # Original
    EXT_INFO_C || EXT_INFO_S     # Add this
)
```

2. **Explicit Sequence Acknowledgment**:
```python
SSH_MSG_NEWKEYS_ACK = {
    'type': NEW_MSG_TYPE,
    'last_seq_before_reset': current_seq,
    'expected_seq_after': 0
}
```

3. **Mandatory Extensions**:
```python
if 'ext-info-c' in client_kexinit:
    connection.require_ext_info = True
    
if not received_ext_info and require_ext_info:
    disconnect("Missing required extension")
```

### Detection Mechanisms

#### Server-Side Detection

```python
def detect_terrapin_attack():
    """
    Detect potential Terrapin attack
    """
    indicators = []
    
    # Check 1: Missing EXT_INFO
    if supports_ext_info and not received_ext_info:
        indicators.append("Missing EXT_INFO")
    
    # Check 2: Timing anomaly
    if ext_info_delay > threshold:
        indicators.append("Delayed EXT_INFO")
    
    # Check 3: Sequence gap
    if sequence_gap_detected():
        indicators.append("Sequence anomaly")
    
    return len(indicators) > 0
```

#### Network-Level Detection

```bash
# Monitor for dropped packets during handshake
tcpdump -i any 'tcp[13] & 8 != 0 and port 22' | \
  grep -A 10 "SSH_MSG_NEWKEYS"
```

## Real-World Impact

### Affected Software

- OpenSSH < 9.6
- PuTTY < 0.80
- FileZilla < 3.66.0
- WinSCP < 6.3.0
- libssh < 0.10.6
- AsyncSSH < 2.14.2
- Many commercial SSH implementations

### Exploitation Difficulty

```
Difficulty: MEDIUM
Requires:
✓ MITM position
✓ Precise timing
✓ Packet manipulation capability
✓ Knowledge of SSH internals

Typical Success Rate: 80-95% in lab conditions
Real-world Success Rate: 30-60% (depends on network)
```

### Security Implications

1. **Extension Downgrade**: HIGH
   - Removes important security features
   - May enable other attacks

2. **Direct Command Injection**: LOW
   - Very specific conditions required
   - Limited practical scenarios

3. **Async Protocol Attacks**: MEDIUM
   - Depends on higher-layer protocol
   - Potential for data manipulation

## Research References

1. **Original Paper**: "Terrapin Attack: Breaking SSH Channel Integrity By Sequence Number Manipulation"
   - Authors: Fabian Bäumer, Marcus Brinkmann, Jörg Schwenk
   - Institution: Ruhr University Bochum
   - Date: December 2023

2. **CVE-2023-48795**: https://nvd.nist.gov/vuln/detail/CVE-2023-48795

3. **OpenSSH Response**: https://www.openssh.com/txt/release-9.6

4. **IETF Response**: Draft-ietf-curdle-ssh-kex-sha2

## Conclusion

The Terrapin attack demonstrates that even mature protocols like SSH can have subtle vulnerabilities. It emphasizes the importance of:

- Explicit integrity protection
- Comprehensive security proofs
- Regular protocol audits
- Defense-in-depth approaches

While the immediate impact is limited, it represents a class of attacks that could be more severe in other contexts.
