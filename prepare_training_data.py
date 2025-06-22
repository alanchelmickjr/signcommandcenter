#!/usr/bin/env python3
"""
Prepare ASL training dataset for SmolVLM fine-tuning
Berkeley Cal Hacks 2025
"""

import json
import os
import shutil
from datetime import datetime
import base64
from PIL import Image

def create_training_dataset():
    """Create training dataset structure for ASL recognition"""
    print("🗂️  Preparing ASL training dataset...")
    
    # ASL command mappings (from asl_server.py)
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
        'search': 'internet_search',
        'spreadsheet': 'open_spreadsheet'
    }
    
    # Create directory structure
    base_dir = "training_data"
    os.makedirs(f"{base_dir}/asl_signs", exist_ok=True)
    os.makedirs(f"{base_dir}/annotations", exist_ok=True)
    os.makedirs(f"{base_dir}/processed", exist_ok=True)
    
    # Training data metadata
    dataset_info = {
        "name": "ASL Command Center Training Dataset",
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "description": "ASL sign recognition dataset for Berkeley Cal Hacks 2025",
        "classes": list(ASL_COMMANDS.keys()),
        "total_images": 0,
        "annotations_format": "SmolVLM_compatible"
    }
    
    # Create class directories
    for sign_class in ASL_COMMANDS.keys():
        class_dir = f"{base_dir}/asl_signs/{sign_class.replace(' ', '_')}"
        os.makedirs(class_dir, exist_ok=True)
    
    # Save dataset info
    with open(f"{base_dir}/dataset_info.json", 'w') as f:
        json.dump(dataset_info, f, indent=2)
    
    print(f"✅ Training dataset structure created in {base_dir}/")
    print(f"📝 ASL classes prepared: {len(ASL_COMMANDS)}")
    
    return base_dir

def process_collected_data():
    """Process collected ASL recognition data for training"""
    base_dir = "training_data"
    processed_dir = f"{base_dir}/processed"
    
    # Look for collected data
    radata_dir = "radata"
    if not os.path.exists(radata_dir):
        print("⚠️  No collected data found in radata/ directory")
        return
    
    print("🔄 Processing collected ASL data...")
    
    # Process each file in radata
    processed_count = 0
    for filename in os.listdir(radata_dir):
        if filename.endswith('.json'):
            try:
                with open(f"{radata_dir}/{filename}", 'r') as f:
                    data = json.load(f)
                
                # Extract relevant training data
                if 'image_data' in data and 'recognized_text' in data:
                    # Save processed annotation
                    annotation = {
                        "image_file": filename.replace('.json', '.jpg'),
                        "text": data['recognized_text'],
                        "timestamp": data.get('timestamp', ''),
                        "confidence": data.get('confidence', 'unknown'),
                        "source": "asl_collection"
                    }
                    
                    # Save to processed directory
                    output_file = f"{processed_dir}/{filename}"
                    with open(output_file, 'w') as f:
                        json.dump(annotation, f, indent=2)
                    
                    processed_count += 1
                    
            except Exception as e:
                print(f"⚠️  Error processing {filename}: {e}")
    
    print(f"✅ Processed {processed_count} training samples")

def create_training_script():
    """Create a script for SmolVLM fine-tuning"""
    script_content = '''#!/usr/bin/env python3
"""
SmolVLM Fine-tuning Script for ASL Recognition
Berkeley Cal Hacks 2025
"""

import json
import os
from transformers import AutoProcessor, AutoTokenizer, TrainingArguments, Trainer
import torch
from torch.utils.data import Dataset
from PIL import Image

class ASLDataset(Dataset):
    def __init__(self, data_dir, processor):
        self.data_dir = data_dir
        self.processor = processor
        self.annotations = []
        
        # Load annotations
        annotations_dir = f"{data_dir}/annotations"
        for filename in os.listdir(annotations_dir):
            if filename.endswith('.json'):
                with open(f"{annotations_dir}/{filename}", 'r') as f:
                    self.annotations.append(json.load(f))
    
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        annotation = self.annotations[idx]
        
        # Load image
        image_path = f"{self.data_dir}/asl_signs/{annotation['image_file']}"
        if os.path.exists(image_path):
            image = Image.open(image_path)
        else:
            # Create dummy image if file not found
            image = Image.new('RGB', (224, 224), color='white')
        
        # Process with SmolVLM processor
        text = f"This is an ASL sign for: {annotation['text']}"
        inputs = self.processor(images=image, text=text, return_tensors="pt")
        
        return {
            'pixel_values': inputs['pixel_values'].squeeze(),
            'input_ids': inputs['input_ids'].squeeze(),
            'labels': inputs['input_ids'].squeeze()
        }

def train_asl_model():
    """Train SmolVLM for ASL recognition"""
    print("🚀 Starting ASL model training...")
    
    # Load processor and model
    model_name = "HuggingFaceTB/SmolVLM-500M-Instruct"
    processor = AutoProcessor.from_pretrained(model_name)
    
    # Create dataset
    dataset = ASLDataset("training_data", processor)
    print(f"📊 Training dataset size: {len(dataset)}")
    
    if len(dataset) == 0:
        print("❌ No training data found. Please collect ASL data first.")
        return
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./asl_model_checkpoints",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        save_steps=500,
        save_total_limit=2,
        logging_steps=100,
        learning_rate=5e-5,
        warmup_steps=100,
    )
    
    print("✅ Training configuration ready")
    print("💡 Run this script after collecting sufficient ASL training data")
    print("📈 Recommended: 50+ examples per ASL sign class")

if __name__ == "__main__":
    train_asl_model()
'''
    
    with open("ml_training/train_asl_model.py", 'w') as f:
        f.write(script_content)
    
    print("✅ Training script created: ml_training/train_asl_model.py")

def main():
    """Main function to prepare training infrastructure"""
    print("🎯 ASL Command Center - Training Data Preparation")
    print("================================================")
    
    # Create training dataset structure
    base_dir = create_training_dataset()
    
    # Process any existing collected data
    process_collected_data()
    
    # Create training script
    os.makedirs("ml_training", exist_ok=True)
    create_training_script()
    
    print("")
    print("🎓 Training Infrastructure Ready!")
    print("================================")
    print("")
    print("📁 Training data will be collected to:")
    print(f"   📸 Images: {base_dir}/asl_signs/")
    print(f"   📝 Annotations: {base_dir}/annotations/")
    print(f"   🔄 Processed: {base_dir}/processed/")
    print("")
    print("🚀 Next Steps:")
    print("   1. Start the ASL system and collect data")
    print("   2. Use the web interface to perform ASL signs")
    print("   3. Data will be automatically logged")
    print("   4. Run training when you have 50+ examples per sign")
    print("")
    print("💡 Training Command:")
    print("   python ml_training/train_asl_model.py")

if __name__ == "__main__":
    main()
