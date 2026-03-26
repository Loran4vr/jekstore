#!/usr/bin/env python3
"""
Working Transformer LLM - Simplified but Functional
Implements the core transformer architecture
"""

import math
import random
import json

random.seed(42)

# ==================== UTILITIES ====================

def softmax(x):
    max_x = max(x)
    exp_x = [math.exp(i - max_x) for i in x]
    return [i / sum(exp_x) for i in exp_x]


class Tokenizer:
    """Simple tokenizer"""
    
    def __init__(self):
        self.tok_to_idx = {'<PAD>': 0, '<UNK>': 1, '<BOS>': 2, '<EOS>': 3}
        self.idx_to_tok = {0: '<PAD>', 1: '<UNK>', 2: '<BOS>', 3: '<EOS>'}
        self.vocab_size = 4
    
    def train(self, text):
        for c in set(text):
            if c not in self.tok_to_idx:
                self.tok_to_idx[c] = self.vocab_size
                self.idx_to_tok[self.vocab_size] = c
                self.vocab_size += 1
        return self
    
    def encode(self, text, add_bos=False, add_eos=False):
        tokens = []
        if add_bos: tokens.append(2)
        for c in text:
            tokens.append(self.tok_to_idx.get(c, 1))
        if add_eos: tokens.append(3)
        return tokens
    
    def decode(self, ids):
        return ''.join([self.idx_to_tok.get(i, '?') for i in ids])


class SimpleTransformer:
    """Simplified transformer for text generation"""
    
    def __init__(self, vocab_size, d_model=64, n_layers=2, n_heads=2):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_layers = n_layers
        
        # Embeddings
        self.token_emb = [[random.gauss(0, 0.1) for _ in range(d_model)] 
                         for _ in range(vocab_size)]
        
        # Positional encoding
        self.pos_enc = [[math.sin(pos / 10000 ** (2*i/d_model)) if i % 2 == 0 
                        else math.cos(pos / 10000 ** (2*i/d_model)) 
                        for i in range(d_model)] for pos in range(128)]
        
        # Transformer layers: simplified attention + FFN
        # We use a single weight matrix for Q,K,V
        self.W_qkv = [[[random.gauss(0, 0.1) for _ in range(d_model)] 
                      for _ in range(d_model)] for _ in range(n_layers)]
        self.W_out = [[[random.gauss(0, 0.1) for _ in range(d_model)] 
                     for _ in range(d_model)] for _ in range(n_layers)]
        
        # Feed-forward
        self.W_ff = [[[random.gauss(0, 0.1) for _ in range(d_model*4)] 
                    for _ in range(d_model)] for _ in range(n_layers)]
        self.W_ff_out = [[[random.gauss(0, 0.1) for _ in range(d_model)] 
                         for _ in range(d_model*4)] for _ in range(n_layers)]
        
        # Output
        self.W_final = [[random.gauss(0, 0.1) for _ in range(vocab_size)] 
                       for _ in range(d_model)]
        
        print(f"🤖 Transformer: vocab={vocab_size}, d_model={d_model}, layers={n_layers}")
    
    def forward(self, tokens, layer_idx=0):
        """Simplified forward pass"""
        seq_len = len(tokens)
        
        # Embeddings + positional
        x = []
        for i, tok in enumerate(tokens):
            emb = self.token_emb[tok]
            pos = self.pos_enc[i]
            x.append([emb[j] + pos[j] for j in range(self.d_model)])
        
        # Apply transformer layers
        for li in range(self.n_layers):
            # Simplified self-attention
            # Project to Q, K, V
            Q = [[sum(x[i][j] * self.W_qkv[li][j][k] for j in range(self.d_model)) 
                  for k in range(self.d_model)] for i in range(seq_len)]
            K = Q  # Simplified: Q=K=V
            V = Q
            
            # Attention scores
            scores = [[sum(Q[i][j] * K[j][k] for j in range(self.d_model)) / math.sqrt(self.d_model) 
                      for k in range(seq_len)] for i in range(seq_len)]
            
            # Causal mask
            for i in range(seq_len):
                for j in range(seq_len):
                    if j > i:
                        scores[i][j] = -1e9
            
            # Softmax
            attn = []
            for i in range(seq_len):
                row = softmax(scores[i])
                # Apply to values
                out = [0] * self.d_model
                for k in range(seq_len):
                    for j in range(self.d_model):
                        out[j] += row[k] * V[k][j]
                attn.append(out)
            
            # Residual + output projection
            x = [[x[i][j] + attn[i][j] for j in range(self.d_model)] for i in range(seq_len)]
            x = [[sum(x[i][j] * self.W_out[li][j][k] for j in range(self.d_model)) 
                  for k in range(self.d_model)] for i in range(seq_len)]
            
            # Feed-forward
            ff = []
            for xi in x:
                h = [sum(xi[j] * self.W_ff[li][j][k] for j in range(self.d_model)) 
                     for k in range(self.d_model*4)]
                h = [max(0, h[k]) for k in range(self.d_model*4)]  # ReLU
                out = [sum(h[j] * self.W_ff_out[li][j][k] for j in range(self.d_model*4)) 
                       for k in range(self.d_model)]
                ff.append(out)
            
            # Residual
            x = [[x[i][j] + ff[i][j] for j in range(self.d_model)] for i in range(seq_len)]
        
        # Output projection
        logits = [[sum(x[i][j] * self.W_final[j][k] for j in range(self.d_model)) 
                   for k in range(self.vocab_size)] for i in range(seq_len)]
        
        return logits
    
    def generate(self, tokens, max_new=30):
        """Generate new tokens"""
        for _ in range(max_new):
            if len(tokens) > 64:  # Max context
                tokens = tokens[-64:]
            
            logits = self.forward(tokens)
            next_token_logits = logits[-1]
            
            probs = softmax(next_token_logits)
            token = random.choices(range(self.vocab_size), weights=probs)[0]
            
            tokens.append(token)
            
            if token == 3:  # <EOS>
                break
        
        return tokens
    
    def train(self, inputs, targets, lr=0.001):
        """Simplified training step"""
        logits = self.forward(inputs)
        
        # Cross-entropy loss
        loss = 0
        for i, target in enumerate(targets):
            probs = softmax(logits[i])
            loss -= math.log(max(probs[target], 1e-10))
        
        # Very simplified weight update - only update output layer
        for i, target in enumerate(targets):
            probs = softmax(logits[i])
            for j in range(self.d_model):
                # Gradient approximation
                error = (probs[target] - 1.0) * lr
                self.W_final[j][target] += error * inputs[i][j] if i < len(inputs) else 0
        
        return loss / len(targets)


# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 WORKING TRANSFORMER LLM")
    print("=" * 50)
    
    # Training text
    text = """hello world artificial intelligence machine learning neural networks 
    deep learning transformer models generate text tokens embeddings attention 
    softmax cross entropy backpropagation gradient descent optimization weights 
    biases forward pass loss function vocabulary tokenization sequence batch 
    epoch iteration learning rate patience early stopping overfitting dropout 
    layer normalization residual connection scaled dot product query key value 
    feed forward layer position encoding masked attention causal language model 
    text generation sentence completion autocomplete prediction probability 
    distribution sampling temperature top k nucleus sampling greedy beam search"""
    
    # Tokenize
    tokenizer = Tokenizer()
    tokenizer.train(text)
    print(f"📝 Vocab: {tokenizer.vocab_size}")
    
    # Model
    model = SimpleTransformer(tokenizer.vocab_size, d_model=32, n_layers=2)
    
    # Prepare data
    tokens = tokenizer.encode(text, add_bos=True, add_eos=True)
    seq_len = 16
    data = [(tokens[i:i+seq_len], tokens[i+1:i+seq_len+1]) 
            for i in range(0, len(tokens)-seq_len, 2)]
    print(f"📊 Training sequences: {len(data)}")
    
    # Train
    print("\n🔄 Training...")
    for epoch in range(10):
        loss = 0
        for inp, tgt in data:
            l = model.train(inp, tgt, lr=0.01)
            loss += l
        print(f"   Epoch {epoch+1}: loss={loss/len(data):.4f}")
    
    # Generate
    print("\n🎨 Generating...")
    seed = tokenizer.encode("hello")
    result = model.generate(seed, max_new=40)
    output = tokenizer.decode(result)
    print(f"   Input: hello")
    print(f"   Output: {output}")
    
    # Save
    with open('transformer_vocab.json', 'w') as f:
        json.dump({
            'vocab_size': tokenizer.vocab_size,
            'idx_to_tok': tokenizer.idx_to_tok,
            'tok_to_idx': tokenizer.tok_to_idx
        }, f)
    
    print("\n✅ Done!")