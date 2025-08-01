#!/bin/bash

# Enhanced Knowledge Base Generation Script with Agent Debate
# This script runs the enhanced generation system in the background

echo "=== Enhanced Knowledge Base Generation System ==="
echo "Starting background generation with agent debate system..."
echo ""

# Function to show running status
show_status() {
    echo "Checking running processes..."
    pgrep -f "enhanced_cli.py" | while read pid; do
        echo "Process $pid is running: $(ps -p $pid -o cmd --no-headers)"
    done
    
    if [ ! -f generation_windows.log ]; then
        echo "No active generation processes found."
    else
        echo "Log files found:"
        ls -la *.log 2>/dev/null || echo "No log files yet"
    fi
}

# Function to start Windows generation
start_windows() {
    echo "Starting Windows generation with agent debate..."
    nohup python3 enhanced_cli.py --generate --platform windows --use-debate --include-code --verbose > generation_windows.log 2>&1 &
    echo "Windows generation started (PID: $!)"
    echo "Monitor with: tail -f generation_windows.log"
}

# Function to start Linux generation  
start_linux() {
    echo "Starting Linux generation with agent debate..."
    nohup python3 enhanced_cli.py --generate --platform linux --use-debate --include-code --verbose > generation_linux.log 2>&1 &
    echo "Linux generation started (PID: $!)"
    echo "Monitor with: tail -f generation_linux.log"
}

# Function to start all platforms sequentially
start_all() {
    echo "Starting generation for all platforms sequentially..."
    nohup bash -c '
        echo "Starting Windows..." >> all_platforms.log 2>&1
        python3 enhanced_cli.py --generate --platform windows --use-debate --include-code --verbose >> all_platforms.log 2>&1
        echo "Windows complete, starting Linux..." >> all_platforms.log 2>&1  
        python3 enhanced_cli.py --generate --platform linux --use-debate --include-code --verbose >> all_platforms.log 2>&1
        echo "All platforms complete!" >> all_platforms.log 2>&1
    ' > /dev/null 2>&1 &
    echo "All platforms generation started (PID: $!)"
    echo "Monitor with: tail -f all_platforms.log"
}

# Function to stop all generation processes
stop_all() {
    echo "Stopping all generation processes..."
    pkill -f "enhanced_cli.py"
    echo "All processes stopped."
}

# Main menu
case "${1:-menu}" in
    "windows")
        start_windows
        ;;
    "linux") 
        start_linux
        ;;
    "all")
        start_all
        ;;
    "status")
        show_status
        ;;
    "stop")
        stop_all
        ;;
    "menu"|*)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  windows  - Start Windows generation in background"
        echo "  linux    - Start Linux generation in background" 
        echo "  all      - Start all platforms sequentially in background"
        echo "  status   - Check running processes and logs"
        echo "  stop     - Stop all generation processes"
        echo ""
        echo "Examples:"
        echo "  ./run.sh windows     # Start Windows generation"
        echo "  ./run.sh all         # Start all platforms"
        echo "  ./run.sh status      # Check what's running"
        echo "  ./run.sh stop        # Stop everything"
        echo ""
        echo "Monitor logs:"
        echo "  tail -f generation_windows.log"
        echo "  tail -f generation_linux.log"
        echo "  tail -f all_platforms.log"
        ;;
esac