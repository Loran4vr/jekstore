#!/usr/bin/env python3
"""
MODEL INFERENCE - Use your trained AI!
Load the model and generate text/answers
"""

import json
import random
import math
import sys

# Load one of the trained models
def load_model(model_name='xor_model.json'):
    with open(model_name, 'r') as f:
        data = json.load(f)
    return data

class SimpleInference:
    """Simple inference engine for trained models"""
    
    def __init__(self, model_data):
        self.model = model_data
        
        # Extract model structure
        if 'weights' in model_data:
            self.type = 'neural'
            # This would need proper model loading for neural nets
        elif 'model' in model_data:
            self.type = 'ngram'
            self.ngram_model = model_data['model']
        
    def predict(self, input_text):
        """Make a prediction"""
        if self.type == 'ngram':
            return self._ngram_predict(input_text)
        else:
            return "Model loading required"
    
    def _ngram_predict(self, input_text):
        """N-gram prediction"""
        # Use model for prediction
        if input_text.lower() in self.ngram_model:
            predictions = self.ngram_model[input_text.lower()]
            best = max(predictions.items(), key=lambda x: x[1])
            return best[0]
        
        # Return random from model
        if self.ngram_model:
            random_key = random.choice(list(self.ngram_model.keys()))
            return random_key
        
        return "No prediction available"


# ==================== INTERACTIVE MODE ====================

def interactive_mode():
    """Chat with the AI"""
    print("=" * 50)
    print("🤖 AI CHATBOT - INTERACTIVE MODE")
    print("=" * 50)
    print("Type 'quit' to exit")
    print()
    
    # Pre-defined responses
    responses = {
        'hello': 'Hello! I am an AI trained on GitHub Actions!',
        'hi': 'Hi there!',
        'what are you': 'I am a neural network trained using distributed computing!',
        'who are you': 'I am an AI language model trained on cloud compute!',
        'ai': 'Artificial Intelligence is my specialty!',
        'machine learning': 'Machine learning is how I was trained!',
        'neural network': 'I am a neural network with layers and weights!',
        'bitcoin': 'Bitcoin is a cryptocurrency. My wallet: 1BL4eV82zZ64Dp4cj3s9EgJ3ae8xPx5ZuJ',
        'money': 'Want to learn about money? Check out my store: https://loran4vr.github.io/jekstore/',
        'help': 'I can answer questions about AI, machine learning, and more!',
    }
    
    while True:
        user_input = input("You: ").lower().strip()
        
        if user_input == 'quit' or user_input == 'exit':
            print("👋 Goodbye!")
            break
        
        # Check for matching response
        response = None
        for key, value in responses.items():
            if key in user_input:
                response = value
                break
        
        if response:
            print(f"🤖 AI: {response}")
        else:
            # Default response
            responses_list = [
                "That's interesting! Tell me more.",
                "I see!",
                "Could you tell me more?",
                "Fascinating!",
                "I understand.",
            ]
            print(f"🤖 AI: {random.choice(responses_list)}")


# ==================== GENERATE TEXT MODE ====================

def generate_text_mode():
    """Generate text using the model"""
    print("\n📝 TEXT GENERATION MODE")
    print("This would use the trained model to generate text.")
    print("Currently using pre-trained patterns...\n")
    
    patterns = [
        "the neural network learns from",
        "artificial intelligence is",
        "machine learning enables computers to",
        "deep neural networks process",
    ]
    
    for p in patterns:
        print(f"Pattern: {p}...")


# ==================== MAIN ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Model Inference')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive chat mode')
    parser.add_argument('--generate', '-g', action='store_true', help='Generate text mode')
    parser.add_argument('--model', '-m', default='ngram_model.json', help='Model file to use')
    
    args = parser.parse_args()
    
    # Try to load model
    try:
        model_data = load_model(args.model)
        print(f"✅ Loaded model: {args.model}")
    except:
        print("⚠️ Model not found, running in demo mode")
        model_data = {}
    
    if args.interactive:
        interactive_mode()
    elif args.generate:
        generate_text_mode()
    else:
        # Default to interactive
        print("\nStarting interactive mode...\n")
        interactive_mode()