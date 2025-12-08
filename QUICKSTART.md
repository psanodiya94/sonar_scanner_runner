# Quick Start Guide

Get up and running with Sonar Scanner Runner in minutes!

## Prerequisites Check

Make sure you have these installed:

```bash
# Check Python
python3 --version

# Check Git
git --version

# Check SonarQube Scanner
sonar-scanner --version

# Check Build Wrapper
build-wrapper-linux-x86-64 --version
```

## Installation

### 1. Configure Settings

```bash
# Option 1: Environment Variables
cp .env.example .env
nano .env

# Option 2: Config File
cp config.json.example config.json
nano config.json
```

**Minimum Required Configuration:**
```bash
SONAR_HOST_URL=http://your-sonarqube-server:9000
SONAR_TOKEN=your_sonarqube_authentication_token
```

### 2. Start the Server

**For Linux:**
```bash
./start_server.sh
```

**For WSL/Windows:**
```bash
./start_server.rb
```

**Background Mode:**
```bash
./start_server.sh 8080 --background
```

## Usage

### 1. Open Browser
Navigate to `http://localhost:8080`

### 2. Fill the Form
- **Repository URL**: `https://github.com/username/repo.git`
- **Branch**: `main`
- **Version**: `1.0.0`

### 3. Click "Start Scan"

### 4. View Results
- Watch output in real-time
- Check SonarQube dashboard when complete

## Common Commands

```bash
# Start server
./start_server.sh

# Start on custom port
./start_server.sh 9090

# Start in background
./start_server.sh 8080 --background

# Stop background server
kill $(cat server.pid)

# View logs
tail -f logs/server.log

# Clean temp files
rm -rf temp/*
```

## Troubleshooting

### Port in Use
```bash
./start_server.sh 9090
```

### Can't Find SonarQube Scanner
```bash
# Check if installed
which sonar-scanner

# Add to PATH if needed
export PATH=$PATH:/opt/sonar-scanner/bin
```

### Authentication Failed
- Check your `SONAR_TOKEN` in config.json or .env
- Verify token has proper permissions in SonarQube

### Clone Failed
- Verify repository URL
- For private repos, configure Git credentials:
```bash
git config --global credential.helper store
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check [Configuration](#configuration) section for advanced options
- Review logs in `logs/server.log` for debugging

## Quick Reference

| Action | Command |
|--------|---------|
| Start server | `./start_server.sh` |
| Custom port | `./start_server.sh 9090` |
| Background mode | `./start_server.sh 8080 -b` |
| Stop server | `Ctrl+C` or `kill $(cat server.pid)` |
| View logs | `tail -f logs/server.log` |
| Access UI | `http://localhost:8080` |

## Need Help?

1. Check the [README.md](README.md)
2. Review `logs/server.log`
3. Run with debug: `DEBUG=1 ./start_server.sh`

---

Happy scanning! 🔍
