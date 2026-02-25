# Troubleshooting Guide

This guide covers common issues you might encounter while setting up and running the Terrapin Attack demo lab.

## Table of Contents

1. [Docker Issues](#docker-issues)
2. [Container Issues](#container-issues)
3. [Network Issues](#network-issues)
4. [Attack Issues](#attack-issues)
5. [Performance Issues](#performance-issues)
6. [Platform-Specific Issues](#platform-specific-issues)

## Docker Issues

### Docker is not installed

**Symptom**: `docker: command not found`

**Solution**:
```bash
# Linux (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Or install Docker Desktop:
# Windows: https://docs.docker.com/desktop/install/windows-install/
# Mac: https://docs.docker.com/desktop/install/mac-install/
```

### Docker daemon is not running

**Symptom**: `Cannot connect to the Docker daemon`

**Solution**:
```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# Windows/Mac: Start Docker Desktop application
```

### Permission denied while trying to connect to Docker daemon

**Symptom**: `permission denied while trying to connect to the Docker daemon socket`

**Solution**:
```bash
# Add your user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Log out and back in for changes to take effect
```

## Container Issues

### Containers fail to build

**Symptom**: `ERROR [internal] load metadata for docker.io/library/ubuntu:22.04`

**Solution**:
```bash
# Pull base image manually
docker pull ubuntu:22.04

# Rebuild
docker-compose build --no-cache
```

### Container exits immediately

**Symptom**: Container appears running then immediately stops

**Solution**:
```bash
# Check container logs
docker logs terrapin-vulnerable-server
docker logs terrapin-attacker
docker logs terrapin-client

# Look for errors and address them
```

### Containers won't start

**Symptom**: `Error starting userland proxy: listen tcp4 0.0.0.0:2222: bind: address already in use`

**Solution**:
```bash
# Check what's using the port
netstat -ano | findstr :2222  # Windows
netstat -nlp | grep :2222     # Linux/Mac

# Stop the conflicting process or change ports in docker-compose.yml
```

### Cannot access container shell

**Symptom**: `docker exec` fails or container not found

**Solution**:
```bash
# List running containers
docker ps

# Check if container name is correct
docker-compose ps

# Start if stopped
docker-compose up -d

# Use correct container name
docker exec -it terrapin-attacker /bin/bash
```

## Network Issues

### Containers cannot communicate

**Symptom**: `Connection refused` when trying to connect between containers

**Solution**:
```bash
# Check network exists
docker network ls | grep terrapin

# Inspect network
docker network inspect terapin_terrapin-net

# Verify all containers are on same network
docker inspect terrapin-attacker | grep NetworkMode

# Recreate network
docker-compose down
docker-compose up -d
```

### Cannot reach containers from host

**Symptom**: Cannot connect to published ports from host machine

**Solution**:
```bash
# Verify ports are actually published
docker port terrapin-vulnerable-server

# Check if something else is using the port
# Windows
netstat -ano | findstr :2222
# Linux/Mac
sudo lsof -i :2222

# Try different port in docker-compose.yml
```

### DNS resolution fails

**Symptom**: `Could not resolve hostname: vulnerable-server`

**Solution**:
```bash
# Use IP address instead
docker exec terrapin-client python3 /client/test_client.py --host 172.20.0.10

# Or check Docker DNS
docker exec terrapin-client nslookup vulnerable-server

# Restart containers
docker-compose restart
```

## Attack Issues

### Server shows as not vulnerable

**Symptom**: Verification script says "NOT VULNERABLE"

**Possible causes and solutions**:

1. **Server configuration issue**
```bash
# Check SSH config
docker exec terrapin-vulnerable-server cat /etc/ssh/sshd_config | grep Cipher

# Should include chacha20-poly1305@openssh.com
```

2. **Server not reachable**
```bash
# Test connectivity
docker exec terrapin-attacker nc -zv vulnerable-server 22

# Check if SSH is running
docker exec terrapin-vulnerable-server ps aux | grep sshd
```

3. **Wrong version of OpenSSH (too new)**
```bash
# Check version
docker exec terrapin-vulnerable-server ssh -V

# Rebuild with older version if needed
```

### Attack proxy doesn't intercept packets

**Symptom**: Client connects but attack messages not shown

**Possible causes**:

1. **Client connecting to wrong host/port**
```bash
# Make sure client connects to: attacker:2222
# NOT to: vulnerable-server:22

# Correct:
docker exec terrapin-client python3 /client/test_client.py --host attacker --port 2222

# Wrong:
docker exec terrapin-client python3 /client/test_client.py --host vulnerable-server
```

2. **IP forwarding not enabled**
```bash
# Run MITM setup
docker exec terrapin-attacker /attack/mitm_setup.sh

# Verify
docker exec terrapin-attacker cat /proc/sys/net/ipv4/ip_forward
# Should output: 1
```

3. **Firewall blocking traffic**
```bash
# Check iptables
docker exec terrapin-attacker iptables -L

# Flush and reconfigure
docker exec terrapin-attacker iptables -F
docker exec terrapin-attacker /attack/mitm_setup.sh
```

### EXT_INFO not being dropped

**Symptom**: Connection works but no "DROPPING" message

**Debug steps**:
```bash
# Run with verbose flag
docker exec terrapin-attacker python3 /attack/poc_exploit/terrapin_exploit.py \
  --target vulnerable-server --port 22 --proxy-port 2222 --verbose

# Check if cipher negotiation succeeded
# The cipher must be chacha20-poly1305@openssh.com or another vulnerable one

# Capture and analyze traffic
docker exec terrapin-attacker tcpdump -i any -w /tmp/debug.pcap port 22
# Analyze with: tshark -r /tmp/debug.pcap -V
```

### Connection times out

**Symptom**: Connection hangs or times out

**Solutions**:
```bash
# Increase timeout
docker exec terrapin-client python3 /client/test_client.py \
  --host attacker --port 2222 --timeout 30

# Check if proxy is running
docker exec terrapin-attacker ps aux | grep terrapin_exploit

# Check network connectivity
docker exec terrapin-client ping -c 3 attacker
docker exec terrapin-attacker ping -c 3 vulnerable-server
```

## Performance Issues

### Containers are slow

**Symptom**: Commands take a long time to execute

**Solutions**:
```bash
# Check Docker resource allocation (Desktop)
# Settings → Resources → Increase memory/CPU

# Check system resources
docker stats

# Remove unused containers/images
docker system prune -a
```

### Build takes too long

**Symptom**: `docker-compose build` is very slow

**Solutions**:
```bash
# Use BuildKit
export DOCKER_BUILDKIT=1
docker-compose build

# Clear build cache
docker builder prune

# Use pre-built images (if available)
```

## Platform-Specific Issues

### Windows Issues

#### Line ending problems

**Symptom**: `/bin/bash^M: bad interpreter`

**Solution**:
```bash
# Convert line endings in git
git config --global core.autocrlf input
git clone <repo> --config core.autocrlf=input

# Or manually fix
dos2unix setup.sh
```

#### Path issues in volumes

**Symptom**: Volume mounts don't work

**Solution**:
```yaml
# In docker-compose.yml, use absolute Windows paths or
# Enable "Expose daemon on tcp://localhost:2375" in Docker Desktop settings

# Or use WSL2 for better Linux compatibility
```

### Mac Issues

#### M1/M2 compatibility

**Symptom**: `The requested image's platform (linux/amd64) does not match`

**Solution**:
```yaml
# Add to service in docker-compose.yml:
platform: linux/amd64

# Or build for ARM
platform: linux/arm64
```

### Linux Issues

#### SELinux problems

**Symptom**: Permission denied in containers

**Solution**:
```bash
# Temporarily disable SELinux
sudo setenforce 0

# Or add :z to volumes in docker-compose.yml
volumes:
  - ./logs:/var/log/ssh:z
```

#### AppArmor blocks

**Symptom**: Container cannot perform certain operations

**Solution**:
```bash
# Check AppArmor status
sudo aa-status

# Disable for Docker (temporarily)
sudo systemctl stop apparmor
```

## Python/Script Issues

### ModuleNotFoundError: No module named 'scapy'

**Symptom**: Python import errors

**Solution**:
```bash
# Rebuild containers
docker-compose build --no-cache

# Or install manually
docker exec terrapin-attacker pip3 install -r /attack/poc_exploit/requirements.txt
```

### Script has no execute permission

**Symptom**: `Permission denied` when running scripts

**Solution**:
```bash
# Inside container
docker exec terrapin-attacker chmod +x /attack/mitm_setup.sh
docker exec terrapin-attacker chmod +x /attack/tools/*.sh
```

## Logging and Debugging

### Enable detailed logging

```bash
# SSH server verbose logging
docker exec terrapin-vulnerable-server tail -f /var/log/auth.log

# Attacker detailed output
docker exec terrapin-attacker python3 /attack/poc_exploit/terrapin_exploit.py --verbose

# Network traffic logging
docker exec terrapin-attacker tcpdump -i any -vvv -X port 22
```

### Capture full packet data

```bash
# Start capture before attack
docker exec terrapin-attacker tcpdump -i any -s 65535 -w /attack/captures/full.pcap port 22

# Analyze later
docker exec terrapin-attacker tshark -r /attack/captures/full.pcap -V
```

### Check container logs

```bash
# View logs
docker logs terrapin-vulnerable-server
docker logs terrapin-attacker
docker logs terrapin-client

# Follow logs in real-time
docker logs -f terrapin-attacker

# Show only recent logs
docker logs --tail 50 terrapin-vulnerable-server
```

## Getting More Help

If you're still stuck:

1. **Check the documentation**:
   - [README.md](README.md) - Overview
   - [LAB_WALKTHROUGH.md](LAB_WALKTHROUGH.md) - Detailed steps
   - [ATTACK_DETAILS.md](ATTACK_DETAILS.md) - Technical info

2. **Search for similar issues**:
   - Check GitHub Issues (if repo is public)
   - Search for error messages online

3. **Gather diagnostic information**:
```bash
# System info
uname -a
docker version
docker-compose version

# Container status
docker-compose ps
docker stats --no-stream

# Network info
docker network inspect terapin_terrapin-net

# Logs
docker logs terrapin-vulnerable-server > server.log
docker logs terrapin-attacker > attacker.log
docker logs terrapin-client > client.log
```

4. **Report the issue** with:
   - Full error message
   - Steps to reproduce
   - System information
   - Logs

## Quick Reset

If all else fails, clean slate:

```bash
# Stop everything
docker-compose down

# Remove all related containers
docker ps -a | grep terrapin | awk '{print $1}' | xargs docker rm -f

# Remove network
docker network rm terapin_terrapin-net

# Remove images
docker images | grep terrapin | awk '{print $3}' | xargs docker rmi -f

# Remove volumes
docker volume ls | grep terrapin | awk '{print $2}' | xargs docker volume rm

# Start fresh
docker-compose build --no-cache
docker-compose up -d
```

---

**Still having issues?** Double-check that:
- [ ] Docker is running
- [ ] No port conflicts
- [ ] Containers are actually running (`docker ps`)
- [ ] You're using the correct container/host names
- [ ] Network connectivity works between containers
