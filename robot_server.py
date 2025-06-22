#!/usr/bin/env python3
"""
Simple Robot Control Server for ASL Integration
Simulates robot arm commands for Berkeley Cal Hacks 2025 demo
"""

import json
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Robot state
robot_state = {
    'position': 'home',
    'is_holding': False,
    'last_command': None,
    'last_command_time': None,
    'status': 'ready'
}

# Command history
command_history = []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Robot Control Server',
        'robot_status': robot_state['status'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/command', methods=['POST'])
def execute_command():
    """Execute robot commands"""
    try:
        data = request.json
        command = data.get('command')
        source = data.get('source', 'unknown')
        timestamp = data.get('timestamp', time.time())
        
        logger.info(f"Robot command: {command} from {source}")
        
        # Validate command
        valid_commands = ['pick_up', 'deliver', 'stop', 'home']
        if command not in valid_commands:
            return jsonify({'error': 'Invalid command'}), 400
        
        # Log command
        command_entry = {
            'command': command,
            'source': source,
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp).isoformat()
        }
        command_history.append(command_entry)
        
        # Execute command (simulated)
        result = simulate_robot_command(command)
        
        # Update robot state
        robot_state['last_command'] = command
        robot_state['last_command_time'] = timestamp
        robot_state['status'] = result['status']
        
        logger.info(f"Command executed: {result}")
        
        return jsonify({
            'success': True,
            'command': command,
            'result': result,
            'robot_state': robot_state,
            'timestamp': timestamp
        })
        
    except Exception as e:
        logger.error(f"Command execution error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get robot status"""
    return jsonify({
        'robot_state': robot_state,
        'command_count': len(command_history),
        'recent_commands': command_history[-5:]  # Last 5 commands
    })

@app.route('/history', methods=['GET'])
def get_history():
    """Get command history"""
    return jsonify({
        'total_commands': len(command_history),
        'commands': command_history
    })

def simulate_robot_command(command):
    """Simulate robot arm movements"""
    global robot_state
    
    if command == 'pick_up':
        if robot_state['is_holding']:
            return {
                'status': 'error',
                'message': 'Robot is already holding an object'
            }
        
        # Simulate pick up sequence
        robot_state['position'] = 'target'
        time.sleep(0.1)  # Simulate movement time
        robot_state['is_holding'] = True
        robot_state['position'] = 'lifted'
        
        return {
            'status': 'completed',
            'message': 'Object picked up successfully',
            'action': 'pick_up',
            'sequence': ['move_to_target', 'close_gripper', 'lift_object']
        }
    
    elif command == 'deliver':
        if not robot_state['is_holding']:
            return {
                'status': 'error',
                'message': 'Robot is not holding any object'
            }
        
        # Simulate delivery sequence
        robot_state['position'] = 'delivery'
        time.sleep(0.1)  # Simulate movement time
        robot_state['is_holding'] = False
        robot_state['position'] = 'home'
        
        return {
            'status': 'completed',
            'message': 'Object delivered successfully',
            'action': 'deliver',
            'sequence': ['move_to_delivery', 'open_gripper', 'return_home']
        }
    
    elif command == 'stop':
        robot_state['status'] = 'stopped'
        return {
            'status': 'stopped',
            'message': 'Robot stopped immediately',
            'action': 'emergency_stop'
        }
    
    elif command == 'home':
        robot_state['position'] = 'home'
        robot_state['status'] = 'ready'
        return {
            'status': 'completed',
            'message': 'Robot returned to home position',
            'action': 'home'
        }
    
    return {
        'status': 'error',
        'message': f'Unknown command: {command}'
    }

if __name__ == '__main__':
    logger.info("Starting Robot Control Server for Berkeley Cal Hacks 2025")
    logger.info("Simulating robot arm for ASL integration demo")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
