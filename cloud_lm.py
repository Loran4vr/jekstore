#!/usr/bin/env python3
"""
CLOUD-READY NEURAL LANGUAGE MODEL
This code is designed to run on free cloud services:
- Google Colab (colab.research.google.com)
- Kaggle Notebooks (kaggle.com)
- Gradient (gradient.run)
- Paperspace Gradient
- FloydHub (floydhub.com)

Instructions for each service included below
"""

# ============================================================
# GOOGLE COLAB INSTRUCTIONS:
# 1. Go to colab.research.google.com
# 2. New Notebook
# 3. Paste this entire code
# 4. Runtime > Change runtime type > GPU
# 5. Run cell
# ============================================================

# ============================================================
# KAGGLE INSTRUCTIONS:
# 1. Go to kaggle.com/notebooks
# 2. New Notebook
# 3. Add this code
# 4. Enable GPU in settings
# 5. Run
# ============================================================

# ============================================================
# GRADIENT INSTRUCTIONS:
# 1. Go to gradient.run
# 2. Create new notebook
# 3. Choose GPU preset
# 4. Paste code
# ============================================================

import math
import random
import json

# Try to detect GPU availability
try:
    import torch
    HAS_TORCH = True
    print(f"🔥 GPU Available: {torch.cuda.is_available()}")
except ImportError:
    HAS_TORCH = False
    print("📌 Running on CPU (install PyTorch for GPU)")

# Set random seeds for reproducibility
random.seed(42)


