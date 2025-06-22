#!/bin/bash
# ASL Command Center - Quick Start Script for Berkeley Cal Hacks 2025
#
# DEBUGGING NOTES:
# - Claude 3.5 previously installed conflicting llama-server versions
# - /usr/local/bin/llama-server has library issues (libmtmd.dylib)
# - /opt/homebrew/bin/llama-server works correctly
# - Always use the Homebrew version for stability
# - Future custom llama.cpp builds should go in different location
#
# MODEL NOTES:
# - Primary model: ggml-org/SmolVLM-500M-Instruct-GGUF (M2 compatible)
# - Fallback for non-Apple: HuggingFaceTB/SmolVLM-500M-Instruct
# - Actual files: SmolVLM-500M-Instruct-Q8_0.gguf + mmproj-SmolVLM-500M-Instruct-Q8_0.gguf

echo "🤟 ASL Command Center - Berkeley Cal Hacks 2025"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: Please run this script from the project directory (where index.html is located)"
    exit 1
fi

# Create directories for model storage and training data
echo "📁 Setting up directories..."
mkdir -p models/SmolVLM
mkdir -p training_data/asl_signs
mkdir -p training_data/annotations

# Kill any existing processes first (be specific about llama-server path)
echo "🧹 Cleaning up any existing processes..."
pkill -f "python.*asl_server" 2>/dev/null || true
pkill -f "python.*https-server" 2>/dev/null || true
pkill -f "python.*http.server" 2>/dev/null || true
pkill -f "node.*gun-relay" 2>/dev/null || true
pkill -f "/opt/homebrew/bin/llama-server" 2>/dev/null || true
pkill -f "/usr/local/bin/llama-server" 2>/dev/null || true  # Clean up broken installation too
sleep 2

echo "📋 Checking requirements..."

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python to run the ASL server."
    exit 1
fi

echo "✅ Python found: $PYTHON_CMD"

# Install Python dependencies for ASL system
echo "📦 Installing ASL system dependencies..."
if [ -f "requirements_asl.txt" ]; then
    $PYTHON_CMD -m pip install -r requirements_asl.txt
    echo "✅ ASL dependencies installed"
else
    echo "⚠️  requirements_asl.txt not found. Installing basic dependencies..."
    $PYTHON_CMD -m pip install flask flask-cors requests python-dotenv
fi

# Check for Node.js (needed for Gun.js relay)
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Installing Node.js for data persistence..."
    if command -v brew &> /dev/null; then
        brew install node
    else
        echo "❌ Please install Node.js manually from https://nodejs.org/"
        echo "   Gun.js data persistence will be limited without relay server"
    fi
else
    echo "✅ Node.js found"
fi

# Check for llama-server (use Homebrew version to avoid library conflicts)
LLAMA_SERVER="/opt/homebrew/bin/llama-server"
if [ ! -f "$LLAMA_SERVER" ]; then
    echo "🤖 Setting up your personal ASL AI assistant (this keeps you safe!)"
    echo "📥 Installing llama.cpp automatically..."
    echo "🔒 This protects your privacy - everything stays on your device"
    echo "⏱️  One-time setup takes 2-3 minutes, then it's instant forever"
    echo ""
    
    # Auto-install llama.cpp via Homebrew
    if command -v brew &> /dev/null; then
        echo "🍺 Installing via Homebrew..."
        brew install llama.cpp
        if [ $? -eq 0 ] && [ -f "$LLAMA_SERVER" ]; then
            echo "✅ llama.cpp installed successfully!"
            AI_SERVER=true
        else
            echo "❌ Installation failed. AI features will be disabled."
            AI_SERVER=false
        fi
    else
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        AI_SERVER=false
    fi
else
    echo "✅ llama-server found (Homebrew version)"
    # Test if llama-server works properly
    if "$LLAMA_SERVER" --help >/dev/null 2>&1; then
        AI_SERVER=true
    else
        echo "⚠️  llama-server has issues. Trying to fix..."
        if command -v brew &> /dev/null; then
            brew reinstall llama.cpp
            if [ $? -eq 0 ]; then
                echo "✅ llama-server fixed!"
                AI_SERVER=true
            else
                echo "❌ Could not fix llama-server. AI features will be disabled."
                AI_SERVER=false
            fi
        else
            echo "❌ Cannot fix llama-server without Homebrew. AI features will be disabled."
            AI_SERVER=false
        fi
    fi
fi

