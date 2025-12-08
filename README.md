# 🔍 Sonar Scanner Runner

A web-based application for running SonarQube Scanner with automated build wrapper integration. This tool provides a simple and intuitive interface to trigger code quality analysis on Git repositories.

## ✨ Features

- **Simple Web Interface**: Clean, modern UI for entering repository details
- **Automated Build Detection**: Automatically detects build system (Maven, Gradle, Make, CMake, npm, etc.)
- **Build Wrapper Integration**: Seamlessly integrates with SonarQube Build Wrapper for C/C++ projects
- **Real-time Output**: View scan progress and output in real-time
- **Background Processing**: Server runs continuously, handling multiple scan requests
- **Cross-platform Support**: Python backend with Ruby launcher for Windows/WSL compatibility
- **Standard Library Only**: Python backend uses only standard libraries for maximum compatibility

## 📋 Prerequisites

Before using this application, ensure you have the following installed:

### Required
- **Python 3.6+**: For running the backend server
- **Git**: For cloning repositories
- **SonarQube Scanner**: Command-line scanner for SonarQube
- **Build Wrapper**: SonarQube build wrapper (for C/C++ projects)

### Optional
- **Ruby 2.5+**: For using the Ruby launcher script (recommended for WSL/Windows users)

### Installation of Prerequisites

#### SonarQube Scanner
```bash
# Download and install SonarQube Scanner
# Visit: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/

# For Linux
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
unzip sonar-scanner-cli-4.8.0.2856-linux.zip
sudo mv sonar-scanner-4.8.0.2856-linux /opt/sonar-scanner
sudo ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
```

#### Build Wrapper
```bash
# Download from your SonarQube instance
# Usually available at: http://your-sonarqube-url/static/cpp/build-wrapper-linux-x86.zip

# Or download directly
wget https://sonarqube.example.com/static/cpp/build-wrapper-linux-x86.zip
unzip build-wrapper-linux-x86.zip
sudo mv build-wrapper-linux-x86 /opt/build-wrapper
sudo ln -s /opt/build-wrapper/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux-x86-64
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd sonar_scanner_runner
```

### 2. Configure the Application

#### Option A: Using Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

#### Option B: Using Configuration File
```bash
cp config.json.example config.json
# Edit config.json with your settings
nano config.json
```