class TransformerLM:
    """
    Full Transformer Language Model
    Works with PyTorch on GPU, falls back to CPU
    """
    
    def __init__(self, vocab_size, d_model=256, n_heads=8, n_layers=6, 
                 d_ff=1024, dropout=0.1, max_len=512):
        
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_layers = n_layers
        
        if HAS_TORCH:
            # PyTorch version
            import torch
            import torch.nn as nn
            
            self.model = nn.Sequential(
                nn.Embedding(vocab_size, d_model),
                nn.Dropout(dropout),
                *[nn.TransformerEncoderLayer(
                    d_model=d_model, 
                    nhead=n_heads, 
                    dim_feedforward=d_ff,
                    dropout=dropout,
                    batch_first=True
                ) for _ in range(n_layers)],
                nn.Linear(d_model, vocab_size)
            )
            
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)
            self.criterion = nn.CrossEntropyLoss()
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            
            print(f"🤖 PyTorch Transformer: {self.count_params():,} parameters")
        
        else:
            # Pure Python fallback (limited)
            self._init_pure_python(vocab_size, d_model)
        
    def _init_pure_python(self, vocab_size, d_model):
        """Initialize pure Python version"""
        import math
        
        # Token embedding
        scale = math.sqrt(2.0 / d_model)
        self.token_emb = [[random.gauss(0, scale) for _ in range(d_model)] 
                         for _ in range(vocab_size)]
        
        # Positional encoding
        self.pos_enc = [[math.sin(pos / 10000 ** (2*i/d_model)) if i % 2 == 0 
                        else math.cos(pos / 10000 ** (2*i/d_model)) 
                        for i in range(d_model)] for pos in range(512)]
        
        # Simplified transformer layers
        self.W_qkv = [[[random.gauss(0, 0.1) for _ in range(d_model)] 
                      for _ in range(d_model)] for _ in range(self.n_layers)]
        self.W_out = [[[random.gauss(0, 0.1) for _ in range(d_model)] 
                     for _ in range(d_model)] for _ in range(self.n_layers)]
        
        # Output projection
        self.W_final = [[random.gauss(0, 0.1) for _ in range(vocab_size)] 
                       for _ in range(d_model)]
        
        params = vocab_size * d_model + self.n_layers * (d_model * d_model * 2) + d_model * vocab_size
        print(f"🤖 Pure Python Transformer: {params:,} parameters (limited)")
    
    def count_params(self):
        if HAS_TORCH:
            return sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        return 0
    
    def forward(self, x):
        if HAS_TORCH:
            import torch
            with torch.no_grad():
                return self.model(x)
        else:
            # Pure Python forward (simplified)
            return self._python_forward(x)
    
    def _python_forward(self, x):
        seq_len = len(x)
        
        # Embedding + positional
        emb = [self.token_emb[x[i]] if i < len(x) and x[i] < len(self.token_emb) 
               else [0] * self.d_model for i in range(seq_len)]
        
        # Add positional encoding
        for i in range(seq_len):
            emb[i] = [emb[i][j] + self.pos_enc[i][j] for j in range(self.d_model)]
        
        # Simplified transformer (just pass through)
        for layer in range(self.n_layers):
            # Simplified attention
            for i in range(seq_len):
                emb[i] = [emb[i][j] + 0.01 * random.gauss(0, 1) for j in range(self.d_model)]
        
        # Output projection
        logits = [[sum(emb[i][j] * self.W_final[j][k] for j in range(self.d_model)) 
                   for k in range(self.vocab_size)] for i in range(seq_len)]
        
        return logits[-1] if logits else [0] * self.vocab_size
    
    def train_step(self, inputs, targets):
        if HAS_TORCH:
            import torch
            
            self.model.train()
            self.optimizer.zero_grad()
            
            inputs = torch.tensor(inputs, dtype=torch.long)
            targets = torch.tensor(targets, dtype=torch.long)
            
            if torch.cuda.is_available():
                inputs = inputs.cuda()
                targets = targets.cuda()
            
            logits = self.model(inputs)
            loss = self.criterion(logits.view(-1, self.vocab_size), targets)
            
            loss.backward()
            self.optimizer.step()
            
            return loss.item()
        else:
            # Pure Python training (very limited)
            logits = self.forward(inputs)
            probs = softmax(logits)
            loss = -math.log(max(probs[targets[-1]], 1e-10))
            
            # Very simplified gradient update
            for j in range(self.vocab_size):
                if j == targets[-1]:
                    for i in range(self.d_model):
                        self.W_final[i][j] += 0.001 * (1 - probs[j])
            
            return loss
    
    def generate(self, seed, max_length=50, temperature=1.0):
        if HAS_TORCH:
            import torch
            
            self.model.eval()
            generated = list(seed)
            
            for _ in range(max_length):
                input_seq = torch.tensor([generated[-50:]], dtype=torch.long)
                if torch.cuda.is_available():
                    input_seq = input_seq.cuda()
                
                with torch.no_grad():
                    logits = self.model(input_seq)[0, -1]
                    
                    if temperature != 1.0:
                        logits = logits / temperature
                    
                    probs = torch.softmax(logits, dim=0)
                    next_token = torch.multinomial(probs, 1).item()
                
                generated.append(next_token)
                
                if next_token == 3:  # EOS
                    break
            
            return generated
        else:
            # Pure Python generation
            generated = list(seed)
            
            for _ in range(max_length):
                logits = self.forward(generated)
                
                if temperature != 1.0:
                    logits = [l / temperature for l in logits]
                
                probs = softmax(logits)
                next_token = random.choices(range(self.vocab_size), weights=probs)[0]
                
                generated.append(next_token)
                
                if next_token == 3:
                    break
            
            return generated


def softmax(x):
    max_x = max(x)
    exp_x = [math.exp(i - max_x) for i in x]
    return [i / sum(exp_x) for i in exp_x]


# ==================== TOKENIZER ====================

class Tokenizer:
    """Simple character tokenizer"""
    
    def __init__(self):
        self.tok_to_idx = {'<PAD>': 0, '<UNK>': 1, '<BOS>': 2, '<EOS>': 3}
        self.idx_to_tok = {0: '<PAD>', 1: '<UNK>', 2: '<BOS>', 3: '<EOS>'}
        self.vocab_size = 4
    
    def train(self, texts):
        chars = set()
        for text in texts:
            chars.update(text)
        
        for c in sorted(chars):
            self.tok_to_idx[c] = self.vocab_size
            self.idx_to_tok[self.vocab_size] = c
            self.vocab_size += 1
        
        return self
    
    def encode(self, text):
        return [self.tok_to_idx.get(c, 1) for c in text]
    
    def decode(self, ids):
        return ''.join([self.idx_to_tok.get(i, '?') for i in ids])


# ==================== TRAINING DATA ====================

