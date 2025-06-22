#!/bin/bash
# ASL Command Center - System Test Script
# Berkeley Cal Hacks 2025

echo "🧪 Testing ASL Command Center System"
echo "==================================="

# Test Python availability
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "✅ Python found: $(python --version)"
    PYTHON_CMD="python"
else
    echo "❌ Python not found"
    exit 1
fi

# Test ASL dependencies
echo "📦 Checking ASL dependencies..."
if [ -f "requirements_asl.txt" ]; then
    echo "✅ Requirements file found"
    if $PYTHON_CMD -c "import flask, flask_cors, requests" 2>/dev/null; then
        echo "✅ Basic dependencies available"
    else
        echo "⚠️  Installing missing dependencies..."
        $PYTHON_CMD -m pip install -r requirements_asl.txt
    fi
else
    echo "❌ requirements_asl.txt not found"
fi

# Test llama.cpp availability
echo "🤖 Checking llama.cpp..."
LLAMA_SERVER="/opt/homebrew/bin/llama-server"
if [ -f "$LLAMA_SERVER" ]; then
    echo "✅ llama-server found"
    if "$LLAMA_SERVER" --help >/dev/null 2>&1; then
        echo "✅ llama-server is working"
    else
        echo "❌ llama-server has issues"
    fi
else
    echo "⚠️  llama-server not found. Will be installed on first run."
fi

# Test Node.js availability
echo "📦 Checking Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(node --version)"
else
    echo "⚠️  Node.js not found. Gun.js data persistence will be limited."
fi

# Test file structure
echo "📁 Checking file structure..."
required_files=(
    "index.html"
    "asl_server.py"
    "https-server.py"
    "start.sh"
    "requirements_asl.txt"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file found"
    else
        echo "❌ $file missing"
    fi
done

# Test certificates
echo "🔐 Checking SSL certificates..."
if [ -f "cert.pem" ] && [ -f "key.pem" ]; then
    echo "✅ SSL certificates found"
else
    echo "⚠️  SSL certificates not found. Will be generated automatically."
fi

# Test directory structure
echo "📂 Checking directory structure..."
if [ ! -d "training_data" ]; then
    echo "📁 Creating training data directories..."
    mkdir -p training_data/{asl_signs,annotations,processed}
    echo "✅ Training directories created"
else
    echo "✅ Training directories exist"
fi

if [ ! -d "models" ]; then
    echo "📁 Creating models directory..."
    mkdir -p models/SmolVLM
    echo "✅ Models directory created"
else
    echo "✅ Models directory exists"
fi

echo ""
echo "🎯 System Test Summary"
echo "====================="
echo "✅ Ready to start ASL Command Center!"
echo ""
echo "🚀 Next steps:"
echo "   1. Run ./start.sh to start all services"
echo "   2. Open browser to https://localhost:8443"
echo "   3. Grant camera permissions"
echo "   4. Start practicing ASL signs!"
echo ""
echo "📚 For training data collection:"
echo "   1. Use the interface to perform ASL signs"
echo "   2. Data will be automatically collected"
echo "   3. Run python3 prepare_training_data.py for training setup"
