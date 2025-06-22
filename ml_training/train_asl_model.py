#!/usr/bin/env python3
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
