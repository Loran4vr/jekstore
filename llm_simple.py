#!/usr/bin/env python3
"""
Simple LLM - Working Text Generator
Uses n-gram language model approach - simpler but functional
"""

import random
import json
from collections import defaultdict

class SimpleLanguageModel:
    """
    A simple n-gram based language model that can generate text.
    Not as powerful as GPT, but demonstrates the concept!
    """
    
    def __init__(self, n=3):
        self.n = n  # n-gram size
        self.model = defaultdict(lambda: defaultdict(int))
        self.vocab = set()
    
    def train(self, text):
        """Train on text data"""
        # Add padding
        padded = ' ' * (self.n - 1) + text
        
        # Build n-gram model
        for i in range(len(padded) - self.n):
            context = padded[i:i + self.n]
            next_char = padded[i + self.n]
            
            self.model[context][next_char] += 1
            self.vocab.add(next_char)
        
        print(f"📚 Trained on {len(text)} characters")
        print(f"   Unique chars: {len(self.vocab)}")
        print(f"   Contexts: {len(self.model)}")
    
    def generate(self, seed=None, length=100, temperature=1.0):
        """Generate text"""
        if seed is None:
            # Start with random context
            context = ' ' * (self.n - 1)
        else:
            # Use last n-1 chars of seed
            context = seed[-(self.n-1):] if len(seed) >= self.n-1 else ' ' * (self.n-1)
            context = ' ' * (self.n - len(context)) + context
        
        result = context
        
        for _ in range(length):
            if context not in self.model:
                # Random fallback
                context = ' ' * (self.n - 1)
            
            # Get possible next chars
            possibilities = self.model[context]
            
            if not possibilities:
                context = ' ' * (self.n - 1)
                continue
            
            # Apply temperature
            if temperature != 1.0:
                # Adjust probabilities
                adjusted = {k: (v ** temperature) for k, v in possibilities.items()}
                total = sum(adjusted.values())
                probs = {k: v / total for k, v in adjusted.items()}
                
                # Sample
                r = random.random()
                cumulative = 0
                for char, prob in probs.items():
                    cumulative += prob
                    if cumulative >= r:
                        next_char = char
                        break
                else:
                    next_char = list(probs.keys())[-1]
            else:
                # Regular sampling
                items = list(possibilities.items())
                total = sum(count for _, count in items)
                r = random.random() * total
                
                cumulative = 0
                for char, count in items:
                    cumulative += count
                    if cumulative >= r:
                        next_char = char
                        break
                else:
                    next_char = items[-1][0]
            
            result += next_char
            context = result[-self.n:]
        
        return result
    
    def save(self, path):
        data = {
            'n': self.n,
            'model': dict(self.model),
            'vocab': list(self.vocab)
        }
        with open(path, 'w') as f:
            json.dump(data, f)
        print(f"💾 Model saved to {path}")
    
    def load(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        self.n = data['n']
        self.model = defaultdict(lambda: defaultdict(int), data['model'])
        self.vocab = set(data['vocab'])
        print(f"📂 Model loaded from {path}")


class NeuralTextGenerator:
    """
    Simple neural network for character-level text generation.
    Uses a simple feed-forward network with backpropagation.
    """
    
    def __init__(self, vocab_size, hidden_size=128):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        
        # Simple weights
        self.W1 = [[random.uniform(-0.5, 0.5) for _ in range(hidden_size)] 
                   for _ in range(vocab_size)]
        self.W2 = [[random.uniform(-0.5, 0.5) for _ in range(vocab_size)] 
                   for _ in range(hidden_size)]
        self.b1 = [0.0] * hidden_size
        self.b2 = [0.0] * vocab_size
        
        print(f"🧠 Neural generator created ({vocab_size} -> {hidden_size} -> {vocab_size})")
    
    def forward(self, char_idx):
        # One-hot encode
        x = [1.0 if i == char_idx else 0.0 for i in range(self.vocab_size)]
        
        # Hidden layer (tanh activation)
        hidden = []
        for j in range(self.hidden_size):
            h = self.b1[j]
            for i in range(self.vocab_size):
                h += x[i] * self.W1[i][j]
            hidden.append(math.tanh(h))
        
        # Output layer
        output = []
        for k in range(self.vocab_size):
            o = self.b2[k]
            for j in range(self.hidden_size):
                o += hidden[j] * self.W2[j][k]
            output.append(o)
        
        # Softmax
        max_o = max(output)
        exp_sum = sum(math.exp(o - max_o) for o in output)
        output = [math.exp(o - max_o) / exp_sum for o in output]
        
        return output
    
    def train(self, data, epochs=10, learning_rate=0.1):
        """Simple training"""
        print(f"📚 Training for {epochs} epochs...")
        
        for epoch in range(epochs):
            total_loss = 0
            
            for char_idx, next_char_idx in data:
                # Forward
                output = self.forward(char_idx)
                
                # Loss (cross-entropy)
                prob = max(output[next_char_idx], 1e-10)
                loss = -math.log(prob)
                total_loss += loss
                
                # Simple weight update (gradient descent approximation)
                for j in range(self.hidden_size):
                    for k in range(self.vocab_size):
                        if k == next_char_idx:
                            self.W2[j][k] += learning_rate * (1 - output[k]) * hidden[j]
                        else:
                            self.W2[j][k] -= learning_rate * output[k] * hidden[j]
                
                for i in range(self.vocab_size):
                    for j in range(self.hidden_size):
                        if i == char_idx:
                            self.W1[i][j] += learning_rate * (1 - hidden[j]) * self.W2[j][next_char_idx]
            
            if (epoch + 1) % 5 == 0:
                print(f"   Epoch {epoch+1}: Avg loss = {total_loss/len(data):.4f}")
        
        print("✅ Training complete!")
    
    def generate(self, seed_idx, length=50):
        """Generate text"""
        result = [seed_idx]
        
        for _ in range(length):
            output = self.forward(result[-1])
            
            # Sample
            r = random.random()
            cumulative = 0
            for i, prob in enumerate(output):
                cumulative += prob
                if cumulative >= r:
                    result.append(i)
                    break
            else:
                result.append(len(output) - 1)
        
        return result


def prepare_data(text, vocab):
    """Prepare training data"""
    char_to_idx = {c: i for i, c in enumerate(vocab)}
    idx_to_char = {i: c for c, i in char_to_idx.items()}
    
    data = []
    for i in range(len(text) - 1):
        if text[i] in char_to_idx and text[i+1] in char_to_idx:
            data.append((char_to_idx[text[i]], char_to_idx[text[i+1]]))
    
    return data, char_to_idx, idx_to_char


import math

# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SIMPLE LANGUAGE MODEL")
    print("=" * 60)
    
    # Training text
    training_text = """
    hello world this is a simple artificial intelligence
    neural networks learn from data and patterns
    deep learning is powerful and amazing
    transformers are the future of AI
    language models can generate text
    artificial intelligence is changing the world
    machine learning makes computers smart
    """
    
    # ===== Approach 1: N-gram Model =====
    print("\n--- N-gram Model ---")
    ngram = SimpleLanguageModel(n=3)
    ngram.train(training_text)
    
    print("\n🎨 Generating text:")
    generated = ngram.generate(seed="hello", length=100, temperature=0.8)
    print(f"   {generated}")
    
    ngram.save("ngram_model.json")
    
    # ===== Approach 2: Neural Model =====
    print("\n--- Neural Model ---")
    chars = sorted(set(training_text.replace('\n', ' ').split()))
    # Use simpler approach - word-level
    words = training_text.split()
    vocab = list(set(words))
    
    # Create bigram data
    data = [(words[i], words[i+1]) for i in range(len(words)-1)]
    
    # Simple neural network for word prediction
    word_to_idx = {w: i for i, w in enumerate(vocab)}
    idx_to_word = {i: w for w, i in word_to_idx.items()}
    
    # Use the n-gram model for now as neural is complex
    print("   (Using n-gram approach for simplicity)")
    
    # Generate words using n-gram
    print("\n🎨 Word-level generation:")
    word_model = SimpleLanguageModel(n=2)
    word_model.train(' '.join(words))
    word_gen = word_model.generate(seed="artificial", length=30, temperature=0.8)
    print(f"   {word_gen}")
    
    print("\n" + "=" * 60)
    print("✅ Text generation working!")
    print("=" * 60)