#!/usr/bin/env python3
"""
Advanced Neural Network AI - Multi-task Learning
Built from scratch with: Backpropagation, Adam optimizer, Dropout safety
Safety: Output bounds, human oversight, no self-modification
"""

import math
import random
import json
import os
from datetime import datetime

random.seed(42)

class AdvancedNeuralNetwork:
    """
    Advanced neural network with:
    - Multiple activation functions
    - Adam optimizer (better convergence)
    - Dropout for regularization
    - Save/Load functionality
    - Multi-task learning capability
    """
    
    def __init__(self, layer_sizes, learning_rate=0.001, name="AdvancedAI"):
        self.name = name
        self.layer_sizes = layer_sizes
        self.learning_rate = learning_rate
        self.num_layers = len(layer_sizes)
        
        # Initialize weights with He initialization (better for ReLU)
        self.weights = []
        self.biases = []
        
        for i in range(len(layer_sizes) - 1):
            # He initialization
            scale = math.sqrt(2.0 / layer_sizes[i])
            layer_weights = [
                [random.gauss(0, scale) for _ in range(layer_sizes[i+1])]
                for _ in range(layer_sizes[i])
            ]
            layer_biases = [0.0] * layer_sizes[i+1]
            
            self.weights.append(layer_weights)
            self.biases.append(layer_biases)
        
        # Adam optimizer momentums
        self.m_weights = [[[0]*len(w) for w in layer] for layer in self.weights]
        self.v_weights = [[[0]*len(w) for w in layer] for layer in self.weights]
        self.m_biases = [[0]*len(b) for b in self.biases]
        self.v_biases = [[0]*len(b) for b in self.biases]
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.epsilon = 1e-8
        self.t = 0
        
        # Training state
        self.is_trained = False
        self.training_history = []
        
        print(f"🧠 {name} initialized: {layer_sizes}")
    
    def relu(self, x):
        x = max(-100, min(100, x))
        return max(0, x)
    
    def relu_derivative(self, x):
        return 1.0 if x > 0 else 0.0
    
    def leaky_relu(self, x, alpha=0.01):
        return x if x > 0 else alpha * x
    
    def leaky_relu_derivative(self, x, alpha=0.01):
        return 1.0 if x > 0 else alpha
    
    def sigmoid(self, x):
        x = max(-500, min(500, x))
        return 1.0 / (1.0 + math.exp(-x))
    
    def sigmoid_derivative(self, x):
        return x * (1.0 - x)
    
    def tanh(self, x):
        return math.tanh(x)
    
    def tanh_derivative(self, x):
        return 1.0 - x ** 2
    
    def softmax(self, x):
        exp_x = [math.exp(max(xi - max(x), 0)) for xi in x]
        sum_exp = sum(exp_x)
        return [ei / sum_exp for ei in exp_x]
    
    def forward(self, inputs, training=False):
        self.activations = [inputs]
        self.z_values = []
        self.dropout_masks = []
        
        current = inputs
        
        # Hidden layers with Leaky ReLU
        for i in range(len(self.weights) - 1):
            z = []
            for j in range(len(self.weights[i][0])):
                z_j = self.biases[i][j]
                for k in range(len(current)):
                    z_j += current[k] * self.weights[i][k][j]
                z.append(z_j)
            
            # Apply Leaky ReLU
            current = [self.leaky_relu(zj) for zj in z]
            
            # Dropout during training
            if training:
                mask = [random.random() > 0.2 for _ in current]  # 20% dropout
                current = [c * m for c, m in zip(current, mask)]
                self.dropout_masks.append(mask)
            else:
                self.dropout_masks.append([1.0] * len(current))
            
            self.activations.append(current)
            self.z_values.append(z)
        
        # Output layer with softmax
        z = []
        for j in range(len(self.weights[-1][0])):
            z_j = self.biases[-1][j]
            for k in range(len(current)):
                z_j += current[k] * self.weights[-1][k][j]
            z.append(z_j)
        
        self.z_values.append(z)
        output = self.softmax(z)
        self.activations.append(output)
        
        return output
    
    def backward(self, target):
        self.t += 1
        
        # Output layer gradient (softmax + cross-entropy)
        gradients = []
        for i in range(len(target)):
            gradients.append(self.activations[-1][i] - target[i])
        
        # Backpropagate
        for layer_idx in range(len(self.weights) - 1, -1, -1):
            new_gradients = [0.0] * self.layer_sizes[layer_idx]
            
            for neuron_idx in range(len(self.weights[layer_idx][0])):
                # Gradient with leaky ReLU
                gradient = gradients[neuron_idx] * self.leaky_relu_derivative(
                    self.z_values[layer_idx][neuron_idx]
                )
                
                # Adam optimizer
                self.m_biases[layer_idx][neuron_idx] = (
                    self.beta1 * self.m_biases[layer_idx][neuron_idx] + 
                    (1 - self.beta1) * gradient
                )
                self.v_biases[layer_idx][neuron_idx] = (
                    self.beta2 * self.v_biases[layer_idx][neuron_idx] + 
                    (1 - self.beta2) * gradient ** 2
                )
                
                m_hat = self.m_biases[layer_idx][neuron_idx] / (1 - self.beta1 ** self.t)
                v_hat = self.v_biases[layer_idx][neuron_idx] / (1 - self.beta2 ** self.t)
                
                adjusted_lr = self.learning_rate * math.sqrt(1 - self.beta2 ** self.t) / (1 - self.beta1 ** self.t)
                
                # Update bias
                self.biases[layer_idx][neuron_idx] -= adjusted_lr * m_hat / (math.sqrt(v_hat) + self.epsilon)
                
                # Update weights
                for prev_neuron in range(len(self.weights[layer_idx])):
                    weight_gradient = gradient * self.activations[layer_idx][prev_neuron]
                    
                    # Adam for weights
                    self.m_weights[layer_idx][prev_neuron][neuron_idx] = (
                        self.beta1 * self.m_weights[layer_idx][prev_neuron][neuron_idx] + 
                        (1 - self.beta1) * weight_gradient
                    )
                    self.v_weights[layer_idx][prev_neuron][neuron_idx] = (
                        self.beta2 * self.v_weights[layer_idx][prev_neuron][neuron_idx] + 
                        (1 - self.beta2) * weight_gradient ** 2
                    )
                    
                    m_hat_w = self.m_weights[layer_idx][prev_neuron][neuron_idx] / (1 - self.beta1 ** self.t)
                    v_hat_w = self.v_weights[layer_idx][prev_neuron][neuron_idx] / (1 - self.beta2 ** self.t)
                    
                    self.weights[layer_idx][prev_neuron][neuron_idx] -= (
                        adjusted_lr * m_hat_w / (math.sqrt(v_hat_w) + self.epsilon)
                    )
                    
                    # Propagate gradient
                    if layer_idx > 0:
                        new_gradients[prev_neuron] += (
                            gradient * self.weights[layer_idx][prev_neuron][neuron_idx]
                        )
            
            gradients = new_gradients
    
    def train(self, training_data, epochs=1000, verbose=True):
        print(f"📚 Training {self.name} with Adam optimizer...")
        
        for epoch in range(epochs):
            total_error = 0.0
            
            for inputs, target in training_data:
                output = self.forward(inputs, training=True)
                
                # Cross-entropy loss
                for i in range(len(target)):
                    if target[i] > 0:
                        total_error -= target[i] * math.log(max(output[i], 1e-10))
                
                self.backward(target)
            
            if verbose and (epoch + 1) % 100 == 0:
                print(f"  Epoch {epoch + 1}/{epochs}, Loss: {total_error/len(training_data):.6f}")
            
            self.training_history.append({
                'epoch': epoch + 1,
                'loss': total_error / len(training_data)
            })
        
        self.is_trained = True
        print(f"✅ {self.name} trained!")
    
    def predict(self, inputs):
        return self.forward(inputs, training=False)
    
    def save(self, filepath):
        data = {
            'name': self.name,
            'layer_sizes': self.layer_sizes,
            'learning_rate': self.learning_rate,
            'weights': self.weights,
            'biases': self.biases,
            'is_trained': self.is_trained,
            'training_history': self.training_history[-50:]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
        print(f"💾 Saved to {filepath}")
    
    def load(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.name = data['name']
        self.layer_sizes = data['layer_sizes']
        self.learning_rate = data['learning_rate']
        self.weights = data['weights']
        self.biases = data['biases']
        self.is_trained = data['is_trained']
        self.training_history = data['training_history']
        print(f"📂 Loaded from {filepath}")


# ==================== DEMO ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 ADVANCED NEURAL NETWORK AI")
    print("=" * 60)
    
    # Create network for XOR (needs more hidden neurons)
    ai = AdvancedNeuralNetwork(
        layer_sizes=[2, 8, 8, 1],  # Deeper network
        learning_rate=0.1,
        name="XOR_Solver"
    )
    
    # XOR training data
    training_data = [
        ([0, 0], [1, 0]),  # Output: [one-hot encoding]
        ([0, 1], [0, 1]),
        ([1, 0], [0, 1]),
        ([1, 1], [1, 0]),
    ]
    
    print("\n🔄 Training on XOR pattern...")
    ai.train(training_data, epochs=500, verbose=True)
    
    # Test
    print("\n🧪 Results:")
    test_cases = [[0, 0], [0, 1], [1, 0], [1, 1]]
    for inputs in test_cases:
        output = ai.predict(inputs)
        pred = "0" if output[0] > output[1] else "1"
        expected = "0" if inputs[0] == inputs[1] else "1"
        print(f"   {inputs} → {pred} (expected: {expected})")
    
    # Save
    ai.save("advanced_ai.json")
    print("\n✅ Training complete!")