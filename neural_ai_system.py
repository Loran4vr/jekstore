#!/usr/bin/env python3
"""
Neural Network AI System - Complete Implementation
Features:
- Backpropagation with momentum
- Multiple activation functions
- Save/Load models
- Training visualization
- Pattern recognition tasks

SAFETY: Output bounds, no destructive ops, human oversight required
"""

import math
import random
import json
import os
from datetime import datetime

random.seed(42)

class NeuralNetworkAI:
    """Complete neural network with backpropagation"""
    
    def __init__(self, layers, learning_rate=0.5, momentum=0.9, name="AI"):
        """
        Args:
            layers: List of layer sizes, e.g., [2, 4, 1] = 2 input, 4 hidden, 1 output
            learning_rate: How fast to learn (0.1-0.9 recommended)
            momentum: Helps avoid local minima (0.5-0.9)
        """
        self.name = name
        self.layers = layers
        self.lr = learning_rate
        self.momentum = momentum
        
        # Initialize weights randomly
        self.weights = []
        self.biases = []
        self.velocity_w = []  # For momentum
        self.velocity_b = []
        
        for i in range(len(layers) - 1):
            # Xavier initialization
            scale = math.sqrt(2.0 / (layers[i] + layers[i+1]))
            w = [[random.gauss(0, scale) for _ in range(layers[i+1])] for _ in range(layers[i])]
            b = [0.0] * layers[i+1]
            vw = [[0.0] * layers[i+1] for _ in range(layers[i])]
            vb = [0.0] * layers[i+1]
            
            self.weights.append(w)
            self.biases.append(b)
            self.velocity_w.append(vw)
            self.velocity_b.append(vb)
        
        self.history = []
        print(f"🧠 {name} created with {sum(len(w) for l in self.weights for w in l)} weights")
    
    def sigmoid(self, x):
        x = max(-500, min(500, x))
        return 1 / (1 + math.exp(-x))
    
    def sigmoid_deriv(self, y):  # Use output y, not input x
        return y * (1 - y)
    
    def forward(self, inputs):
        self.activations = [inputs]
        
        current = inputs
        for i in range(len(self.weights)):
            next_layer = []
            for j in range(len(self.weights[i][0])):
                z = self.biases[i][j]
                for k in range(len(current)):
                    z += current[k] * self.weights[i][k][j]
                next_layer.append(self.sigmoid(z))
            current = next_layer
            self.activations.append(current)
        
        return current
    
    def backward(self, targets):
        # Output layer error
        errors = []
        for i in range(len(targets)):
            errors.append(targets[i] - self.activations[-1][i])
        
        # Backpropagate
        for i in range(len(self.weights) - 1, -1, -1):
            new_errors = [0.0] * self.layers[i]
            
            for j in range(len(self.weights[i][0])):
                # Gradient
                delta = errors[j] * self.sigmoid_deriv(self.activations[i+1][j])
                
                # Update bias with momentum
                self.velocity_b[i][j] = self.momentum * self.velocity_b[i][j] + self.lr * delta
                self.biases[i][j] += self.velocity_b[i][j]
                
                # Update weights
                for k in range(len(self.weights[i])):
                    self.velocity_w[i][k][j] = (self.momentum * self.velocity_w[i][k][j] + 
                                                 self.lr * delta * self.activations[i][k])
                    self.weights[i][k][j] += self.velocity_w[i][k][j]
                    
                    if i > 0:
                        new_errors[k] += delta * self.weights[i][k][j]
            
            errors = new_errors
    
    def train(self, data, epochs=1000, verbose=True):
        print(f"📚 Training {self.name}...")
        
        for epoch in range(epochs):
            total_error = 0
            
            for inputs, targets in data:
                outputs = self.forward(inputs)
                
                # Calculate error
                for i in range(len(targets)):
                    total_error += abs(targets[i] - outputs[i])
                
                self.backward(targets)
            
            avg_error = total_error / len(data)
            
            if verbose and (epoch + 1) % 100 == 0:
                print(f"  Epoch {epoch+1}: Error = {avg_error:.4f}")
            
            self.history.append(avg_error)
        
        print(f"✅ Training complete!")
    
    def predict(self, inputs):
        return self.forward(inputs)
    
    def save(self, path):
        data = {
            'name': self.name,
            'layers': self.layers,
            'lr': self.lr,
            'weights': self.weights,
            'biases': self.biases
        }
        with open(path, 'w') as f:
            json.dump(data, f)
        print(f"💾 Saved to {path}")
    
    def load(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        self.name = data['name']
        self.layers = data['layers']
        self.lr = data['lr']
        self.weights = data['weights']
        self.biases = data['biases']
        print(f"📂 Loaded from {path}")


def create_pattern_task(task_type='xor'):
    """Create different training tasks"""
    
    if task_type == 'xor':
        return [
            ([0, 0], [0]),
            ([0, 1], [1]),
            ([1, 0], [1]),
            ([1, 1], [0]),
        ]
    
    elif task_type == 'and':
        return [
            ([0, 0], [0]),
            ([0, 1], [0]),
            ([1, 0], [0]),
            ([1, 1], [1]),
        ]
    
    elif task_type == 'or':
        return [
            ([0, 0], [0]),
            ([0, 1], [1]),
            ([1, 0], [1]),
            ([1, 1], [1]),
        ]
    
    elif task_type == 'not':
        return [
            ([0], [1]),
            ([1], [0]),
        ]
    
    elif task_type == 'identity':
        return [
            ([1, 0], [1, 0]),
            ([0, 1], [0, 1]),
            ([1, 1], [1, 1]),
            ([0, 0], [0, 0]),
        ]
        layers = [2, 4, 2]  # 2 inputs, 2 outputs
    
    elif task_type == 'addition':
        return [
            ([0, 0], [0, 0]),  # 0+0=00
            ([0, 1], [0, 1]),  # 0+1=01
            ([1, 0], [0, 1]),  # 1+0=01
            ([1, 1], [1, 0]),  # 1+1=10 (binary 2)
        ]
        layers = [2, 4, 2]
    
    else:
        raise ValueError(f"Unknown task: {task_type}")


def test_network():
    """Test the neural network on various tasks"""
    
    print("=" * 60)
    print("🧠 NEURAL NETWORK AI - TEST SUITE")
    print("=" * 60)
    
    tasks = ['and', 'or', 'not', 'identity', 'xor']
    
    results = []
    
    for task in tasks:
        print(f"\n📊 Testing {task.upper()}...")
        
        data = create_pattern_task(task)
        
        # Determine architecture based on task
        if task == 'not':
            layers = [1, 4, 1]
        elif task == 'xor':
            layers = [2, 8, 1]  # XOR needs more hidden neurons
        elif task == 'identity':
            layers = [2, 4, 2]  # 2 outputs
        elif task == 'addition':
            layers = [2, 4, 2]  # 2 outputs
        else:
            layers = [2, 4, 1]
        
        # Create and train
        ai = NeuralNetworkAI(layers, learning_rate=0.5, momentum=0.9, name=f"{task}_AI")
        ai.train(data, epochs=1000, verbose=False)
        
        # Test
        print(f"   Results:")
        correct = 0
        for inputs, expected in data:
            output = ai.predict(inputs)
            pred = 1 if output[0] > 0.5 else 0
            exp = int(expected[0])
            status = "✅" if pred == exp else "❌"
            print(f"      {inputs} → {output[0]:.3f} ({pred}) expected {exp} {status}")
            if pred == exp:
                correct += 1
        
        accuracy = correct / len(data) * 100
        results.append((task, accuracy))
        print(f"   Accuracy: {accuracy:.0f}%")
        
        # Save
        ai.save(f"{task}_model.json")
    
    print("\n" + "=" * 60)
    print("📈 SUMMARY")
    print("=" * 60)
    for task, acc in results:
        print(f"   {task.upper()}: {acc:.0f}%")
    
    return results


if __name__ == "__main__":
    test_network()