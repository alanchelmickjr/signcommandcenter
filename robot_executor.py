#!/usr/bin/env python3
"""
Simple robot executor server to bridge frontend ASL commands to actual robot execution
"""

from flask import Flask, request, jsonify
import subprocess
import os
import threading

app = Flask(__name__)

# Simple CORS header for local development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/robot/execute_real', methods=['POST', 'OPTIONS'])
def execute_robot():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json if request.json else {}
        command = data.get('command', 'pick_up')
        
        print(f"🤖 Executing robot command: {command}")
        
        # Use the exact working command with venv activation
        robot_command = "cd ../Cal-Hacks--Hack-for-Impact--2025 && source .venv/bin/activate && python -m lerobot.replay --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5A7A0186141 --robot.id=my_awesome_follower_arm --dataset.repo_id=lerobot/svla_so101_pickplace --dataset.episode=0"
        
        # Execute in background thread to avoid blocking
        def run_robot():
            try:
                result = subprocess.run(["bash", "-c", robot_command],
                                      capture_output=True, text=True, timeout=30)
                print(f"✅ Robot execution completed: {result.stdout}")
                if result.stderr:
                    print(f"Robot stderr: {result.stderr}")
            except Exception as e:
                print(f"❌ Robot execution error: {e}")
        
        # Start robot execution in background
        robot_thread = threading.Thread(target=run_robot)
        robot_thread.start()
        
        return jsonify({
            "status": "success",
            "message": f"Robot command '{command}' initiated",
            "command": command
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/robot/health', methods=['GET'])
def health():
    return jsonify({"status": "Robot executor ready"})

if __name__ == '__main__':
    print("🤖 Starting Robot Executor Server on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)