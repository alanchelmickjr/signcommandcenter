#!/bin/bash
# Start ASL Recognition System for Berkeley Cal Hacks 2025

echo "🤟 Starting ASL Command Center..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements_asl.txt

# Start Gun.js relay server in background
echo "🔗 Starting Gun.js relay server..."
node gun-relay.js &
GUNJS_PID=$!

# Start ASL recognition server
echo "🧠 Starting ASL recognition server..."
python3 asl_server.py &
ASL_PID=$!

# Start HTTPS server for camera access
echo "📹 Starting HTTPS server..."
python3 https-server.py &
HTTPS_PID=$!

echo ""
echo "✅ ASL Command Center is running!"
echo ""
echo "📱 Open: https://localhost:8443"
echo "🤟 Available ASL commands:"
echo "   - Hello"
echo "   - Help" 
echo "   - Robot pick up"
echo "   - Robot deliver"
echo "   - Stop/Go"
echo ""
echo "🎯 Ready for Berkeley Cal Hacks 2025 demo!"
echo ""
echo "Press Ctrl+C to stop all services..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping ASL Command Center..."
    kill $GUNJS_PID 2>/dev/null
    kill $ASL_PID 2>/dev/null  
    kill $HTTPS_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for all services
wait
