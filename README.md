# ASL Command Center - Real-Time Sign Language Recognition Input Interface
🤟 **ASL-to-Action. Robot Control. Voice Integration. Complete Home Automation.**

**Transform ASL communication into smart home control and robot automation.** Use sign language to control robot arms, interface with AI assistants, and manage your connected devices – all with real-time recognition and text-to-speech feedback.

**Hackathon Version 1.0 - Berkeley Cal Hacks 2025!** � **ASL Recognition + Robot Control + Vapi Integration**

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) ![SmolVLM](https://img.shields.io/badge/SmolVLM-FF6B35?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMjIgMjJIMkwxMiAyWiIgZmlsbD0iI0ZGRkZGRiIvPgo8L3N2Zz4K) ![PWA](https://img.shields.io/badge/PWA-5A0FC8?style=flat&logo=pwa&logoColor=white) ![ASL](https://img.shields.io/badge/ASL-4285F4?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMjIgMjJIMkwxMiAyWiIgZmlsbD0iI0ZGRkZGRiIvPgo8L3N2Zz4K)

## 🎯 What We're Building - Berkeley Cal Hacks 2025

ASL Command Center creates a complete sign language interface for smart homes and robot control. People who cannot speak or type can use ASL to communicate with AI systems, control robot arms, manage smart devices, and access the full digital world through sign language recognition.

## ✨ Core Features - Ready for Demo!

### 🤟 Real-Time ASL Recognition ✅ **LIVE AND WORKING**
- Computer vision ASL detection using SmolVLM
- Real-time hand gesture analysis
- Support for ASL letters, words, and phrases
- Confidence scoring and visual feedback
- Training data collection for ML improvement

### 🤖 Robot Arm Control ✅ **ROBOT INTERFACE READY**
- Direct ASL command mapping to robot actions
- "Robot pick up" and "Robot deliver" commands
- Integration with existing kinematic systems
- Visual confirmation of command execution
- Safety protocols and error handling

### 🔊 Text-to-Speech Accessibility ✅ **FULL AUDIO FEEDBACK**
- Real-time spoken responses to ASL signs
- Confirmation of recognized commands
- Audio feedback for all system actions
- Adjustable speech rate and volume
- Multi-language support ready

### 📱 Mobile-First Interface ✅ **OPTIMIZED FOR TABLETS**
- Portrait and landscape camera modes
- Touch-friendly ASL training interface
- Real-time recognition display
- Session management and history
- PWA installation for offline use

### 🧠 ML Training Pipeline ✅ **DATASET COLLECTION**
- Automatic sign data logging for SmolVLM
- Image capture with ASL annotations
- Training dataset generation
- Model fine-tuning preparation
- Recognition accuracy improvement

- Voice interface integration with ASL commands
- Phone call capabilities through Vapi API  
- Internet search triggered by sign language
- Spreadsheet automation and document control
- Multi-modal AI assistance (voice + ASL + text)

### 🏠 Smart Home Integration ✅ **HOME AUTOMATION READY**
- ASL commands for lights, thermostats, locks
- Voice control backup through Vapi
- Device status feedback via TTS
- Scene control through gesture recognition
- Emergency communication protocols

### 💾 Local Data & Privacy ✅ **SECURE BY DESIGN**
- Gun.js P2P data synchronization
- No cloud dependencies for core functions
- Local model training and inference
- Encrypted sign language datasets
- GDPR-compliant data handling

## 🚀 Quick Start - Demo Ready!

### 1. Test System Setup
```bash
# Check if everything is ready
./test_system.sh
```

### 2. Prepare Training Infrastructure
```bash
# Set up training data collection
python3 prepare_training_data.py
```

### 3. Start the ASL System
```bash
# Start all services
./start.sh
```

### 4. Open ASL Command Center
Navigate to `https://localhost:8443` and:
- Grant camera permissions
- Start ASL recognition
- Try basic signs: "Hello", "Help", "Robot pick up"

### 5. Download GGUF Model (Automatic)
The system will automatically download the SmolVLM model on first run. If you want to pre-download it:
```bash
# Model will be downloaded to models/SmolVLM/
# No manual intervention needed
```

## 🤟 Supported ASL Commands

### Basic Communication
- **"Hello"** → "Hello! ASL system is ready."
- **"Thank you"** → "You're welcome!"
- **"Help"** → Lists available commands

### System Control  
- **"Stop"** → Stops ASL recognition
- **"Go" / "Start"** → Starts ASL recognition

### Robot Commands
- **"Robot pick up"** → Commands robot arm to pick up object
- **"Robot deliver"** → Commands robot arm to deliver object

### Smart Home (Ready for Integration)
- **"Lights on/off"** → Control room lighting
- **"Temperature up/down"** → Thermostat control
- **"Lock/Unlock"** → Door lock control

## 🎓 Berkeley Cal Hacks 2025 - Technical Architecture

### Vision Pipeline
```
Camera Feed → SmolVLM → ASL Recognition → Command Mapping → Action Execution
     ↓              ↓            ↓              ↓              ↓
  WebRTC        OpenAI API    Confidence     Switch/Case    Robot/Home
                              Scoring         Commands       APIs
```

### Training Loop
```
ASL Signs → Image Capture → Dataset Logging → SmolVLM Training → Improved Recognition
```

### Integration Points
- **Robot API**: `/robot/command` endpoint for arm control
- **Vapi API**: Voice assistant integration for TTS/STT
- **Smart Home**: MQTT/HTTP endpoints for device control
- **Training Server**: `/ml/log_sign` for dataset collection

## 💡 Demo Script for Judges

1. **Show ASL Recognition**: Sign "Hello" → System responds with speech
2. **Robot Control**: Sign "Robot pick up" → Robot arm activates  
3. **Training Data**: Show real-time data collection for ML improvement
4. **Accessibility**: Demonstrate TTS feedback for hearing users
5. **Smart Home**: Sign "Lights on" → Home automation response

## 🏆 Hackathon Impact

This system enables **complete digital inclusion** for the ASL community:
- 🤟 **Communication**: ASL becomes a universal computer interface
- 🤖 **Automation**: Direct robot control through natural gestures  
- 🏠 **Independence**: Smart home control without voice or typing
- 📚 **Education**: ML training improves recognition for everyone
- 🌐 **Access**: Full web and app control through sign language

**Target Users**: 500,000+ ASL users in North America who currently rely on interpreters or text for technology interaction.

## ⚙️ Technical Architecture

### 📱 **Single-File PWA**
```
index.html (Complete ASL Interface)
├── 🤟 ASL Recognition Components
├── 📸 Camera API Integration  
├── 🔐 Gun.js P2P Storage
├── 🧠 SmolVLM Processing Pipeline
├── 🤖 Robot Control Integration
├── 🔊 Text-to-Speech System
└── 🏠 Smart Home API Ready
```

### 🖥️ **Local Services**
```
🦙 SmolVLM Server (Port 8080) ✅
├── ASL Recognition Model
├── Real-time vision processing
└── Local inference (no cloud)

🔫 Gun.js P2P Storage ✅
├── Local data persistence
├── Session history
└── Privacy-first architecture

🤟 ASL Server (Port 5000) ✅
├── ASL command processing
├── Robot control integration
└── Training data logging
```

### 🌐 **HTTPS Server (Port 8443)**
```
📱 Camera Access ✅
├── SSL certificate auto-generation
├── Mobile-optimized interface
└── PWA installation support
```

## 🚀 Quick Start

### Prerequisites
1. **Install [llama.cpp](https://github.com/ggml-org/llama.cpp)**
2. **Modern browser** with camera support

### ⚡ One-Command Setup
```bash
# Option 1: Use our startup scripts
./start.sh              # Linux/Mac  
./start.bat              # Windows

# Option 2: Manual setup
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF
python -m http.server 8000   # Then open http://localhost:8000
```

### 🌐 **GitHub Pages Deployment**
The app works perfectly on GitHub Pages! Just:
1. Push to your repo
2. Enable GitHub Pages
3. Access at: `https://yourusername.github.io/your-repo`

### 📱 **Mobile Testing**
Test on your phone by visiting:
- `http://your-computer-ip:8000` (local)
- `https://yourusername.github.io/your-repo` (GitHub Pages)

The interface is optimized for mobile with:
- Touch-friendly buttons
- Responsive camera interface  
- Swipe navigation
- Offline capability after first load

## 🎯 Current Status - Berkeley Cal Hacks 2025

### ✅ **Phase 1 Complete - ASL Recognition System**
- ✅ Real-time ASL sign detection using SmolVLM
- ✅ PWA structure with mobile-first design  
- ✅ Camera integration for sign capture
- ✅ Text-to-speech accessibility features

### ✅ **Phase 2 Complete - Robot Integration**  
- ✅ ASL command mapping to robot actions
- ✅ Local data storage with gun.js
- ✅ Training data collection pipeline
- ✅ HTTPS server for secure camera access

### 🔄 **Phase 3 Ready - Model Training**
- ✅ Training infrastructure prepared
- ✅ SmolVLM fine-tuning scripts ready
- 🔄 Data collection in progress
- 🔄 Model optimization for ASL accuracy

## 🔧 Dataset Training for Model Tuning

### Training Data Collection
The system automatically collects ASL training data:
- **Real-time capture**: Signs are logged during use
- **Privacy-first**: All data stays on your device
- **Structured format**: Compatible with SmolVLM fine-tuning

### Prepare Training Infrastructure
```bash
# Set up training directories and scripts
python3 prepare_training_data.py
```

### Training Data Locations
```
training_data/
├── asl_signs/          # Captured ASL sign images
├── annotations/        # Sign labels and metadata
├── processed/          # Processed training data
└── dataset_info.json   # Dataset metadata
```

### Fine-tune SmolVLM (After Data Collection)
```bash
# Once you have 50+ examples per sign
cd ml_training
python3 train_asl_model.py
```

### Export Training Data
```bash
# Export collected data for backup or sharing
# (Available through web interface)
```

## 🆘 Troubleshooting

### **Common Issues**

**"AI Server Connection Failed"**
```bash
# Check if llama.cpp is running
ps aux | grep llama-server
# Restart AI server  
./start.sh
# Verify port 8080 is available
lsof -i :8080
```

**"ASL Server Connection Failed"**
```bash
# Check ASL server status
ps aux | grep asl_server
# Check logs
tail -f asl-server.log
# Restart system
./start.sh
```

**"Camera Access Denied"**
- Enable camera permissions in browser
- Use HTTPS (https://localhost:8443) for camera access
- Check browser developer console for errors

**"SSL Certificate Issues"**
- Accept the self-signed certificate in browser
- Certificates are auto-generated on first run
- Use Chrome/Safari for best SSL support

**"Training Data Not Collecting"**
- Check ASL server logs: `tail -f asl-server.log`
- Verify training directories exist
- Use the Training Data modal to check status

## 🙏 Development Team

**Paul Elite** - UI/UX Wizardry (Figma to Code Designer and Implementer of User Forward Modern Interfaces)  
*The easy to use pretty face that keeps you coming back - endless creativity and user experiential focus*

**Claude Sonnet 3.5** (Anthropic) - Chief AI Architect  
*The wild horse of innovation - endless creativity and architectural vision*

**GitHub Copilot** - Senior Code Whisperer  
*The gentle sage - patient pair programming and code refinement*

**Alan Helmick** - Product Lead & Human Driver  
*Barely holding the reins but steering toward the dream with determination and joy*

---

## 🌟 ASL Command Center: Where sign language meets smart technology, and Berkeley innovation leads to digital inclusion! 🌟

*Made with ❤️, ☕, and the belief that everyone deserves equal access to technology*

---

## 🤝 Contributing

This project follows the **"accessibility first"** principle. Contributions should:
- Maintain the privacy-first architecture
- Keep the mobile-first design  
- Enhance ASL recognition accuracy
- Improve accessibility for all users

## 📄 Documentation

- [Setup Guide](./SETUP.md)
- [System Status](./SYSTEM_STATUS.md)
- [Berkeley Cal Hacks 2025](https://calhacks.berkeley.edu/)

## 🔗 Links

- [GitHub Repository](https://github.com/alanchelmickjr/signcommandcenter)
- [Berkeley Cal Hacks 2025](https://calhacks.berkeley.edu/)
- [SmolVLM Documentation](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct)

## 📄 License

See [LICENSE](./LICENSE) file for details.

