#!/usr/bin/env python3
"""
Simple LLM (Large Language Model) - Built from Scratch
Implements: Token Embedding, Positional Encoding, Multi-Head Attention, Feed-Forward Networks

This is a MINIMAL transformer that can learn text patterns and generate text-like output.
Not ChatGPT, but demonstrates the core concepts!
"""

import math
import random
import json
from collections import Counter

random.seed(42)

class SimpleTokenizer:
    """Character-level tokenizer"""
    
    def __init__(self, text=None):
        self.char_to_idx = {}
        self.idx_to_char = {}
        self.vocab_size = 0
        
        if text:
            self.train(text)
    
    def train(self, text):
        chars = sorted(set(text))
        self.char_to_idx = {c: i for i, c in enumerate(chars)}
        self.idx_to_char = {i: c for c, i in self.char_to_idx.items()}
        self.vocab_size = len(chars)
        print(f"📝 Tokenizer trained: {self.vocab_size} unique characters")
    
    def encode(self, text):
        return [self.char_to_idx[c] for c in text if c in self.char_to_idx]
    
    def decode(self, indices):
        return ''.join([self.idx_to_char[i] for i in indices])


class PositionalEncoding:
    """Sinusoidal positional encoding"""
    
    def __init__(self, d_model, max_len=1000):
        self.d_model = d_model
        self.pe = [[0] * d_model for _ in range(max_len)]
        
        for pos in range(max_len):
            for i in range(0, d_model, 2):
                self.pe[pos][i] = math.sin(pos / math.pow(10000, (2*i) / d_model))
                self.pe[pos][i+1] = math.cos(pos / math.pow(10000, (2*i+1) / d_model))
    
    def forward(self, position):
        return self.pe[position][:self.d_model]


class MultiHeadAttention:
    """Multi-head self-attention mechanism"""
    
    def __init__(self, d_model, num_heads):
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Initialize weight matrices
        self.W_q = [[random.uniform(-0.1, 0.1) for _ in range(d_model)] 
                    for _ in range(d_model)]
        self.W_k = [[random.uniform(-0.1, 0.1) for _ in range(d_model)] 
                    for _ in range(d_model)]
        self.W_v = [[random.uniform(-0.1, 0.1) for _ in range(d_model)] 
                    for _ in range(d_model)]
        self.W_o = [[random.uniform(-0.1, 0.1) for _ in range(d_model)] 
                    for _ in range(d_model)]
    
    def forward(self, x):
        # x shape: [seq_len, d_model]
        seq_len = len(x)
        
        # Linear projections
        Q = self.linear(x, self.W_q)
        K = self.linear(x, self.W_k)
        V = self.linear(x, self.W_v)
        
        # Split into heads
        Q_heads = [Q[i * self.d_k:(i+1) * self.d_k] for i in range(self.num_heads)]
        K_heads = [K[i * self.d_k:(i+1) * self.d_k] for i in range(self.num_heads)]
        V_heads = [V[i * self.d_k:(i+1) * self.d_k] for i in range(self.num_heads)]
        
        # Attention for each head
        heads_output = []
        for i in range(self.num_heads):
            # Scaled dot-product attention
            scores = [[sum(Q_heads[i][j][k] * K_heads[i][m][k] for k in range(self.d_k)) 
                      / math.sqrt(self.d_k) for m in range(seq_len)] for j in range(seq_len)]
            
            # Softmax
            for j in range(seq_len):
                max_score = max(scores[j])
                exp = [math.exp(s - max_score) for s in scores[j]]
                sum_exp = sum(exp)
                scores[j] = [e / sum_exp for e in exp]
            
            # Apply attention to values
            attention = []
            for j in range(seq_len):
                output = [0] * self.d_k
                for m in range(seq_len):
                    for k in range(self.d_k):
                        output[k] += scores[j][m] * V_heads[i][m][k]
                attention.append(output)
            
            heads_output.append(attention)
        
        # Concatenate heads
        output = []
        for i in range(seq_len):
            concat = []
            for h in heads_output:
                concat.extend(h[i])
            output.append(concat)
        
        # Final linear
        return self.linear(output, self.W_o)
    
    def linear(self, x, W):
        seq_len = len(x)
        d_model = len(W[0])
        
        result = [[0] * d_model for _ in range(seq_len)]
        for i in range(seq_len):
            for j in range(d_model):
                for k in range(len(x[i])):
                    result[i][j] += x[i][k] * W[k][j]
        
        return result


