#!/usr/bin/env python3
"""
ASL Recognition Server for Berkeley Cal Hacks 2025
Real-time ASL recognition using SmolVLM and OpenAI-compatible API
"""

import json
import time
import base64
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
LLAMA_SERVER_URL = "http://localhost:8080"
ROBOT_API_URL = "http://localhost:5001"  # Robot control server
VAPI_API_KEY = os.getenv('VAPI_API_KEY', 'your-vapi-key')
VAPI_API_URL = "https://api.vapi.ai/call"

# ASL command mapping
ASL_COMMANDS = {
    'hello': 'greeting',
    'thank you': 'gratitude', 
    'help': 'assistance',
    'stop': 'system_stop',
    'go': 'system_start',
    'start': 'system_start',
    'robot pick up': 'robot_pickup',
    'pick up': 'robot_pickup',
    'robot deliver': 'robot_deliver',
    'deliver': 'robot_deliver',
    'lights on': 'lights_on',
    'lights off': 'lights_off',
    'call vapi': 'vapi_call',
    'phone call': 'vapi_call',
    'make call': 'vapi_call',
    'search': 'internet_search',
    'spreadsheet': 'open_spreadsheet'
}

# Training data storage
training_data = []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ASL Recognition Server',
        'timestamp': datetime.now().isoformat(),
        'llama_server': check_llama_server(),
        'commands_loaded': len(ASL_COMMANDS)
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint for ASL recognition"""
    try:
        data = request.json
        logger.info(f"Received ASL recognition request")
        
        # Extract image from request
        image_data = None
        messages = data.get('messages', [])
        
        for message in messages:
            if isinstance(message.get('content'), list):
                for content in message['content']:
                    if content.get('type') == 'image_url':
                        image_data = content['image_url']['url']
                        break
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Forward to llama.cpp server for vision processing
        response = requests.post(
            f"{LLAMA_SERVER_URL}/v1/chat/completions",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Process the AI response for ASL commands
            ai_response = result['choices'][0]['message']['content']
            processed_response = process_asl_response(ai_response, image_data)
            
            # Update the response with processed ASL data
            result['choices'][0]['message']['content'] = processed_response
            
            logger.info(f"ASL recognition completed successfully")
            return jsonify(result)
        else:
            logger.error(f"Llama server error: {response.status_code}")
            return jsonify({'error': 'Vision processing failed'}), 500
            
    except Exception as e:
        logger.error(f"ASL recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/robot/command', methods=['POST'])
def robot_command():
    """Handle robot control commands from ASL recognition"""
    try:
        data = request.json
        command = data.get('command')
        timestamp = data.get('timestamp', time.time())
        
        logger.info(f"Robot command received: {command}")
        
        # Validate command
        if command not in ['pick_up', 'deliver', 'stop', 'home']:
            return jsonify({'error': 'Invalid robot command'}), 400
        
        # Log command for safety
        log_robot_command(command, timestamp)
        
        # Try to forward to actual robot API
        try:
            robot_response = requests.post(
                f"{ROBOT_API_URL}/command",
                json={'command': command, 'source': 'asl', 'timestamp': timestamp},
                timeout=5
            )
            
            if robot_response.status_code == 200:
                return jsonify({
                    'status': 'executed',
                    'command': command,
                    'timestamp': timestamp,
                    'robot_response': robot_response.json()
                })
        except requests.RequestException:
            logger.warning("Robot API not available, simulating command")
        
        # Simulate robot response for demo
        return jsonify({
            'status': 'simulated',
            'command': command,
            'timestamp': timestamp,
            'message': f"Robot would execute: {command}"
        })
        
    except Exception as e:
        logger.error(f"Robot command error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/ml/log_sign', methods=['POST'])
def log_sign():
    """Log ASL sign data for training"""
    try:
        data = request.json
        sign = data.get('sign')
        image_data = data.get('imageData')
        session_id = data.get('sessionId')
        timestamp = data.get('timestamp', time.time())
        
        # Store training data
        training_entry = {
            'sign': sign,
            'timestamp': timestamp,
            'session_id': session_id,
            'image_url': image_data[:100] + '...' if image_data else None,  # Truncate for storage
            'logged_at': datetime.now().isoformat()
        }
        
        training_data.append(training_entry)
        
        # Keep only last 1000 entries to prevent memory issues
        if len(training_data) > 1000:
            training_data.pop(0)
        
        logger.info(f"Logged ASL sign: {sign}")
        
        return jsonify({
            'status': 'logged',
            'sign': sign,
            'training_entries': len(training_data)
        })
        
    except Exception as e:
        logger.error(f"Sign logging error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/vapi/trigger', methods=['POST'])
def vapi_trigger():
    """Trigger Vapi functions from ASL commands"""
    try:
        data = request.json
        function = data.get('function')
        parameters = data.get('parameters', {})
        
        logger.info(f"Vapi function triggered: {function}")
        
        # Simulate Vapi integration
        if function == 'phone_call':
            phone_number = parameters.get('phone_number')
            message = parameters.get('message', "Hello, this is an ASL Command Center call.")
            
            # Make the Vapi call
            call_result = make_vapi_call(phone_number, message)
            
            if call_result.get('success'):
                return jsonify({
                    'status': 'call_initiated',
                    'function': 'phone_call',
                    'call_id': call_result.get('call_id'),
                    'message': 'Phone call initiated through Vapi'
                })
            else:
                return jsonify({
                    'status': 'call_failed',
                    'function': 'phone_call',
                    'error': call_result.get('error')
                }), 500
        elif function == 'spreadsheet':
            return jsonify({
                'status': 'opened',
                'function': 'spreadsheet',
                'message': 'Spreadsheet would be opened and controlled'
            })
        elif function == 'search':
            query = parameters.get('query', 'default search')
            return jsonify({
                'status': 'searching',
                'function': 'search',
                'query': query,
                'message': f'Internet search for: {query}'
            })
        else:
            return jsonify({'error': 'Unknown Vapi function'}), 400
            
    except Exception as e:
        logger.error(f"Vapi trigger error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/vapi/call', methods=['POST'])
def vapi_call():
    """Handle Vapi phone call requests from ASL recognition"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        message = data.get('message', "Hello, this is a call initiated through ASL Command Center.")
        source = data.get('source', 'asl')
        
        logger.info(f"Vapi call request: phone={phone_number}, source={source}")
        
        # Make the Vapi call
        import asyncio
        result = asyncio.run(make_vapi_call(phone_number, message))
        
        if result['success']:
            return jsonify({
                'status': 'call_initiated',
                'call_id': result.get('call_id'),
                'phone_number': phone_number,
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'status': 'call_failed',
                'error': result.get('error'),
                'timestamp': time.time()
            }), 400
            
    except Exception as e:
        logger.error(f"Vapi call error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/vapi/status', methods=['GET'])
def vapi_status():
    """Get Vapi service status"""
    return jsonify({
        'service': 'vapi',
        'status': 'available' if VAPI_API_KEY != 'your-vapi-key' else 'not_configured',
        'api_key_configured': VAPI_API_KEY != 'your-vapi-key'
    })

@app.route('/training/data', methods=['GET'])
def get_training_data():
    """Get collected training data"""
    return jsonify({
        'total_entries': len(training_data),
        'recent_entries': training_data[-10:],  # Last 10 entries
        'signs_collected': list(set(entry['sign'] for entry in training_data))
    })

@app.route('/training/status', methods=['GET'])
def training_status():
    """Get training status and model information"""
    try:
        model_info = {
            'model_available': TRAINED_MODEL is not None,
            'model_path': 'models/asl_patterns.json',
            'training_data_available': os.path.exists('training_data/annotations'),
            'supported_commands': [],
            'model_details': {}
        }
        
        if TRAINED_MODEL:
            model_info['model_details'] = {
                'model_type': TRAINED_MODEL.get('model_type', 'unknown'),
                'version': TRAINED_MODEL.get('version', '1.0.0'),
                'trained_commands': TRAINED_MODEL.get('trained_commands', 0),
                'training_date': TRAINED_MODEL.get('training_date', 'unknown'),
                'status': TRAINED_MODEL.get('status', 'unknown')
            }
            model_info['supported_commands'] = TRAINED_MODEL.get('supported_commands', [])
        
        # Check for training data
        if os.path.exists('training_data/annotations'):
            try:
                annotation_files = [f for f in os.listdir('training_data/annotations') if f.endswith('.json')]
                model_info['annotation_files'] = len(annotation_files)
            except:
                model_info['annotation_files'] = 0
        
        return jsonify(model_info)
        
    except Exception as e:
        logger.error(f"Training status error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Load trained ASL model if available
def load_trained_model():
    """Load the trained ASL pattern model"""
    model_path = "models/asl_patterns.json"
    if os.path.exists(model_path):
        try:
            with open(model_path, 'r') as f:
                model_data = json.load(f)
            logger.info(f"✅ Loaded trained ASL model: {model_data.get('trained_commands', 0)} commands")
            return model_data
        except Exception as e:
            logger.warning(f"Failed to load trained model: {e}")
    
    # Try minimal model in current directory
    minimal_path = "asl_patterns_minimal.json"
    if os.path.exists(minimal_path):
        try:
            with open(minimal_path, 'r') as f:
                model_data = json.load(f)
            logger.info(f"✅ Loaded minimal ASL model: {model_data.get('trained_commands', 0)} commands")
            return model_data
        except Exception as e:
            logger.warning(f"Failed to load minimal model: {e}")
    
    logger.info("🔄 No trained model found - using hardcoded patterns")
    # Return hardcoded patterns if no file available
    return {
        'model_type': 'hardcoded_patterns',
        'version': '1.0.0',
        'patterns': {
            'hello': {'gesture': 'wave', 'confidence': 0.9},
            'help': {'gesture': 'fist_on_palm', 'confidence': 0.8},
            'stop': {'gesture': 'flat_hand', 'confidence': 0.9},
            'robot pick up': {'gesture': 'grasp', 'confidence': 0.8},
            'robot deliver': {'gesture': 'place', 'confidence': 0.8},
            'lights on': {'gesture': 'up', 'confidence': 0.7},
            'lights off': {'gesture': 'down', 'confidence': 0.7},
            'call ava': {'gesture': 'phone', 'confidence': 0.8},
            'chat ava': {'gesture': 'talk', 'confidence': 0.8},
            'thank you': {'gesture': 'chin_forward', 'confidence': 0.9}
        },
        'trained_commands': 10,
        'status': 'hardcoded_fallback',
        'supported_commands': ['hello', 'help', 'stop', 'robot pick up', 'robot deliver', 'lights on', 'lights off', 'call ava', 'chat ava', 'thank you']
    }

# Load the model at startup
TRAINED_MODEL = load_trained_model()

def get_asl_confidence(recognized_text):
    """Get confidence score for ASL recognition using trained model"""
    if not TRAINED_MODEL or not recognized_text:
        return 0.5  # Default confidence
    
    text_lower = recognized_text.lower().strip()
    patterns = TRAINED_MODEL.get('patterns', {})
    
    # Direct match
    if text_lower in patterns:
        return patterns[text_lower].get('confidence', 0.8)
    
    # Partial match
    for pattern_text, pattern_data in patterns.items():
        if any(word in text_lower for word in pattern_data.get('words', [])):
            return pattern_data.get('confidence', 0.6) * 0.8  # Reduced for partial match
    
    return 0.3  # Low confidence for unrecognized patterns

def process_asl_response(ai_response, image_data):
    """Process AI response to extract and enhance ASL commands"""
    try:
        # Look for ASL command patterns using trained model
        detected_commands = []
        
        # First try simple pattern recognition (always works)
        simple_signs = simple_pattern_recognition(ai_response)
        detected_commands.extend(simple_signs)
        
        # Use trained model patterns if available (additional detection)
        if TRAINED_MODEL:
            patterns = TRAINED_MODEL.get('patterns', {})
            
            for pattern_text, pattern_data in patterns.items():
                # Skip if already found by simple recognition
                if any(cmd.get('sign') == pattern_text for cmd in detected_commands):
                    continue
                    
                if pattern_text.lower() in ai_response.lower():
                    confidence_score = get_asl_confidence(pattern_text)
                    confidence_level = 'High' if confidence_score > 0.8 else 'Medium' if confidence_score > 0.6 else 'Low'
                    
                    # Map to action if available
                    action = ASL_COMMANDS.get(pattern_text, pattern_data.get('gesture', 'unknown'))
                    
                    detected_commands.append({
                        'sign': pattern_text,
                        'action': action,
                        'confidence': confidence_level,
                        'confidence_score': confidence_score,
                        'gesture': pattern_data.get('gesture', 'unknown')
                    })
        
        # Enhance the response with structured ASL data
        enhanced_response = ai_response
        
        if detected_commands:
            enhanced_response += "\n\nDETECTED ASL COMMANDS:\n"
            for cmd in detected_commands:
                sign_name = cmd.get('sign', 'unknown')
                confidence = cmd.get('confidence', 'Medium')
                action = cmd.get('action', 'unknown')
                enhanced_response += f"SIGN: {sign_name} | CONFIDENCE: {confidence} | ACTION: {action}\n"
                if 'gesture' in cmd:
                    enhanced_response += f"GESTURE: {cmd['gesture']}\n"
                elif 'keyword' in cmd:
                    enhanced_response += f"KEYWORD: {cmd['keyword']}\n"
        else:
            # If no patterns found, at least indicate we're looking for ASL
            enhanced_response += "\n\nASL RECOGNITION: No clear sign language detected in this frame."
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"ASL processing error: {str(e)}")
        return ai_response

def simple_pattern_recognition(ai_response):
    """Simple pattern recognition that works without complex AI"""
    detected_signs = []
    response_lower = ai_response.lower()
    
    # Simple keyword-based recognition
    patterns = {
        'hello': ['wave', 'waving', 'greeting', 'hello'],
        'stop': ['stop', 'flat hand', 'palm up', 'halt'],
        'help': ['help', 'fist on palm', 'assistance'],
        'robot pick up': ['pick up', 'grasp', 'grab', 'lifting'],
        'robot deliver': ['deliver', 'place', 'putting down'],
        'thank you': ['thank', 'grateful', 'chin forward'],
        'lights on': ['lights on', 'turn on', 'illuminate'],
        'lights off': ['lights off', 'turn off', 'dark'],
        'call ava': ['call', 'phone', 'telephone'],
        'chat ava': ['chat', 'talk', 'conversation']
    }
    
    for sign, keywords in patterns.items():
        for keyword in keywords:
            if keyword in response_lower:
                confidence = 'High' if len(keyword) > 4 else 'Medium'
                detected_signs.append({
                    'sign': sign,
                    'confidence': confidence,
                    'keyword': keyword,
                    'action': ASL_COMMANDS.get(sign, 'unknown')
                })
                break  # Only add each sign once
    
    return detected_signs

def check_llama_server():
    """Check if llama.cpp server is running"""
    try:
        response = requests.get(f"{LLAMA_SERVER_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def log_robot_command(command, timestamp):
    """Log robot commands for safety and auditing"""
    log_entry = {
        'command': command,
        'timestamp': timestamp,
        'datetime': datetime.fromtimestamp(timestamp).isoformat(),
        'source': 'asl_recognition'
    }
    
    # In production, this would write to a proper log file
    logger.info(f"ROBOT COMMAND LOG: {json.dumps(log_entry)}")

# Vapi call management
def make_vapi_call(phone_number=None, message="Hello, this is an ASL Command Center call."):
    """Make a phone call using Vapi API"""
    try:
        headers = {
            'Authorization': f'Bearer {VAPI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        call_data = {
            'assistant': {
                'model': {
                    'provider': 'anthropic',
                    'model': 'claude-sonnet-4-preview',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are Agent Ava, a highly intelligent assistant for ASL Command Center built for Berkeley Cal Hacks 2025. You understand and deeply support the deaf and hard-of-hearing community. You provide clear, helpful responses and can assist with accessibility needs, technology questions, robot control, smart home automation, and general support. You are powered by Claude Sonnet 4, the most advanced and capable model available for this critical accessibility work.'
                        }
                    ]
                },
                'voice': {
                    'provider': 'elevenlabs',
                    'voiceId': 'rachel'
                },
                'firstMessage': message
            },
            'phoneNumberId': phone_number or os.getenv('DEFAULT_PHONE_NUMBER'),
            'customer': {
                'number': phone_number or '+1234567890'  # Placeholder
            }
        }
        
        if not phone_number:
            logger.warning("No phone number provided for Vapi call")
            return {'success': False, 'error': 'No phone number provided'}
        
        response = requests.post(VAPI_API_URL, headers=headers, json=call_data)
        
        if response.status_code == 201:
            logger.info(f"Vapi call initiated successfully: {response.json()}")
            return {'success': True, 'call_id': response.json().get('id')}
        else:
            logger.error(f"Vapi call failed: {response.status_code} - {response.text}")
            return {'success': False, 'error': f'API call failed: {response.status_code}'}
            
    except Exception as e:
        logger.error(f"Error making Vapi call: {str(e)}")
        return {'success': False, 'error': str(e)}

