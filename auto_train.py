#!/bin/bash
"""
Auto-training trigger for ASL Command Center
Checks if model exists, triggers training if needed
"""

import os
import sys
import json
from pathlib import Path

def check_model_exists():
    """Check if a trained ASL model exists"""
    model_paths = [
        "../models/asl_patterns.json",
        "../models/smolvlm_asl/",
        "./asl_model_checkpoints/"
    ]
    
    for path in model_paths:
        if Path(path).exists():
            print(f"✅ Model found at: {path}")
            return True
    
    print("❌ No trained model found")
    return False

def trigger_training():
    """Trigger the training pipeline"""
    print("🎯 Starting auto-training...")
    
    # Run the training script
    import subprocess
    result = subprocess.run([
        sys.executable, 
        "train_asl_model.py"
    ], cwd="./ml_training")
    
    return result.returncode == 0

def main():
    """Main auto-training logic"""
    print("🔍 Checking for existing ASL model...")
    
    if not check_model_exists():
        print("🚀 No model found - triggering auto-training")
        if trigger_training():
            print("✅ Auto-training completed successfully!")
            return True
        else:
            print("❌ Auto-training failed")
            return False
    else:
        print("✅ Model already exists - skipping training")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