def get_training_data():
    """Large training corpus"""
    texts = [
        # General knowledge
        "the quick brown fox jumps over the lazy dog",
        "artificial intelligence is transforming the world",
        "machine learning enables computers to learn from data",
        "neural networks are inspired by the human brain",
        "deep learning uses multiple layers of neural networks",
        "transformers revolutionized natural language processing",
        
        # Science facts
        "the sun is the center of our solar system",
        "earth orbits around the sun in one year",
        "water freezes at zero degrees celsius",
        "light travels faster than sound",
        "mount everest is the highest mountain on earth",
        
        # Technology
        "the internet connects billions of computers worldwide",
        "smartphones have become essential in daily life",
        "blockchain creates secure decentralized records",
        "quantum computing offers exponential speedups",
        
        # Learning
        "practice makes perfect when learning new skills",
        "knowledge is power in the modern world",
        "curiosity fuels scientific discovery",
        "reading expands knowledge and vocabulary",
        
        # Space
        "the universe contains billions of galaxies",
        "black holes have extremely strong gravity",
        "stars form from clouds of gas and dust",
        "mars is known as the red planet",
        
        # Facts
        "neurons transmit information at high speeds",
        "the ocean contains most of earths water",
        "music has therapeutic effects on people",
        "exercise promotes physical and mental health",
        
        # More AI
        "computer vision allows machines to see",
        "natural language understanding processes text",
        "reinforcement learning trains agents through rewards",
        "generative models create new content",
        "large language models have billions of parameters",
        
        # Additional
        "the printing press revolutionized information spread",
        "the telephone connected people across distances",
        "airplanes enabled global travel in hours",
        "space exploration expands human knowledge",
    ]
    return texts


# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 CLOUD-READY TRANSFORMER LANGUAGE MODEL")
    print("=" * 60)
    
    # Get training data
    print("\n📚 Loading training data...")
    texts = get_training_data()
    print(f"   Texts: {len(texts)}")
    
    # Tokenize
    print("\n🔤 Tokenizing...")
    tokenizer = Tokenizer()
    tokenizer.train(texts)
    print(f"   Vocabulary: {tokenizer.vocab_size}")
    
    # Create model
    print("\n🏗️ Creating model...")
    model = TransformerLM(
        vocab_size=tokenizer.vocab_size,
        d_model=128,
        n_heads=4,
        n_layers=2,
        d_ff=256
    )
    
    # Prepare training data
    print("\n📝 Preparing training sequences...")
    all_tokens = []
    for text in texts:
        tokens = tokenizer.encode(text)
        all_tokens.extend(tokens)
    
    seq_length = 16
    sequences = []
    for i in range(0, len(all_tokens) - seq_length, 1):
        inputs = all_tokens[i:i+seq_length]
        targets = all_tokens[i+1:i+seq_length+1]
        sequences.append((inputs, targets))
    
    print(f"   Sequences: {len(sequences)}")
    
    # Train
    print("\n🔄 Training...")
    batch_size = 16 if HAS_TORCH else 1
    
    for epoch in range(10):
        total_loss = 0
        random.shuffle(sequences)
        
        for i in range(0, len(sequences), batch_size):
            batch = sequences[i:i+batch_size]
            
            for inputs, targets in batch:
                loss = model.train_step(inputs, targets)
                total_loss += loss
        
        if (epoch + 1) % 2 == 0:
            print(f"   Epoch {epoch+1}: Loss = {total_loss/len(sequences):.4f}")
    
    # Generate
    print("\n🎨 Generating text...")
    prompts = ["the quick", "artificial", "machine", "neural"]
    
    for prompt in prompts:
        seed = tokenizer.encode(prompt)
        generated = model.generate(seed, max_length=30)
        output = tokenizer.decode(generated)
        print(f"   {prompt} → {output[:50]}...")
    
    # Save model info
    print("\n💾 Saving model info...")
    model_info = {
        'vocab_size': tokenizer.vocab_size,
        'd_model': 128,
        'n_heads': 4,
        'n_layers': 2,
        'has_torch': HAS_TORCH
    }
    
    with open('cloud_model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print("\n✅ Cloud-ready model created!")
    print("\n📌 TO SCALE UP:")
    print("   1. Copy this code to Google Colab")
    print("   2. Enable GPU runtime")
    print("   3. Increase d_model to 512+")
    print("   4. Add more training data")
    print("   5. Train for more epochs")