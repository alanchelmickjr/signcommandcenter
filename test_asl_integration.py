#!/usr/bin/env python3
"""
Quick test to verify ASL training and model loading
"""

import json
import os
import sys
from pathlib import Path

def test_model_loading():
    """Test if the trained model can be loaded"""
    print("🧪 Testing ASL Model Loading...")
    
    model_path = "models/asl_patterns.json"
    
    if not os.path.exists(model_path):
        print("❌ Model file not found")
        return False
    
    try:
        with open(model_path, 'r') as f:
            model_data = json.load(f)
        
        print(f"✅ Model loaded successfully!")
        print(f"   Model Type: {model_data.get('model_type')}")
        print(f"   Version: {model_data.get('version')}")
        print(f"   Trained Commands: {model_data.get('trained_commands')}")
        print(f"   Status: {model_data.get('status')}")
        
        patterns = model_data.get('patterns', {})
        print(f"   Available ASL Commands:")
        for cmd in patterns.keys():
            confidence = patterns[cmd].get('confidence', 0)
            gesture = patterns[cmd].get('gesture', 'unknown')
            print(f"     • {cmd} (confidence: {confidence}, gesture: {gesture})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

def test_asl_server_import():
    """Test if ASL server can import and load the model"""
    print("\n🧪 Testing ASL Server Model Integration...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, '.')
        
        # Import the model loading function from ASL server
        import asl_server
        
        # Check if the model was loaded
        if hasattr(asl_server, 'TRAINED_MODEL') and asl_server.TRAINED_MODEL:
            print("✅ ASL Server loaded trained model successfully!")
            model = asl_server.TRAINED_MODEL
            print(f"   Loaded {model.get('trained_commands', 0)} commands")
            print(f"   Model status: {model.get('status', 'unknown')}")
            return True
        else:
            print("⚠️  ASL Server didn't load the trained model")
            return False
            
    except Exception as e:
        print(f"❌ ASL Server import failed: {e}")
        return False

def test_confidence_function():
    """Test the ASL confidence calculation"""
    print("\n🧪 Testing ASL Confidence Calculation...")
    
    try:
        import asl_server
        
        test_commands = [
            "hello",
            "robot pick up", 
            "lights on",
            "call ava",
            "unknown command"
        ]
        
        for cmd in test_commands:
            confidence = asl_server.get_asl_confidence(cmd)
            print(f"   '{cmd}' -> confidence: {confidence:.2f}")
        
        print("✅ Confidence calculation working!")
        return True
        
    except Exception as e:
        print(f"❌ Confidence calculation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤟 ASL Command Center - Model Integration Test")
    print("=" * 50)
    
    tests = [
        test_model_loading,
        test_asl_server_import,
        test_confidence_function
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! ASL training and model integration working correctly!")
        print("💡 The system is ready for camera-based ASL training and recognition!")
        return True
    else:
        print("⚠️  Some tests failed - check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
