#!/usr/bin/env python3
"""
EFFICIENT SCALED LANGUAGE MODEL
Optimized for CPU - can actually train and generate
"""

import random
import math
import json

random.seed(42)

# Simple but functional
class FastLM:
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=128):
        self.vocab = vocab_size
        
        # Embedding
        self.embed = [[random.gauss(0, 0.2) for _ in range(embed_dim)] for _ in range(vocab_size)]
        
        # Hidden weights
        self.W1 = [[random.gauss(0, 0.2) for _ in range(hidden_dim)] for _ in range(embed_dim)]
        self.b1 = [0.0] * hidden_dim
        
        # Output
        self.W2 = [[random.gauss(0, 0.2) for _ in range(vocab_size)] for _ in range(hidden_dim)]
        self.b2 = [0.0] * vocab_size
        
        print(f"🤖 FastLM: {vocab_size} vocab, {embed_dim} emb, {hidden_dim} hidden")
        print(f"   Params: ~{vocab_size*embed_dim + embed_dim*hidden_dim + hidden_dim*vocab_size:,}")
    
    def forward(self, tokens):
        # Embed
        emb = [self.embed[t] for t in tokens]
        avg = [sum(e)/len(emb) for e in zip(*emb)] if emb else [0]*len(self.embed[0])
        
        # Hidden (ReLU)
        h = [max(0, sum(avg[i] * self.W1[i][j] for i in range(len(avg))) + self.b1[j]) 
             for j in range(len(self.b1))]
        
        # Output
        out = [sum(h[i] * self.W2[i][j] for i in range(len(h))) + self.b2[j] 
               for j in range(self.vocab)]
        
        return out, h
    
    def train(self, x, y, lr=0.1):
        out, h = self.forward(x)
        probs = softmax(out)
        
        loss = -math.log(max(probs[y], 1e-10))
        
        # Update output layer (simplified)
        for j in range(self.vocab):
            err = (probs[j] - (1 if j == y else 0)) * lr
            for i in range(len(h)):
                self.W2[i][j] -= err * h[i] * 0.1
            self.b2[j] -= err * 0.1
        
        return loss
    
    def generate(self, seed, n=20):
        for _ in range(n):
            out, _ = self.forward(seed)
            probs = softmax(out)
            t = random.choices(range(self.vocab), weights=probs)[0]
            seed.append(t)
        return seed


def softmax(x):
    m = max(x)
    e = [math.exp(i - m) for i in x]
    s = sum(e)
    return [i/s for i in e]


# ==================== DATA ====================

# Larger corpus
TEXTS = """
the quick brown fox jumps over the lazy dog
artificial intelligence is transforming the world
machine learning enables computers to learn from data
neural networks are inspired by the human brain
deep learning uses multiple layers of abstraction
transformers revolutionized natural language processing
computer vision allows machines to understand images
robotics combines mechanics electronics and ai
the internet connects billions of devices worldwide
smartphones have become essential in daily life
cloud computing provides scalable resources on demand
blockchain creates secure decentralized records
quantum computing offers exponential speedups
the sun is the center of our solar system
earth orbits around the sun in one year
water freezes at zero degrees celsius
light travels faster than sound
mount everest is the highest mountain on earth
the ocean contains most of earths water
neurons transmit information very quickly
learning new languages improves brain function
reading expands knowledge and vocabulary
exercise promotes physical and mental health
music has therapeutic effects on people
art expresses human creativity and emotion
knowledge is power in modern society
innovation drives technological progress
collaboration leads to better outcomes
practice makes perfect in any skill
curiosity fuels scientific discovery
the universe contains billions of galaxies
black holes have strong gravitational pull
stars form from clouds of gas and dust
mars is known as the red planet
saturn has beautiful ring systems
the moon orbits around the earth
gravity keeps planets in orbit around stars
energy cannot be created or destroyed
matter is made of atoms and molecules
dna carries genetic information in cells
evolution explains how species change over time
climate change affects the entire planet
renewable energy sources are becoming more common
automation is transforming the workplace
virtual reality creates immersive experiences
augmented reality overlays digital on physical
the printing press revolutionized information
the telephone connected people across distances
the airplane enabled global travel
space exploration expands human knowledge
artificial general intelligence remains a goal
explainable ai helps us understand model decisions
ethical ai considers fairness and transparency
data science extracts insights from large datasets
software engineering builds functional systems
the scientific method tests hypotheses rigorously
hypothesis leads to experimentation and analysis
conclusion summarizes findings and implications
""".strip().split('\n')

# Build vocab
print("🔤 Building vocabulary...")
all_words = []
for t in TEXTS:
    all_words.extend(t.lower().split())

unique_words = list(set(all_words))
word_to_idx = {w: i+4 for i, w in enumerate(unique_words)}
word_to_idx['<PAD>'] = 0
word_to_idx['<UNK>'] = 1
word_to_idx['<BOS>'] = 2
word_to_idx['<EOS>'] = 3
idx_to_word = {v: k for k, v in word_to_idx.items()}

vocab_size = len(word_to_idx)
print(f"   Vocab: {vocab_size} words")

# Create model
print("\n🏗️ Creating model...")
model = FastLM(vocab_size, embed_dim=64, hidden_dim=128)

# Training pairs
print("\n📝 Preparing training data...")
pairs = []
for text in TEXTS:
    words = text.lower().split()
    ids = [word_to_idx.get(w, 1) for w in words]
    for i in range(1, len(ids)):
        pairs.append((ids[:i], ids[i]))

print(f"   Pairs: {len(pairs)}")

# Train
print("\n🔄 Training...")
for epoch in range(15):
    total_loss = 0
    random.shuffle(pairs)
    for x, y in pairs:
        loss = model.train(x, y, lr=0.1)
        total_loss += loss
    print(f"   Epoch {epoch+1}: loss={total_loss/len(pairs):.4f}")

# Generate
print("\n🎨 Generating...")
prompts = ["artificial", "machine", "neural", "the sun", "learning"]
for p in prompts:
    seed = [word_to_idx.get(w, 1) for w in p.split()]
    result = model.generate(seed, 15)
    words = [idx_to_word.get(i, '?') for i in result]
    print(f"   {p} → {' '.join(words)}")

# Save
with open('fast_lm.json', 'w') as f:
    json.dump({'vocab': word_to_idx, 'inv': idx_to_word}, f)

print("\n✅ Done!")
print(f"   Total params: ~{vocab_size*64 + 64*128 + 128*vocab_size:,}")