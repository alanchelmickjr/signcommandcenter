// Main JavaScript for ASL Command Center
// Initialize Gun.js with dynamic relay server
const gun = Gun({
    peers: [window.ASL_CONFIG?.GUN_RELAY_URL || 'http://localhost:8765/gun']
});
const aslData = gun.get('asl-training-data');

// Vapi Configuration for Agent Ava
const VAPI_CONFIG = {
    apiKey: localStorage.getItem('vapi_api_key') || 'your-vapi-api-key',
    assistantId: localStorage.getItem('vapi_assistant_id') || 'your-assistant-id',
    baseUrl: 'https://api.vapi.ai'
};

const video = document.getElementById('videoFeed');
const canvas = document.getElementById('canvas');
const baseURL = document.getElementById('baseURL');
const intervalSelect = document.getElementById('intervalSelect');
const startButton = document.getElementById('startButton');
const itemsList = document.getElementById('itemsList');
const historySection = document.getElementById('historySection');
const historyList = document.getElementById('historyList');
const toggleHistoryBtn = document.getElementById('toggleHistoryBtn');
const videoOverlay = document.getElementById('videoOverlay');
const overlayText = document.getElementById('overlayText');

// Training data elements
const trainingModal = document.getElementById('trainingModal');
const trainingBtn = document.getElementById('trainingBtn');
const trainingCloseBtn = document.getElementById('trainingCloseBtn');
const exportDataBtn = document.getElementById('exportDataBtn');
const clearDataBtn = document.getElementById('clearDataBtn');
const collectedCount = document.getElementById('collectedCount');
const currentAccuracy = document.getElementById('currentAccuracy');

let stream;
let intervalId;
let isProcessing = false;
let aslServerAvailable = false;

// Dynamic server URLs based on configuration
const AI_SERVER_URL = window.ASL_CONFIG?.AI_SERVER_URL || 'http://localhost:8080';
const ASL_SERVER_URL = window.ASL_CONFIG?.ASL_SERVER_URL || 'http://localhost:5001';

console.log('Using dynamic server URLs:', { AI_SERVER_URL, ASL_SERVER_URL });

// ASL recognition instruction for SmolVLM
const ASL_RECOGNITION_INSTRUCTION = `Look at this image and identify any American Sign Language (ASL) gestures being performed.

Analyze the hand positions, finger configurations, and hand movements visible in the image. If you can recognize any ASL letters, words, or phrases, respond with this exact format:

RECOGNIZED_ASL: [word or phrase]
CONFIDENCE: [High/Medium/Low]
DESCRIPTION: [brief description of the hand gesture]

Common ASL signs to look for:
- Hello (open hand wave)
- Thank you (fingers to chin, then forward)
- Help (fist on opposite palm, lift together)
- Stop (flat hand raised)
- Go/Start (pointing forward)
- Robot pick up (grasping motion)
- Robot deliver (placing motion)

If no clear ASL gesture is visible, respond with "RECOGNIZED_ASL: none"`;

// ASL server endpoints - now dynamically configured

// Function to send ASL data to server for processing
async function sendToAslServer(imageData, recognizedText) {
    if (!aslServerAvailable) {
        console.log('ASL server not available');
        return null;
    }
    
    try {
        const response = await fetch(`${ASL_SERVER_URL}/process_asl`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: imageData,
                recognized_text: recognizedText,
                timestamp: Date.now()
            })
        });
        
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('ASL server error:', error);
    }
    return null;
}

// Text-to-speech for accessibility
function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1.0;
        speechSynthesis.speak(utterance);
    }
}

// Check ASL server availability
async function checkAslServer() {
    try {
        const response = await fetch(`${ASL_SERVER_URL}/health`);
        aslServerAvailable = response.ok;
        return aslServerAvailable;
    } catch {
        aslServerAvailable = false;
        return false;
    }
}

