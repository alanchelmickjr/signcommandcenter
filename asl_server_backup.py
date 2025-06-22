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
ROBOT_API_URL = "http://localhost:5000"  # Robot control server
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

def process_asl_response(ai_response, image_data):
    """Process AI response to extract and enhance ASL commands"""
    try:
        # Look for ASL command patterns
        detected_commands = []
        
        for command, action in ASL_COMMANDS.items():
            if command.lower() in ai_response.lower():
                detected_commands.append({
                    'command': command,
                    'action': action,
                    'confidence': 'High' if len(command.split()) > 1 else 'Medium'
                })
        
        # Enhance the response with structured ASL data
        enhanced_response = ai_response
        
        if detected_commands:
            enhanced_response += "\n\nDETECTED ASL COMMANDS:\n"
            for cmd in detected_commands:
                enhanced_response += f"SIGN: {cmd['command']} | CONFIDENCE: {cmd['confidence']} | ACTION: {cmd['action']}\n"
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"ASL processing error: {str(e)}")
        return ai_response

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
                    'provider': 'openai',
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a helpful assistant for ASL Command Center. You can help with general questions and support.'
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

if __name__ == '__main__':
    logger.info("Starting ASL Recognition Server for Berkeley Cal Hacks 2025")
    logger.info(f"Llama server: {LLAMA_SERVER_URL}")
    logger.info(f"Robot API: {ROBOT_API_URL}")
    logger.info(f"ASL commands loaded: {len(ASL_COMMANDS)}")
    
    # Get port from environment variable or default to 5000
    port = int(os.getenv('ASL_SERVER_PORT', 5000))
    logger.info(f"Starting ASL server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