# Download GGUF model if not present
download_model() {
    echo "📥 Downloading SmolVLM model for ASL recognition..."
    local model_dir="models/SmolVLM"
    local model_file="$model_dir/SmolVLM-500M-Instruct-Q8_0.gguf"
    local mmproj_file="$model_dir/mmproj-SmolVLM-500M-Instruct-Q8_0.gguf"
    
    # Check if model files exist
    if [ ! -f "$model_file" ] || [ ! -f "$mmproj_file" ]; then
        echo "🔽 Model files not found locally. Downloading..."
        
        # Use huggingface-hub to download
        if command -v huggingface-cli &> /dev/null; then
            echo "📦 Using huggingface-cli to download model..."
            huggingface-cli download ggml-org/SmolVLM-500M-Instruct-GGUF SmolVLM-500M-Instruct-Q8_0.gguf --local-dir "$model_dir"
            huggingface-cli download ggml-org/SmolVLM-500M-Instruct-GGUF mmproj-SmolVLM-500M-Instruct-Q8_0.gguf --local-dir "$model_dir"
        else
            echo "📦 Installing huggingface-hub for model download..."
            $PYTHON_CMD -m pip install huggingface-hub[cli]
            if [ $? -eq 0 ]; then
                huggingface-cli download ggml-org/SmolVLM-500M-Instruct-GGUF SmolVLM-500M-Instruct-Q8_0.gguf --local-dir "$model_dir"
                huggingface-cli download ggml-org/SmolVLM-500M-Instruct-GGUF mmproj-SmolVLM-500M-Instruct-Q8_0.gguf --local-dir "$model_dir"
            else
                echo "⚠️  Could not install huggingface-hub. Model will be downloaded by llama-server on first run."
            fi
        fi
        
        if [ -f "$model_file" ] && [ -f "$mmproj_file" ]; then
            echo "✅ Model files downloaded successfully!"
            return 0
        else
            echo "⚠️  Model files not found locally. Will download on first llama-server run."
            return 1
        fi
    else
        echo "✅ Model files found locally"
        return 0
    fi
}

if [ "$AI_SERVER" = true ]; then
    download_model
fi

# Find available ports
find_available_port() {
    local start_port=$1
    local port=$start_port
    while lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; do
        port=$((port + 1))
    done
    echo $port
}

WEB_PORT=$(find_available_port 8000)
AI_PORT=$(find_available_port 8080)
GUN_PORT=$(find_available_port 8765)
ASL_PORT=$(find_available_port 5000)
HTTPS_PORT=$(find_available_port 8443)

if [ $WEB_PORT -ne 8000 ]; then
    echo "⚠️  Port 8000 is busy. Using port $WEB_PORT for web server."
fi
if [ $AI_PORT -ne 8080 ]; then
    echo "⚠️  Port 8080 is busy. Using port $AI_PORT for AI server."
fi
if [ $GUN_PORT -ne 8765 ]; then
    echo "⚠️  Port 8765 is busy. Using port $GUN_PORT for Gun.js relay."
fi
if [ $ASL_PORT -ne 5000 ]; then
    echo "⚠️  Port 5000 is busy. Using port $ASL_PORT for ASL server."
fi
if [ $HTTPS_PORT -ne 8443 ]; then
    echo "⚠️  Port 8443 is busy. Using port $HTTPS_PORT for HTTPS server."
fi

# Create temporary Gun.js relay server file
echo "const Gun = require('gun');
const server = require('http').createServer().listen($GUN_PORT);
const gun = Gun({web: server});
console.log('Gun.js relay server started on port $GUN_PORT');" > gun-relay.js

# Install Gun.js if not available
if ! npm list gun &> /dev/null; then
    echo "📦 Installing Gun.js for data persistence..."
    npm install gun --no-save &> /dev/null || {
        echo "⚠️  Gun.js installation failed. Data persistence may be limited."
    }
fi

# Start Gun.js relay server
echo "📦 Starting Gun.js relay server on port $GUN_PORT..."
node gun-relay.js > gun-relay.log 2>&1 &
GUN_PID=$!

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    
    # Kill processes by PID if available
    if [ ! -z "$WEB_PID" ] && kill -0 $WEB_PID 2>/dev/null; then
        kill $WEB_PID 2>/dev/null
        echo "   ✅ Web server stopped"
    fi
    if [ ! -z "$AI_PID" ] && kill -0 $AI_PID 2>/dev/null; then
        kill $AI_PID 2>/dev/null
        echo "   ✅ AI server stopped"
    fi
    if [ ! -z "$GUN_PID" ] && kill -0 $GUN_PID 2>/dev/null; then
        kill $GUN_PID 2>/dev/null
        echo "   ✅ Gun.js relay stopped"
    fi
    if [ ! -z "$ASL_PID" ] && kill -0 $ASL_PID 2>/dev/null; then
        kill $ASL_PID 2>/dev/null
        echo "   ✅ ASL server stopped"
    fi
    if [ ! -z "$HTTPS_PID" ] && kill -0 $HTTPS_PID 2>/dev/null; then
        kill $HTTPS_PID 2>/dev/null
        echo "   ✅ HTTPS server stopped"
    fi
    
    # Fallback: kill by process name (be specific about paths)
    pkill -f "python.*asl_server" 2>/dev/null
    pkill -f "python.*https-server" 2>/dev/null
    pkill -f "python.*http.server" 2>/dev/null
    pkill -f "/opt/homebrew/bin/llama-server" 2>/dev/null
    pkill -f "/usr/local/bin/llama-server" 2>/dev/null
    pkill -f "node.*gun-relay" 2>/dev/null
    
    # Clean up temporary files
    rm -f gun-relay.js 2>/dev/null
    
    echo "🏁 All servers stopped. Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "🌐 Starting web server on port $WEB_PORT..."