// Vapi Agent Ava Integration Functions
async function callVapiAgent(message, isPhoneCall = false) {
    try {
        const response = await fetch(`${VAPI_CONFIG.baseUrl}/assistant/call`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${VAPI_CONFIG.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                assistantId: VAPI_CONFIG.assistantId,
                message: message,
                phoneCall: isPhoneCall,
                customerDetails: {
                    name: 'ASL User',
                    language: 'en',
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Vapi API error: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.warn('Vapi call failed:', error);
        // Fallback response for demo
        return {
            response: `Agent Ava would respond to: "${message}"`,
            callId: 'demo-' + Date.now(),
            isMockData: true
        };
    }
}

async function startVapiPhoneCall(phoneNumber = null) {
    try {
        speakText("Starting phone call with Agent Ava");
        
        const callData = await callVapiAgent("User initiated phone call via ASL command", true);
        
        showNotification(`Phone call started: ${callData.callId}`, 'success', 5000);
        return callData;
    } catch (error) {
        console.error('Phone call failed:', error);
        speakText("Unable to start phone call. Please try again.");
        showNotification('Phone call failed', 'error', 3000);
    }
}

async function chatWithVapi(message) {
    try {
        const response = await callVapiAgent(message, false);
        
        // Display chat response
        if (response.response) {
            speakText(response.response);
            showNotification(`Ava: ${response.response}`, 'info', 5000);
        }
        
        return response;
    } catch (error) {
        console.error('Vapi chat failed:', error);
        speakText("Unable to connect to Agent Ava. Please try again.");
    }
}

// Save identified items to local storage
function saveItemsLocally(items) {
    // Store individual items in current session
    items.forEach((item, index) => {
        const itemData = {
            ...item,
            sessionId: currentSessionId,
            itemIndex: index,
            timestamp: Date.now()
        };
        gun.get('sessions').get(currentSessionId).get('items').set(itemData);
    });
    
    // Update session metadata
    gun.get('sessions').get(currentSessionId).put({
        itemCount: currentSessionItems.size,
        lastUpdate: Date.now()
    });
}

// Load recent scanning sessions
async function loadRecentSessions() {
    return new Promise((resolve) => {
        const sessions = [];
        gun.get('sessions').map().once((sessionData, sessionId) => {
            if (sessionData && sessionData.startTime) {
                sessions.push(sessionData);
            }
        });
        
        // Give it a moment to load
        setTimeout(() => resolve(sessions.sort((a, b) => b.startTime - a.startTime)), 1500);
    });
}

async function sendChatCompletionRequest(instruction, imageBase64URL) {
    try {
        const response = await fetch(`${baseURL.value}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: "gpt-4-vision-preview",
                messages: [
                    {
                        role: "user",
                        content: [
                            {
                                type: "text",
                                text: instruction
                            },
                            {
                                type: "image_url",
                                image_url: {
                                    url: imageBase64URL
                                }
                            }
                        ]
                    }
                ],
                max_tokens: 500
            })
        });

        if (!response.ok) {
            const errorData = await response.text();
            throw new Error(`Server error: ${response.status} - ${errorData}`);
        }

        const data = await response.json();
        return data.choices[0].message.content;
    } catch (error) {
        throw new Error(`Request failed: ${error.message}`);
    }
}

async function initCamera() {
    try {
        // Start with portrait constraints
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'environment',
                aspectRatio: { ideal: 0.75 }, // 3:4 portrait ratio
                width: { ideal: 720 },
                height: { ideal: 1280 }
            }, 
            audio: false 
        });
        video.srcObject = stream;
        updateStatus('ready', 'Camera ready - start ASL recognition');
        return true;
    } catch (err) {
        console.error("Error accessing camera:", err);
        updateStatus('error', `Camera error: ${err.message}`);
        throw err;
    }
}

// Camera rotation handler
function setupCameraRotation() {
    const wrapper = document.querySelector('.video-wrapper');
    let isPortrait = true; // Start in portrait mode
    
    // Set initial portrait mode
    wrapper.style.aspectRatio = '3/4';
    
    document.getElementById('rotateBtn').addEventListener('click', async () => {
        isPortrait = !isPortrait;
        
        // Get current track
        const track = stream.getVideoTracks()[0];
        
        // Apply new constraints
        try {
            await track.applyConstraints({
                aspectRatio: isPortrait ? 0.75 : 1.33333 // 3:4 or 4:3
            });
            
            // Update wrapper aspect ratio
            wrapper.style.aspectRatio = isPortrait ? '3/4' : '4/3';
        } catch (err) {
            console.error('Failed to change aspect ratio:', err);
        }
    });
}

// Clear current session items when starting new scan
function clearCurrentSession() {
    currentSessionItems.clear();
    itemsList.innerHTML = '<p style="color: var(--text-secondary); font-style: italic;">Start scanning to recognize ASL signs...</p>';
}

// Enhanced history display with session loading
function displayHistory(sessions) {
    if (sessions.length === 0) {
        historyList.innerHTML = '<p style="color: var(--text-secondary); font-style: italic;">No recent scanning sessions...</p>';
        return;
    }

    const historyHTML = sessions.map(session => {
        const date = new Date(session.startTime).toLocaleDateString();
        const time = new Date(session.startTime).toLocaleTimeString();
        const duration = session.endTime ? 
            Math.round((session.endTime - session.startTime) / 1000) + 's' : 
            'Active';
        
        return `
        <div class="item-card" style="border-left-color: var(--accent-color);">
            <div class="item-name">Session: ${date} at ${time}</div>
            <div class="item-details">
                <strong>Duration:</strong> ${duration}<br>
                <strong>Items Found:</strong> ${session.itemCount || 0}<br>
                <button onclick="loadSession('${session.id}')" class="settings-input" style="margin-top: 10px;">
                    View Items
                </button>
            </div>
        </div>
        `;
    }).join('');

    historyList.innerHTML = historyHTML;
}

// Load specific session
function loadSession(sessionId) {
    clearCurrentSession();
    gun.get('sessions').get(sessionId).get('items').map().once((item, id) => {
        if (item) {
            addItemToDisplay(item);
        }
    });
}

function updateStatus(type, message) {
    const indicator = document.querySelector('.status-indicator');
    indicator.className = `status-indicator status-${type}`;
    overlayText.textContent = message;
    videoOverlay.classList.toggle('show', type !== 'ready');
}

function captureImage() {
    if (!stream || !video.videoWidth) {
        console.warn("Video stream not ready for capture.");
        return null;
    }
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    
    // Since video is mirrored for display, we need to flip it back for training
    context.save();
    context.scale(-1, 1); // Flip horizontally
    context.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
    context.restore();
    
    return canvas.toDataURL('image/jpeg', 0.7);
}

// Current session ID
let currentSessionId = `scan_${Date.now()}`;
let currentSessionItems = new Set();

function parseSignLanguageResponse(response) {
    // Show raw output for debugging
    document.getElementById('rawOutput').textContent = response;
    
    const recognizedSigns = [];
    const lines = response.split('\n');
    
    for (const line of lines) {
        if (line.includes('SIGN:')) {
            const signMatch = line.match(/SIGN:\s*([^|]+)/);
            const confidenceMatch = line.match(/CONFIDENCE:\s*([^|]+)/);
            const descriptionMatch = line.match(/DESCRIPTION:\s*([^|]+)/);
            
            if (signMatch) {
                const signText = signMatch[1].trim();
                // Only add if not already in current session
                if (!currentSessionItems.has(signText)) {
                    const sign = {
                        id: `sign-${Date.now()}`,
                        name: signText,
                        confidence: confidenceMatch ? confidenceMatch[1].trim() : 'Medium',
                        description: descriptionMatch ? descriptionMatch[1].trim() : 'N/A',
                        timestamp: Date.now()
                    };
                    recognizedSigns.push(sign);
                    currentSessionItems.add(signText);
                    
                    // Store in Gun.js
                    gun.get('signs').get(sign.id).put(sign);
                    gun.get('sessions').get(currentSessionId).get('signs').set(sign);
                }
            }
        }
    }
    
    // If no structured signs found, check for common ASL phrases
    if (recognizedSigns.length === 0) {
        const commonSigns = ['hello', 'thank you', 'please', 'yes', 'no', 'help', 'stop', 'go', 'come', 'good', 'bad', 'more', 'finished', 'water', 'food'];
        
        for (const signWord of commonSigns) {
            if (response.toLowerCase().includes(signWord) && !currentSessionItems.has(signWord)) {
                const sign = {
                    id: `sign-${Date.now()}`,
                    name: signWord,
                    confidence: 'Low',
                    description: 'Detected from text',
                    timestamp: Date.now()
                };
                recognizedSigns.push(sign);
                currentSessionItems.add(signWord);
                
                // Store in Gun.js
                gun.get('signs').get(sign.id).put(sign);
                gun.get('sessions').get(currentSessionId).get('signs').set(sign);
            }
        }
    }
    
    return recognizedSigns;
}

// Execute commands based on recognized signs
function executeSignCommand(signText) {
    const command = signText.toLowerCase();
    
    switch(command) {
        case 'hello':
            speakText("Hello! ASL system is ready.");
            break;
        case 'help':
            speakText("Available commands: Hello, Thank you, Stop, Go, Robot pick up, Robot deliver, Call Ava, Chat with Ava");
            break;
        case 'stop':
            if (isProcessing) {
                handleStop();
                speakText("ASL recognition stopped");
            }
            break;
        case 'go':
        case 'start':
            if (!isProcessing) {
                handleStart();
                speakText("ASL recognition started");
            }
            break;
        case 'robot pick up':
        case 'pick up':
            sendRobotCommand('pick_up');
            speakText("Robot picking up object");
            break;
        case 'robot deliver':
        case 'deliver':
            sendRobotCommand('deliver');
            speakText("Robot delivering object");
            break;
        case 'call vapi':
        case 'call ava':
        case 'phone call':
            startVapiPhoneCall();
            break;
        case 'chat ava':
        case 'chat vapi':
        case 'ask ava':
            chatWithVapi("Hello, I'm communicating through ASL. How are you today?");
            break;
        case 'search':
        case 'internet search':
            chatWithVapi("Please help me search the internet for information");
            break;
        case 'spreadsheet':
        case 'open spreadsheet':
            chatWithVapi("Please help me open or create a spreadsheet");
            break;
        case 'lights on':
            speakText("Turning lights on");
            // Future smart home integration
            break;
        case 'lights off':
            speakText("Turning lights off");
            // Future smart home integration
            break;
        case 'thank you':
            speakText("You're welcome!");
            break;
        default:
    }
}

// Text-to-Speech function
function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 0.8;
        speechSynthesis.speak(utterance);
    }
    
    // Also show visual feedback
    showNotification(text, 'info', 3000);
}

// Send commands to robot arm
async function sendRobotCommand(command) {
    try {
        const response = await fetch('/robot/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command, timestamp: Date.now() })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`Robot command executed: ${command}`, result);
        } else {
            console.error('Robot command failed');
        }
    } catch (error) {
        console.error('Robot communication error:', error);
        // For demo purposes, simulate robot action
        showNotification(`Robot would execute: ${command}`, 'info', 2000);
    }
}

// Log signs for ML training
function logSignForTraining(signText) {
    const trainingData = {
        sign: signText,
        timestamp: Date.now(),
        imageData: captureImage(), // Capture current frame
        sessionId: currentSessionId
    };
    
    // Store for SmolVLM training
    gun.get('training_data').set(trainingData);
    
    // Also send to training server if available
    fetch('/ml/log_sign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(trainingData)
    }).catch(err => console.log('Training server not available:', err));
}


function displaySigns(newSigns) {
    // Get all signs from current session
    gun.get('sessions').get(currentSessionId).get('signs').map().once((sign, id) => {
    });

    // Add any new signs
    newSigns.forEach(sign => addSignToDisplay(sign));
}

function addSignToDisplay(sign) {
    // If no signs are displayed yet, clear the "no signs" message
    if (itemsList.innerHTML.includes('Start scanning to identify') || itemsList.innerHTML.includes('No sellable items detected')) {
        itemsList.innerHTML = '';
    }

    // Create sign card if it doesn't exist
    if (!document.getElementById(`sign-${sign.id}`)) {
        const card = document.createElement('div');
        card.id = `sign-${sign.id}`;
        card.className = 'item-card';
        
        const confidenceClass = sign.confidence.toLowerCase();
        if (['high', 'medium', 'low'].includes(confidenceClass)) {
            card.classList.add(`sellable-${confidenceClass}`);
        }
        
        card.innerHTML = `
            <div class="item-name">${sign.name}</div>
            <div class="item-details">
                <strong>Confidence:</strong> ${sign.confidence}<br>
                <strong>Description:</strong> ${sign.description}
            </div>
        `;
        itemsList.prepend(card);
    }
}

// Save recognized signs to local storage
function saveSignsLocally(signs) {
    // Store individual signs in current session
    signs.forEach((sign, index) => {
        const signData = {
            ...sign,
            sessionId: currentSessionId,
            itemIndex: index,
            timestamp: Date.now()
        };
        gun.get('sessions').get(currentSessionId).get('signs').set(signData);
    });
    
    // Update session metadata
    gun.get('sessions').get(currentSessionId).put({
        lastUpdate: Date.now()
    });
}

async function scanForItems() {
    if (!isProcessing) return;

    updateStatus('processing', 'Recognizing sign language...');

    const imageBase64URL = captureImage();
    if (!imageBase64URL) {
        updateStatus('ready', 'Ready for ASL recognition');
        return;
    }

    try {
        const response = await sendChatCompletionRequest(ASL_RECOGNITION_INSTRUCTION, imageBase64URL);
        const newSigns = parseSignLanguageResponse(response);
        
        if (newSigns.length > 0) {
            displaySigns(newSigns);
            saveSignsLocally(newSigns);
            
            // Execute command for the first recognized sign
            executeSignCommand(newSigns[0].name);
        }
        
        updateStatus('ready', 'Ready for ASL recognition');
    } catch (error) {
        console.error("Error during scanning:", error);
        updateStatus('error', `Error: ${error.message}`);
    }
}

function handleStart() {
    if (isProcessing) return;
    isProcessing = true;
    startButton.textContent = 'Stop';
    startButton.classList.remove('start');
    startButton.classList.add('stop');
    
    // Create new session
    currentSessionId = `scan_${Date.now()}`;
    gun.get('sessions').get(currentSessionId).put({
        id: currentSessionId,
        startTime: Date.now(),
        itemCount: 0
    });
    
    clearCurrentSession();
    
    const interval = parseInt(intervalSelect.value, 10);
    intervalId = setInterval(scanForItems, interval);
    scanForItems(); // Initial scan
}

function handleStop() {
    if (!isProcessing) return;
    isProcessing = false;
    startButton.textContent = 'Start';
    startButton.classList.remove('stop');
    startButton.classList.add('start');
    clearInterval(intervalId);
    updateStatus('ready', 'Ready for ASL recognition');
    
    // Save session end time
    gun.get('sessions').get(currentSessionId).put({ endTime: Date.now() });
}

// FAB Controls
const settingsBtn = document.getElementById('settingsBtn');
const settingsMenu = document.getElementById('settingsMenu');

settingsBtn.addEventListener('click', () => {
    settingsMenu.classList.toggle('show');
});

document.addEventListener('click', (e) => {
    if (!settingsBtn.contains(e.target) && !settingsMenu.contains(e.target)) {
        settingsMenu.classList.remove('show');
    }
});

// Training Modal Controls
trainingBtn.addEventListener('click', () => {
    trainingModal.style.display = 'flex';
    updateTrainingStats();
});

trainingCloseBtn.addEventListener('click', () => {
    trainingModal.style.display = 'none';
});

clearDataBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear all collected training data? This cannot be undone.')) {
        gun.get('training_data').put(null);
        updateTrainingStats();
        showNotification('Training data cleared', 'info');
    }
});

exportDataBtn.addEventListener('click', () => {
    const dataToExport = [];
    gun.get('training_data').map().once(data => {
        if (data) {
            dataToExport.push(data);
        }
    });
    
    setTimeout(() => {
        if (dataToExport.length > 0) {
            const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `asl_training_data_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showNotification('Training data exported', 'success');
        } else {
            showNotification('No training data to export', 'warning');
        }
    }, 1000);
});

function updateTrainingStats() {
    let count = 0;
    gun.get('training_data').map().once(() => count++);
    
    setTimeout(() => {
        collectedCount.textContent = `${count} signs collected`;
        // Placeholder for accuracy
        currentAccuracy.textContent = count > 50 ? 'Good' : 'Needs more data';
    }, 500);
}

// Raw output toggle
document.getElementById('toggleRawBtn').addEventListener('click', () => {
    const rawOutput = document.getElementById('rawOutput');
    const btn = document.getElementById('toggleRawBtn');
    
    if (rawOutput.style.display === 'none') {
        rawOutput.style.display = 'block';
        btn.textContent = 'Hide';
    } else {
        rawOutput.style.display = 'none';
        btn.textContent = 'Show';
    }
});

// Notification system
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 500);
    }, duration);
}