@app.route('/test_recognition', methods=['GET'])
def test_recognition():
    """Test endpoint to verify ASL recognition is working"""
    try:
        test_responses = [
            "I see a person waving their hand hello",
            "The person is making a stop gesture with flat hand raised",
            "I observe a grasping motion that looks like pick up",
            "The hand is moving to the chin and forward, looks like thank you"
        ]
        
        results = []
        for test_response in test_responses:
            processed = process_asl_response(test_response, None)
            if "DETECTED ASL COMMANDS:" in processed:
                # Extract the detected commands
                lines = processed.split('\n')
                for line in lines:
                    if line.startswith('SIGN:'):
                        results.append({
                            'input': test_response,
                            'detected': line,
                            'working': True
                        })
                        break
            else:
                results.append({
                    'input': test_response,
                    'detected': 'No sign detected',
                    'working': False
                })
        
        working_count = sum(1 for r in results if r['working'])
        
        return jsonify({
            'status': 'test_complete',
            'total_tests': len(test_responses),
            'working_tests': working_count,
            'success_rate': f"{(working_count/len(test_responses)*100):.1f}%",
            'results': results,
            'ready_for_demo': working_count >= 2
        })
        
    except Exception as e:
        logger.error(f"Test recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting ASL Recognition Server for Berkeley Cal Hacks 2025")
    logger.info(f"Llama server: {LLAMA_SERVER_URL}")
    logger.info(f"Robot API: {ROBOT_API_URL}")
    logger.info(f"ASL commands loaded: {len(ASL_COMMANDS)}")
    
    # Use port 5001 to avoid macOS AirPlay conflicts on port 5000
    port = int(os.getenv('ASL_SERVER_PORT', 5001))
    logger.info(f"Starting ASL server on port {port}")
    
    # Test basic pattern recognition
    print("🧪 Testing ASL recognition patterns...")
    test_responses = [
        "I see a hand waving, this looks like hello",
        "The person is making a stop gesture with flat hand",
        "I observe a grasping motion, possibly pick up"
    ]
    
    for test_response in test_responses:
        result = process_asl_response(test_response, None)
        if "DETECTED ASL COMMANDS:" in result:
            print(f"  ✅ Pattern recognition working: {test_response[:30]}...")
        else:
            print(f"  ⚠️  No patterns detected in: {test_response[:30]}...")
    
    print(f"🤟 Model Status: {TRAINED_MODEL.get('status', 'unknown') if TRAINED_MODEL else 'no model'}")
    print(f"🚀 ASL server ready on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