# Try to start the web server with error handling
start_web_server() {
    local attempts=0
    local max_attempts=3
    
    while [ $attempts -lt $max_attempts ]; do
        if $PYTHON_CMD -m http.server $WEB_PORT > /dev/null 2>&1 & then
            WEB_PID=$!
            sleep 2
            if kill -0 $WEB_PID 2>/dev/null; then
                echo "✅ Web server started on port $WEB_PORT"
                return 0
            fi
        fi
        
        attempts=$((attempts + 1))
        WEB_PORT=$(find_available_port $((WEB_PORT + 1)))
        echo "⚠️  Retrying with port $WEB_PORT..."
        sleep 1
    done
    
    echo "❌ Failed to start web server after $max_attempts attempts"
    return 1
}

if ! start_web_server; then
    cleanup
    exit 1
fi

if [ "$AI_SERVER" = true ]; then
    echo "🤖 Preparing AI server..."
    
    # Start the AI server with better error handling
    echo "🚀 Starting AI server on port $AI_PORT..."
    echo "⏳ This may take a moment to download/load the model..."
    
    # Check for local model files first
    LOCAL_MODEL="models/SmolVLM/SmolVLM-500M-Instruct-Q8_0.gguf"
    LOCAL_MMPROJ="models/SmolVLM/mmproj-SmolVLM-500M-Instruct-Q8_0.gguf"
    
    if [ -f "$LOCAL_MODEL" ] && [ -f "$LOCAL_MMPROJ" ]; then
        echo "   Using local model files..."
        "$LLAMA_SERVER" \
            --model "$LOCAL_MODEL" \
            --mmproj "$LOCAL_MMPROJ" \
            --port $AI_PORT \
            --host 0.0.0.0 \
            --n-gpu-layers 0 \
            --chat-template chatml \
            --log-disable > ai-server.log 2>&1 &
    else
        # Fallback to HuggingFace download
        MMPROJ_PATH="$HOME/Library/Caches/llama.cpp/ggml-org_SmolVLM-500M-Instruct-GGUF_mmproj-SmolVLM-500M-Instruct-Q8_0.gguf"
        
        if [ -f "$MMPROJ_PATH" ]; then
            echo "   Using cached mmproj file..."
            "$LLAMA_SERVER" \
                --hf-repo ggml-org/SmolVLM-500M-Instruct-GGUF \
                --hf-file SmolVLM-500M-Instruct-Q8_0.gguf \
                --mmproj "$MMPROJ_PATH" \
                --port $AI_PORT \
                --host 0.0.0.0 \
                --n-gpu-layers 0 \
                --chat-template chatml \
                --log-disable > ai-server.log 2>&1 &
        else
            echo "   Downloading mmproj file automatically..."
            "$LLAMA_SERVER" \
                --hf-repo ggml-org/SmolVLM-500M-Instruct-GGUF \
                --hf-file SmolVLM-500M-Instruct-Q8_0.gguf \
                --mmproj ggml-org/SmolVLM-500M-Instruct-GGUF/mmproj-SmolVLM-500M-Instruct-Q8_0.gguf \
                --port $AI_PORT \
                --host 0.0.0.0 \
                --n-gpu-layers 0 \
                --chat-template chatml \
                --log-disable > ai-server.log 2>&1 &
        fi
    fi
    AI_PID=$!
    
    # Wait for server to be ready with timeout
    echo "⏳ Waiting for AI server to initialize..."
    MAX_RETRIES=60
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s "http://localhost:$AI_PORT/health" >/dev/null 2>&1; then
            echo "✅ AI server ready!"
            break
        fi
        
        # Check if process is still running
        if ! kill -0 $AI_PID 2>/dev/null; then
            echo "❌ AI server process died. Check ai-server.log for details."
            echo "   Last few lines of log:"
            tail -n 5 ai-server.log 2>/dev/null || echo "   (No log file found)"
            AI_SERVER=false
            break
        fi
        
        if [ $((RETRY_COUNT % 10)) -eq 0 ]; then
            echo "   Still waiting... ($RETRY_COUNT/${MAX_RETRIES})"
        fi
        
        sleep 1
        RETRY_COUNT=$((RETRY_COUNT + 1))
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ AI server failed to start within timeout. Check ai-server.log for details."
        AI_SERVER=false
    fi