// Loading screen logic
async function initializeApp() {
    const loadingScreen = document.getElementById('loadingScreen');
    const loadingText = document.getElementById('loadingText');
    
    // Check browser
    document.getElementById('checkBrowser').querySelector('.loading-icon').textContent = '✅';
    
    // Check camera
    try {
        await initCamera();
        document.getElementById('checkCamera').querySelector('.loading-icon').textContent = '✅';
    } catch (err) {
        document.getElementById('checkCamera').querySelector('.loading-icon').textContent = '❌';
        loadingText.textContent = 'Camera access denied. Please enable camera permissions.';
        return;
    }
    
    // Check Gun.js
    setTimeout(() => {
        document.getElementById('checkGun').querySelector('.loading-icon').textContent = '✅';
    }, 500);
    
    // Check AI server
    if (window.ASL_CONFIG?.AI_SERVER_AVAILABLE) {
        try {
            const response = await fetch(`${AI_SERVER_URL}/health`);
            if (response.ok) {
                document.getElementById('checkAI').querySelector('.loading-icon').textContent = '✅';
            } else {
                document.getElementById('checkAI').querySelector('.loading-icon').textContent = '⚠️';
            }
        } catch {
            document.getElementById('checkAI').querySelector('.loading-icon').textContent = '❌';
        }
    } else {
        document.getElementById('checkAI').querySelector('.loading-icon').textContent = '⚪️';
        document.getElementById('checkAI').querySelector('span:last-child').textContent = 'AI server disabled';
    }
    
    // Check ASL server
    try {
        const response = await fetch(`${ASL_SERVER_URL}/health`);
        if (response.ok) {
            document.getElementById('checkASL').querySelector('.loading-icon').textContent = '✅';
        } else {
            document.getElementById('checkASL').querySelector('.loading-icon').textContent = '⚠️';
        }
    } catch {
        document.getElementById('checkASL').querySelector('.loading-icon').textContent = '❌';
    }
    
    loadingText.textContent = 'Initialization complete!';
    
    setTimeout(() => {
        loadingScreen.classList.add('hidden');
    }, 1000);
}

// Event Listeners
startButton.addEventListener('click', () => {
    if (isProcessing) {
        handleStop();
    } else {
        handleStart();
    }
});

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    baseURL.value = AI_SERVER_URL;
    initializeApp();
    setupCameraRotation();
});