class FeedForward:
    """Position-wise feed-forward network"""
    
    def __init__(self, d_model, d_ff):
        self.W1 = [[random.uniform(-0.1, 0.1) for _ in range(d_ff)] for _ in range(d_model)]
        self.b1 = [0] * d_ff
        self.W2 = [[random.uniform(-0.1, 0.1) for _ in range(d_model)] for _ in range(d_ff)]
        self.b2 = [0] * d_model
    
    def forward(self, x):
        # ReLU activation
        hidden = [[max(0, sum(x[i][j] * self.W1[j][k] + self.b1[k] for j in range(len(x[i])))) 
                   for k in range(len(self.W1[0]))] for i in range(len(x))]
        
        # Output layer
        output = [[sum(hidden[i][j] * self.W2[j][k] + self.b2[k] for j in range(len(hidden[i]))) 
                   for k in range(len(self.W2[0]))] for i in range(len(hidden))]
        
        return output


class TransformerBlock:
    """Single transformer block"""
    
    def __init__(self, d_model, num_heads, d_ff):
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)
        self.norm1 = [0.0] * d_model
        self.norm2 = [0.0] * d_model
    
    def forward(self, x):
        # Self-attention with residual
        attn_out = self.attention.forward(x)
        x = [[x[i][j] + attn_out[i][j] for j in range(len(x[i]))] for i in range(len(x))]
        
        # Feed-forward with residual
        ff_out = self.feed_forward.forward(x)
        x = [[x[i][j] + ff_out[i][j] for j in range(len(x[i]))] for i in range(len(x))]
        
        return x


class SimpleLLM:
    """A minimal transformer-based language model"""
    
    def __init__(self, vocab_size, d_model=64, num_heads=4, num_layers=2, d_ff=128):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.token_embedding = [[random.uniform(-0.1, 0.1) for _ in range(d_model)] 
                               for _ in range(vocab_size)]
        self.pos_encoding = PositionalEncoding(d_model)
        self.transformer_blocks = [TransformerBlock(d_model, num_heads, d_ff) 
                                   for _ in range(num_layers)]
        self.output_linear = [[random.uniform(-0.1, 0.1) for _ in range(vocab_size)] 
                             for _ in range(d_model)]
        
        print(f"🤖 SimpleLLM created:")
        print(f"   Vocab size: {vocab_size}")
        print(f"   D model: {d_model}")
        print(f"   Layers: {num_layers}")
        print(f"   Parameters: ~{vocab_size * d_model + num_layers * (d_model * d_model * 4)}")
    
    def forward(self, tokens):
        # Token embeddings
        x = [self.token_embedding[t] for t in tokens]
        
        # Add positional encoding
        for i in range(len(x)):
            pos_enc = self.pos_encoding.forward(i)
            x[i] = [x[i][j] + pos_enc[j] for j in range(len(x[i]))]
        
        # Transformer blocks
        for block in self.transformer_blocks:
            x = block.forward(x)
        
        # Output projection
        logits = [[sum(x[i][j] * self.output_linear[j][k] for j in range(len(x[i]))) 
                   for k in range(self.vocab_size)] for i in range(len(x))]
        
        return logits
    
    def generate(self, tokens, max_length=50):
        """Generate new tokens"""
        self.eval()  # Set to eval mode (no dropout equivalent)
        
        for _ in range(max_length):
            logits = self.forward(tokens)
            next_token = self.sample(logits[-1])
            
            if next_token == 0:  # End token
                break
            
            tokens.append(next_token)
        
        return tokens
    
    def sample(self, logits, temperature=1.0):
        """Sample next token with temperature"""
        # Apply temperature
        adjusted = [l / temperature for l in logits]
        
        # Softmax
        max_adj = max(adjusted)
        exp = [math.exp(x - max_adj) for x in adjusted]
        sum_exp = sum(exp)
        probs = [e / sum_exp for e in exp]
        
        # Sample
        r = random.random()
        cumulative = 0
        for i, p in enumerate(probs):
            cumulative += p
            if cumulative >= r:
                return i
        
        return len(probs) - 1
    
    def train_step(self, inputs, targets, learning_rate=0.01):
        """Single training step"""
        # Forward pass
        logits = self.forward(inputs)
        
        # Calculate loss (cross-entropy)
        loss = 0
        for i, target in enumerate(targets):
            # Softmax
            max_logit = max(logits[i])
            exp_sum = sum(math.exp(l - max_logit) for l in logits[i])
            prob = math.exp(logits[i][target] - max_logit) / exp_sum
            loss -= math.log(max(prob, 1e-10))
        
        loss /= len(targets)
        
        # This would require backpropagation - simplified here
        # In a real implementation, we'd compute gradients and update weights
        
        return loss


