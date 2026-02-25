#!/usr/bin/env python3
"""
PCAP Analysis Tool for Terrapin Attack
Analyzes captured SSH traffic for Terrapin attack indicators
"""

import sys
import struct
import argparse
from collections import defaultdict


class SSHPacketAnalyzer:
    """
    Analyze SSH packets from capture
    """
    
    SSH_MSG_TYPES = {
        1: 'SSH_MSG_DISCONNECT',
        2: 'SSH_MSG_IGNORE',
        7: 'SSH_MSG_EXT_INFO',
        20: 'SSH_MSG_KEXINIT',
        21: 'SSH_MSG_NEWKEYS',
        30: 'SSH_MSG_KEX_ECDH_INIT',
        31: 'SSH_MSG_KEX_ECDH_REPLY',
    }
    
    def __init__(self, pcap_file: str):
        """
        Initialize analyzer
        
        Args:
            pcap_file: Path to PCAP file
        """
        self.pcap_file = pcap_file
        self.packets = []
        self.connections = defaultdict(list)
        
        self.stats = {
            'total_packets': 0,
            'ssh_packets': 0,
            'kexinit_count': 0,
            'newkeys_count': 0,
            'ext_info_count': 0,
            'connections': 0
        }
        
        self.attack_indicators = []
    
    def analyze(self):
        """
        Analyze PCAP file
        """
        print(f"[*] Analyzing: {self.pcap_file}")
        print("-" * 60)
        
        try:
            # Try to use scapy if available
            from scapy.all import rdpcap, TCP, Raw, IP
            
            packets = rdpcap(self.pcap_file)
            self.stats['total_packets'] = len(packets)
            
            print(f"[+] Loaded {len(packets)} packets")
            
            # Analyze each packet
            for pkt in packets:
                if TCP in pkt and Raw in pkt:
                    self._analyze_packet(pkt)
            
            # Detect attack patterns
            self._detect_attack_patterns()
            
            # Print results
            self._print_analysis()
            
        except ImportError:
            print("[-] Scapy not available, using simplified analysis")
            self._simple_analysis()
        except Exception as e:
            print(f"[-] Error: {e}")
    
    def _analyze_packet(self, pkt):
        """
        Analyze individual packet
        """
        try:
            from scapy.all import TCP, Raw, IP
            
            # Extract connection tuple
            conn_tuple = (
                pkt[IP].src, pkt[TCP].sport,
                pkt[IP].dst, pkt[TCP].dport
            )
            
            # Get SSH data
            ssh_data = bytes(pkt[Raw].load)
            
            # Try to parse as SSH packet
            if len(ssh_data) >= 6:
                # Check if it looks like an SSH packet
                packet_length = struct.unpack('>I', ssh_data[:4])[0]
                
                if 0 < packet_length < 35000:  # Reasonable SSH packet size
                    self.stats['ssh_packets'] += 1
                    
                    padding_length = ssh_data[4]
                    
                    if len(ssh_data) > 5:
                        msg_type = ssh_data[5]
                        
                        # Track message types
                        if msg_type == 20:
                            self.stats['kexinit_count'] += 1
                            self.connections[conn_tuple].append(('KEXINIT', pkt.time))
                        elif msg_type == 21:
                            self.stats['newkeys_count'] += 1
                            self.connections[conn_tuple].append(('NEWKEYS', pkt.time))
                        elif msg_type == 7:
                            self.stats['ext_info_count'] += 1
                            self.connections[conn_tuple].append(('EXT_INFO', pkt.time))
        
        except Exception:
            pass
    
    def _detect_attack_patterns(self):
        """
        Detect Terrapin attack patterns
        """
        self.stats['connections'] = len(self.connections)
        
        for conn_tuple, messages in self.connections.items():
            # Look for NEWKEYS without following EXT_INFO
            newkeys_indices = [i for i, (msg, _) in enumerate(messages) if msg == 'NEWKEYS']
            ext_info_indices = [i for i, (msg, _) in enumerate(messages) if msg == 'EXT_INFO']
            
            for nk_idx in newkeys_indices:
                # Check if EXT_INFO follows NEWKEYS
                ext_info_follows = any(ei_idx == nk_idx + 1 for ei_idx in ext_info_indices)
                
                if not ext_info_follows and len(messages) > nk_idx + 1:
                    self.attack_indicators.append({
                        'connection': conn_tuple,
                        'type': 'Missing EXT_INFO after NEWKEYS',
                        'index': nk_idx
                    })
    
    def _simple_analysis(self):
        """
        Simple analysis without scapy
        """
        try:
            with open(self.pcap_file, 'rb') as f:
                data = f.read()
                
                # Look for SSH version strings
                ssh_versions = []
                offset = 0
                while True:
                    idx = data.find(b'SSH-2.0-', offset)
                    if idx == -1:
                        break
                    
                    end_idx = data.find(b'\r\n', idx)
                    if end_idx != -1:
                        version = data[idx:end_idx].decode('utf-8', errors='ignore')
                        ssh_versions.append(version)
                    
                    offset = idx + 1
                
                print(f"[+] Found {len(ssh_versions)} SSH version strings")
                for ver in set(ssh_versions):
                    print(f"    {ver}")
        
        except Exception as e:
            print(f"[-] Error in simple analysis: {e}")
    
    def _print_analysis(self):
        """
        Print analysis results
        """
        print("\n" + "=" * 60)
        print("TRAFFIC ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"Total Packets: {self.stats['total_packets']}")
        print(f"SSH Packets: {self.stats['ssh_packets']}")
        print(f"Connections: {self.stats['connections']}")
        print()
        
        print("SSH Message Counts:")
        print(f"  KEXINIT:  {self.stats['kexinit_count']}")
        print(f"  NEWKEYS:  {self.stats['newkeys_count']}")
        print(f"  EXT_INFO: {self.stats['ext_info_count']}")
        print()
        
        # Attack indicators
        if self.attack_indicators:
            print("=" * 60)
            print("⚠️  ATTACK INDICATORS DETECTED")
            print("=" * 60)
            
            for indicator in self.attack_indicators:
                print(f"\n[!] {indicator['type']}")
                conn = indicator['connection']
                print(f"    Connection: {conn[0]}:{conn[1]} -> {conn[2]}:{conn[3]}")
                print(f"    Message index: {indicator['index']}")
            
            print()
            print("These indicators suggest a possible Terrapin attack:")
            print("  - NEWKEYS message was sent")
            print("  - EXT_INFO message is missing or delayed")
            print("  - This is consistent with packet dropping attack")
        else:
            print("✅ No obvious attack indicators detected")
        
        print()
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze PCAP for Terrapin attack indicators'
    )
    
    parser.add_argument('pcap_file',
                       help='PCAP file to analyze')
    
    args = parser.parse_args()
    
    analyzer = SSHPacketAnalyzer(args.pcap_file)
    analyzer.analyze()


if __name__ == '__main__':
    main()
