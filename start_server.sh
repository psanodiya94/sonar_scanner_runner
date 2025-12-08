#!/bin/bash

#
# Sonar Scanner Runner - Simple Shell Launcher
# Quick start script for the Python backend server
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PORT="${1:-8080}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/backend/server.py"

# Print header
echo "============================================================"
echo "  Sonar Scanner Runner - Server Launcher"
echo "============================================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "  Please install Python 3 to continue"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

if [ ! -f "$SERVER_SCRIPT" ]; then
    echo -e "${RED}✗ Server script not found: $SERVER_SCRIPT${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Server script found${NC}"

echo ""

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}✗ Port $PORT is already in use${NC}"
    echo "  Please stop the existing service or use a different port:"
    echo "  $0 <port_number>"
    exit 1
fi
echo -e "${GREEN}✓ Port $PORT is available${NC}"

echo ""

# Create necessary directories
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/temp"

# Start server
echo "Starting server on port $PORT..."
echo ""

cd "$SCRIPT_DIR"

# Check if we should run in background
if [ "$2" == "--background" ] || [ "$2" == "-b" ]; then
    # Run in background
    nohup python3 "$SERVER_SCRIPT" "$PORT" > "$SCRIPT_DIR/logs/server.out" 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > "$SCRIPT_DIR/server.pid"

    echo -e "${GREEN}✓ Server started in background with PID: $SERVER_PID${NC}"
    echo ""
    echo "Server is running at: http://localhost:$PORT"
    echo ""
    echo "To stop the server, run:"
    echo "  kill $SERVER_PID"
    echo "  or: kill \$(cat $SCRIPT_DIR/server.pid)"
    echo ""
    echo "To view logs, run:"
    echo "  tail -f $SCRIPT_DIR/logs/server.out"
    echo ""
else
    # Run in foreground
    echo "Server is starting..."
    echo "Access the web interface at: http://localhost:$PORT"
    echo "Press Ctrl+C to stop the server"
    echo ""
    echo "============================================================"
    echo ""

    # Trap Ctrl+C to clean up
    trap 'echo ""; echo "Shutting down server..."; exit 0' INT TERM

    python3 "$SERVER_SCRIPT" "$PORT"
fi