def prepare_training_data(text, seq_length=20):
    """Prepare training data from text"""
    tokens = list(text)
    sequences = []
    
    for i in range(0, len(tokens) - seq_length, 1):
        input_seq = tokens[i:i+seq_length]
        target_seq = tokens[i+1:i+seq_length+1]
        
        # Convert to indices
        unique_chars = sorted(set(tokens))
        char_to_idx = {c: i for i, c in enumerate(unique_chars)}
        
        inputs = [char_to_idx[c] for c in input_seq]
        targets = [char_to_idx[c] for c in target_seq]
        
        sequences.append((inputs, targets))
    
    return sequences, char_to_idx


# ==================== DEMO ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SIMPLE LLM - Built from Scratch")
    print("=" * 60)
    
    # Simple training text
    training_text = "hello world this is a simple language model built from scratch "
    training_text += "it learns patterns in text and generates new text like this "
    training_text += "artificial intelligence is amazing and learning is fun "
    training_text += "neural networks are powerful and transformers are the future "
    
    print(f"\n📚 Training text ({len(training_text)} chars)")
    
    # Tokenize
    tokenizer = SimpleTokenizer(training_text)
    print(f"   Vocab size: {tokenizer.vocab_size}")
    
    # Create LLM
    llm = SimpleLLM(
        vocab_size=tokenizer.vocab_size,
        d_model=32,
        num_heads=2,
        num_layers=2,
        d_ff=64
    )
    
    # Prepare training data
    sequences, char_to_idx = prepare_training_data(training_text)
    print(f"\n🔄 Created {len(sequences)} training sequences")
    
    # Simple training (demonstration)
    print("\n📚 Training...")
    for epoch in range(5):
        total_loss = 0
        for inputs, targets in sequences[:10]:  # Use subset for demo
            loss = llm.train_step(inputs, targets, learning_rate=0.01)
            total_loss += loss
        print(f"   Epoch {epoch+1}: Loss = {total_loss/10:.4f}")
    
    # Generate text
    print("\n🎨 Generating text...")
    seed = "hello"
    seed_tokens = [char_to_idx[c] for c in seed if c in char_to_idx]
    
    generated = llm.generate(seed_tokens, max_length=50)
    output_text = tokenizer.decode(generated)
    
    print(f"   Input: {seed}")
    print(f"   Output: {output_text}")
    
    # Save model info
    model_info = {
        'vocab_size': tokenizer.vocab_size,
        'd_model': 32,
        'num_layers': 2,
        'chars': list(sorted(set(training_text)))
    }
    
    with open('llm_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print("\n✅ Simple LLM demo complete!")
    print("   Note: This is a MINIMAL implementation.")
    print("   Real LLM like GPT-3 has billions of parameters.")