fi

# Start ASL Recognition Server
echo ""
echo "🤟 Starting ASL Recognition Server on port $ASL_PORT..."
if [ -f "asl_server.py" ]; then
    # Set environment variables for ASL server
    export LLAMA_SERVER_URL="http://localhost:$AI_PORT"
    export ASL_SERVER_PORT=$ASL_PORT
    $PYTHON_CMD asl_server.py > asl-server.log 2>&1 &
    ASL_PID=$!
    
    # Wait for ASL server to be ready
    sleep 3
    if kill -0 $ASL_PID 2>/dev/null; then
        echo "✅ ASL Recognition Server started successfully!"
    else
        echo "❌ ASL Recognition Server failed to start. Check asl-server.log for details."
        echo "   Last few lines of log:"
        tail -n 5 asl-server.log 2>/dev/null || echo "   (No log file found)"
    fi
else
    echo "❌ asl_server.py not found. ASL recognition will not be available."
    ASL_PID=""
fi

# Start HTTPS Server for camera access
echo ""
echo "🔐 Starting HTTPS Server on port $HTTPS_PORT..."
if [ -f "https-server.py" ]; then
    $PYTHON_CMD https-server.py --port $HTTPS_PORT > https-server.log 2>&1 &
    HTTPS_PID=$!
    
    # Wait for HTTPS server to be ready
    sleep 2
    if kill -0 $HTTPS_PID 2>/dev/null; then
        echo "✅ HTTPS Server started successfully!"
    else
        echo "❌ HTTPS Server failed to start. Check https-server.log for details."
        echo "   Last few lines of log:"
        tail -n 5 https-server.log 2>/dev/null || echo "   (No log file found)"
        # Fallback to HTTP server
        echo "🔄 Falling back to HTTP server..."
        $PYTHON_CMD -m http.server $WEB_PORT > web-server.log 2>&1 &
        WEB_PID=$!
        HTTPS_PORT=$WEB_PORT
    fi
else
    echo "⚠️  https-server.py not found. Starting regular HTTP server..."
    $PYTHON_CMD -m http.server $WEB_PORT > web-server.log 2>&1 &
    WEB_PID=$!
    HTTPS_PORT=$WEB_PORT
fi


echo ""
echo "🎯 ASL Command Center Ready!"
echo "============================="
echo ""
echo "🌐 Access the interface at:"
if [ "$HTTPS_PORT" -eq 8443 ] || [ "$HTTPS_PORT" -eq 443 ]; then
    echo "   📱 Primary: https://localhost:$HTTPS_PORT"
    echo "   🔒 Camera access enabled via HTTPS"
else
    echo "   📱 Primary: http://localhost:$HTTPS_PORT"
    echo "   ⚠️  Limited camera access (HTTP only)"
fi
echo ""
echo "� Available ASL Commands:"
echo "   Basic: Hello, Help, Thank you"
echo "   System: Stop, Go/Start"  
echo "   Robot: Robot pick up, Robot deliver"
echo "   Smart Home: Lights on/off (ready for integration)"
echo ""
echo "🎮 Demo Instructions:"
echo "   1. Open the URL above in your browser"
echo "   2. Grant camera permissions when prompted"
echo "   3. Click 'Start ASL Recognition'"
echo "   4. Try signing 'Hello' to test the system"
echo ""
echo "🔧 Server Status:"
echo "   🌐 Web Interface: http://localhost:$WEB_PORT (if HTTPS fails)"
if [ "$AI_SERVER" = true ]; then
    echo "   🤖 AI Server: http://localhost:$AI_PORT (SmolVLM)"
else
    echo "   🤖 AI Server: ❌ Disabled"
fi
echo "   📦 Gun.js Relay: Port $GUN_PORT"
if [ ! -z "$ASL_PID" ] && kill -0 $ASL_PID 2>/dev/null; then
    echo "   🤟 ASL Server: http://localhost:$ASL_PORT"
else
    echo "   🤟 ASL Server: ❌ Not running"
fi
echo ""
echo "📁 Training Data will be saved to:"
echo "   📸 Images: ./training_data/asl_signs/"
echo "   📝 Annotations: ./training_data/annotations/"
echo ""
echo "📋 Troubleshooting:"
echo "   • Check *-server.log files if services aren't working"
echo "   • Use Chrome/Safari for best camera support"
echo "   • Make sure you're on localhost or HTTPS for camera access"
echo ""
echo "🏆 Berkeley Cal Hacks 2025 - Ready for Demo!"
echo ""
echo "🛑 Press Ctrl+C to stop all servers"
echo ""

# Wait for background processes
wait