**Important Configuration Values:**
- `SONAR_HOST_URL`: Your SonarQube server URL (default: http://localhost:9000)
- `SONAR_TOKEN`: Your SonarQube authentication token
- `SERVER_PORT`: Port for the web server (default: 8080)

### 3. Start the Server

#### Method 1: Using Shell Script (Recommended for Linux)
```bash
# Start in foreground
./start_server.sh

# Start in background
./start_server.sh 8080 --background

# Start on custom port
./start_server.sh 9090
```

#### Method 2: Using Ruby Script (Recommended for WSL/Windows)
```bash
# Start on default port (8080)
./start_server.rb

# Start on custom port
./start_server.rb 9090
```

#### Method 3: Direct Python Execution
```bash
cd backend
python3 server.py 8080
```

### 4. Access the Application

Open your web browser and navigate to:
```
http://localhost:8080
```

If using WSL, the Ruby launcher will automatically attempt to open the browser in Windows.

## 📖 Usage Guide

### Running a Scan

1. **Open the Web Interface**: Navigate to `http://localhost:8080` in your browser

2. **Fill in the Scan Configuration**:
   - **Repository URL**: Full Git repository URL (HTTPS or SSH)
     - Example: `https://github.com/username/project.git`
     - Example: `git@github.com:username/project.git`

   - **Branch Name**: The branch you want to analyze
     - Example: `main`, `develop`, `feature/new-feature`

   - **Release Version**: Version number for this analysis
     - Example: `1.0.0`, `v2.3.1`, `2024.01.15`

3. **Submit the Scan**: Click the "Start Scan" button

4. **View Results**: The output box will display real-time progress and results

### Interpreting Results

The scan process includes these steps:
1. **Prerequisites Check**: Verifies Git, SonarQube Scanner, and Build Wrapper are available
2. **Repository Clone**: Clones the specified repository and branch
3. **Build System Detection**: Automatically detects the project's build system
4. **Build Wrapper Execution**: Runs the build with build wrapper (if applicable)
5. **SonarQube Scan**: Executes the SonarQube Scanner
6. **Cleanup**: Removes temporary files

After completion, check your SonarQube dashboard for detailed analysis results.

## 🏗️ Project Structure

```
sonar_scanner_runner/
├── backend/
│   ├── server.py              # Main HTTP server
│   └── scripts/
│       └── run_sonar_scan.py  # Scan execution logic
├── frontend/
│   ├── index.html             # Web interface
│   └── static/
│       ├── css/
│       │   └── styles.css     # UI styling
│       └── js/
│           └── app.js         # Frontend logic
├── logs/                      # Server and scan logs
├── temp/                      # Temporary workspace for clones
├── config.json.example        # Configuration template
├── .env.example              # Environment variables template
├── start_server.sh           # Shell launcher script
├── start_server.rb           # Ruby launcher script
└── README.md                 # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SONAR_HOST_URL` | SonarQube server URL | `http://localhost:9000` |
| `SONAR_TOKEN` | SonarQube authentication token | - |
| `SERVER_PORT` | Web server port | `8080` |
| `SERVER_HOST` | Web server host | `0.0.0.0` |
| `WORKSPACE_DIR` | Temporary workspace directory | `./temp` |
| `BUILD_WRAPPER_CMD` | Build wrapper command | `build-wrapper-linux-x86-64` |
| `SONAR_SCANNER_CMD` | Sonar scanner command | `sonar-scanner` |

### Configuration File (config.json)

```json
{
  "sonar_host_url": "http://localhost:9000",
  "sonar_token": "your_token_here",
  "workspace_dir": "./temp",
  "build_wrapper_cmd": "build-wrapper-linux-x86-64",
  "sonar_scanner_cmd": "sonar-scanner",
  "server": {
    "host": "0.0.0.0",
    "port": 8080
  }
}
```

## 🔧 Advanced Usage

### Running Multiple Instances

To run multiple instances of the server on different ports:

```bash
# Instance 1 on port 8080
./start_server.sh 8080 --background

# Instance 2 on port 8081
./start_server.sh 8081 --background
```

### Custom Build Commands

The scanner automatically detects build systems, but you can customize the build process by modifying `backend/scripts/run_sonar_scan.py`.

### Logging

Logs are stored in the `logs/` directory:
- `logs/server.log`: Server access and error logs
- `logs/server.out`: Background server output (when using --background)

View logs in real-time:
```bash
tail -f logs/server.log
```

### Stopping the Server

If running in foreground:
- Press `Ctrl+C`

If running in background:
```bash
# Using PID from output
kill <PID>

# Or using saved PID file
kill $(cat server.pid)
```

## 🐛 Troubleshooting

### Port Already in Use
```
Error: Port 8080 is already in use
```
**Solution**: Use a different port or stop the existing service
```bash
./start_server.sh 9090
```

### SonarQube Scanner Not Found
```
Error: SonarQube Scanner NOT found
```
**Solution**: Install SonarQube Scanner and ensure it's in your PATH
```bash
which sonar-scanner
```

### Build Wrapper Not Found
```
Error: Build Wrapper NOT found
```
**Solution**: Install Build Wrapper and ensure it's in your PATH
```bash
which build-wrapper-linux-x86-64
```

### Authentication Error
```
Error: Unauthorized (401)
```
**Solution**: Check your SonarQube token in config.json or .env

### Repository Clone Failed
```
Error: Failed to clone repository
```
**Solutions**:
- Verify the repository URL is correct
- Ensure you have access to the repository
- For private repos, configure Git credentials or use SSH keys

## 🔐 Security Considerations

- **Token Security**: Keep your SonarQube token secure. Don't commit it to version control
- **Network Access**: The server binds to `0.0.0.0` by default. Consider using a firewall or changing to `127.0.0.1` for local-only access
- **Repository Access**: Ensure proper authentication is configured for private repositories
- **Cleanup**: Temporary files are automatically cleaned up after scans

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- WebSocket support for real-time output streaming
- Support for additional build systems
- Docker containerization
- Authentication for the web interface
- Scan history and reporting
- Parallel scan execution

## 📝 License

This project is provided as-is for internal use.

## 🆘 Support

For issues, questions, or suggestions:
1. Check the troubleshooting section
2. Review the logs in `logs/server.log`
3. Enable debug mode: `DEBUG=1 ./start_server.sh`

## 🔄 Updates and Maintenance

### Updating SonarQube Scanner
```bash
# Download latest version
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-latest-linux.zip
# Extract and replace existing installation
```

### Cleaning Up Old Scans
```bash
# Clean temporary files
rm -rf temp/*

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

## 📊 Supported Build Systems

The scanner automatically detects and supports:
- **Maven** (pom.xml)
- **Gradle** (build.gradle, build.gradle.kts)
- **CMake** (CMakeLists.txt)
- **Make** (Makefile)
- **npm** (package.json)
- **Python** (setup.py)

## 🎯 Roadmap

- [ ] WebSocket integration for real-time output
- [ ] User authentication and authorization
- [ ] Scan queue management
- [ ] Email notifications on scan completion
- [ ] Integration with CI/CD pipelines
- [ ] Docker support
- [ ] Scan history dashboard
- [ ] Multi-repository batch scanning

---

**Version**: 1.0.0
**Last Updated**: 2024
