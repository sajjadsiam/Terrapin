#!/usr/bin/env python3
"""
SSH Test Client for Terrapin Attack Demo
"""

import paramiko
import sys
import time
import argparse


def test_ssh_connection(host, port, username, password):
    """
    Test SSH connection to server
    
    Args:
        host: SSH server hostname
        port: SSH server port
        username: SSH username
        password: SSH password
    """
    print("="*60)
    print("SSH Test Client")
    print("="*60)
    print(f"\nConnecting to {host}:{port}")
    print(f"Username: {username}")
    print("-"*60)
    
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect
        print("\n[*] Establishing SSH connection...")
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False
        )
        
        print("[+] Successfully connected!")
        
        # Get transport info
        transport = client.get_transport()
        if transport:
            print("\n[*] Connection details:")
            print(f"    Cipher: {transport.get_cipher_name()}")
            print(f"    Remote version: {transport.remote_version}")
            print(f"    Local version: {transport.local_version}")
            
            # Check for security extensions
            print("\n[*] Checking security features...")
            try:
                # This is a simple check - in real scenario would be more detailed
                print("    [?] Extension info status: Unknown (connection established)")
            except Exception as e:
                print(f"    [!] Could not check extensions: {e}")
        
        # Execute a test command
        print("\n[*] Executing test command (whoami)...")
        stdin, stdout, stderr = client.exec_command('whoami')
        result = stdout.read().decode().strip()
        print(f"    Result: {result}")
        
        # Execute another command
        print("\n[*] Executing test command (uname -a)...")
        stdin, stdout, stderr = client.exec_command('uname -a')
        result = stdout.read().decode().strip()
        print(f"    Result: {result}")
        
        print("\n" + "="*60)
        print("✅ Connection test completed successfully")
        print("="*60)
        
        # Keep connection open for a bit
        print("\n[*] Keeping connection open for 5 seconds...")
        time.sleep(5)
        
        # Close connection
        client.close()
        print("[*] Connection closed")
        
        return True
        
    except paramiko.AuthenticationException:
        print("\n❌ Authentication failed!")
        return False
    except paramiko.SSHException as e:
        print(f"\n❌ SSH error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        return False


def interactive_session(host, port, username, password):
    """
    Start an interactive SSH session
    
    Args:
        host: SSH server hostname
        port: SSH server port
        username: SSH username
        password: SSH password
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"[*] Connecting to {host}:{port}...")
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password
        )
        
        print("[+] Connected! Starting interactive shell...")
        print("[*] Type 'exit' to quit\n")
        
        # Start interactive shell
        channel = client.invoke_shell()
        
        while True:
            # Read from channel
            if channel.recv_ready():
                output = channel.recv(1024).decode()
                print(output, end='')
            
            # Get user input
            if channel.send_ready():
                try:
                    cmd = input()
                    if cmd.lower() == 'exit':
                        break
                    channel.send(cmd + '\n')
                except EOFError:
                    break
        
        client.close()
        print("\n[*] Connection closed")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='SSH Test Client for Terrapin Attack Demo'
    )
    
    parser.add_argument('--host', default='vulnerable-server',
                       help='SSH server hostname (default: vulnerable-server)')
    parser.add_argument('--port', type=int, default=22,
                       help='SSH server port (default: 22)')
    parser.add_argument('--username', default='testuser',
                       help='SSH username (default: testuser)')
    parser.add_argument('--password', default='password123',
                       help='SSH password (default: password123)')
    parser.add_argument('--interactive', action='store_true',
                       help='Start interactive session')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_session(args.host, args.port, args.username, args.password)
    else:
        success = test_ssh_connection(args.host, args.port, args.username, args.password)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
