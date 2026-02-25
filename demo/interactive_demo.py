#!/usr/bin/env python3
"""
Interactive Terrapin Attack Demo
Provides a guided walkthrough of the attack
"""

import os
import sys
import time
import subprocess


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60 + "\n")


def wait_for_enter(prompt="Press Enter to continue..."):
    """Wait for user to press Enter"""
    input(f"\n{prompt}\n")


def run_command(cmd, description):
    """Run a command and display output"""
    print(f"[*] {description}")
    print(f"    Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"[!] Error: {e}")
        return False


def main():
    """Main interactive demo"""
    
    clear_screen()
    
    print("""
╔════════════════════════════════════════════════════════════╗
║      TERRAPIN ATTACK - INTERACTIVE DEMONSTRATION          ║
║                   CVE-2023-48795                          ║
║                                                            ║
║         This script will guide you through the             ║
║         Terrapin attack step-by-step                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    wait_for_enter("Press Enter to begin the demonstration...")
    
    # Step 1: Introduction
    clear_screen()
    print_header("Step 1: Understanding the Terrapin Attack")
    
    print("""
The Terrapin attack (CVE-2023-48795) is a prefix truncation attack
against the SSH protocol. It exploits:

  • Sequence number manipulation during key exchange
  • Lack of integrity protection for certain messages
  • Predictable packet structure in vulnerable ciphers

The attacker positions themselves as a Man-in-the-Middle and drops
the SSH_MSG_EXT_INFO packet, preventing security extensions from
being activated.

Impact:
  ✗ Security feature downgrade
  ✗ Potential for further attacks
  ✗ Silent compromise (no detection by client or server)
    """)
    
    wait_for_enter()
    
    # Step 2: Environment Check
    clear_screen()
    print_header("Step 2: Checking Lab Environment")
    
    print("Let's verify that the lab containers are running...\n")
    time.sleep(1)
    
    if not run_command("docker-compose ps", "Checking container status"):
        print("\n[!] Containers are not running!")
        print("    Please run: docker-compose up -d")
        sys.exit(1)
    
    wait_for_enter()
    
    # Step 3: Vulnerability Check
    clear_screen()
    print_header("Step 3: Verifying Target Vulnerability")
    
    print("""
Before attacking, we need to verify that the target server is
vulnerable. We'll check for:

  1. Vulnerable cipher suites (ChaCha20-Poly1305)
  2. Extension info support (ext-info-s/c)
  3. SSH protocol version

Let's scan the vulnerable server...
    """)
    
    time.sleep(2)
    
    run_command(
        "docker exec terrapin-attacker python3 /attack/demo/verify_vulnerability.py --host vulnerable-server",
        "Running vulnerability scanner"
    )
    
    wait_for_enter()
    
    # Step 4: Normal Connection
    clear_screen()
    print_header("Step 4: Baseline - Normal SSH Connection")
    
    print("""
First, let's see what a NORMAL SSH connection looks like without
any attack. This will be our baseline.

The client will connect directly to the vulnerable server on port 22.
    """)
    
    wait_for_enter("Press Enter to establish normal connection...")
    
    print("\n[*] Connecting to vulnerable-server:22...\n")
    time.sleep(1)
    
    run_command(
        "docker exec terrapin-client python3 /client/test_client.py --host vulnerable-server",
        "Testing normal SSH connection"
    )
    
    print("""
✅ Normal connection successful!
   Notice that all security features are working as expected.
    """)
    
    wait_for_enter()
    
    # Step 5: Attack Setup
    clear_screen()
    print_header("Step 5: Setting Up the Attack")
    
    print("""
Now we'll set up the Man-in-the-Middle attack:

  1. Enable IP forwarding on the attacker
  2. Configure network rules
  3. Start the attack proxy on port 2222

The attacker will:
  ✓ Forward normal traffic between client and server
  ✓ Monitor for SSH_MSG_NEWKEYS messages
  ✓ Drop SSH_MSG_EXT_INFO packets
  ✓ Let all other traffic pass through
    """)
    
    wait_for_enter("Press Enter to configure the attacker...")
    
    run_command(
        "docker exec terrapin-attacker /attack/mitm_setup.sh",
        "Configuring MITM environment"
    )
    
    wait_for_enter()
    
    # Step 6: Launch Attack
    clear_screen()
    print_header("Step 6: Launching the Terrapin Attack")
    
    print("""
⚠️  IMPORTANT: The next step requires TWO terminals!

Terminal 1 (THIS TERMINAL):
  Will start the attack proxy and wait for connections

Terminal 2 (OPEN A NEW TERMINAL):
  Will connect through the attack proxy
  Run this command:
  
  docker exec -it terrapin-client python3 /client/test_client.py --host attacker --port 2222

When you run the client command, watch THIS terminal for:
  🎯 "DROPPING SSH_MSG_EXT_INFO from server!"

This proves the attack is working!
    """)
    
    wait_for_enter("Press Enter to start the attack proxy (then open second terminal)...")
    
    print("\n" + "="*60)
    print(" ATTACK PROXY STARTING - Waiting for client connection...")
    print("="*60)
    print("\n[!] Open a second terminal and run the client command now!\n")
    
    run_command(
        "docker exec -it terrapin-attacker python3 /attack/poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22 --proxy-port 2222",
        "Starting Terrapin attack proxy"
    )
    
    wait_for_enter("\nDid you see the attack message? Press Enter to continue...")
    
    # Step 7: Analysis
    clear_screen()
    print_header("Step 7: What Just Happened?")
    
    print("""
Let's review what occurred during the attack:

1️⃣  Client initiated connection to attacker:2222
   (Client thinks it's connecting to the real server)

2️⃣  Attacker forwarded initial handshake
   (Protocol version exchange, KEXINIT)

3️⃣  Key exchange completed normally
   (Diffie-Hellman key exchange, NEWKEYS sent)

4️⃣  Server sent SSH_MSG_EXT_INFO (sequence 0 after NEWKEYS)
   ⚠️  ATTACKER DROPPED THIS PACKET

5️⃣  Next packet assumed sequence 0
   (Connection continued without detecting the drop)

6️⃣  Security extensions NOT activated
   (But connection appeared successful!)

Result:
  ✗ Client and server unaware of the attack
  ✗ Security features silently disabled
  ✗ Session established with downgraded security
    """)
    
    wait_for_enter()
    
    # Step 8: Conclusion
    clear_screen()
    print_header("Step 8: Demonstration Complete!")
    
    print("""
Congratulations! You've successfully demonstrated the Terrapin attack.

Key Takeaways:

  🎯 The attack exploits SSH sequence number handling
  🎯 Vulnerable ciphers make packet identification trivial
  🎯 EXT_INFO dropping downgrades security features
  🎯 Attack is silent - no detection by either party

Real-World Impact:
  • Affects many SSH implementations (OpenSSH, PuTTY, etc.)
  • CVSS Score: 5.9 (Medium)
  • Fixed in newer versions (OpenSSH 9.6+)

Mitigation:
  ✓ Update SSH software to latest version
  ✓ Disable vulnerable cipher suites
  ✓ Use strict key exchange (if available)
  ✓ Monitor for unusual connection patterns

Next Steps:
  📖 Read ATTACK_DETAILS.md for technical deep-dive
  🔬 Experiment with different scenarios
  🛡️  Learn about detection and mitigation
  📝 Review the captured traffic

Thank you for completing this demonstration!
Remember: Use this knowledge responsibly and ethically.
    """)
    
    print("\n" + "="*60)
    print(" To stop the lab: docker-compose down")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Demo interrupted by user")
        sys.exit(0)
