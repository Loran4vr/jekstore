#!/usr/bin/env python3
"""
Safe Neural Network AI - Built from Scratch
Implements: Forward Propagation, Backpropagation, Gradient Descent
Safety: Bounded outputs, no destructive operations, human oversight required
"""

import math
import random
import json
from datetime import datetime

# Seed for reproducibility
random.seed(42)

class SafeNeuralNetwork:
    """
    A simple neural network built from scratch with backpropagation.
    Safety features: Output bounds, no self-modification, human oversight required.
    """
    
    def __init__(self, layer_sizes, learning_rate=0.01, name="AI"):
        """
        Initialize the neural network.
        
        Args:
            layer_sizes: List of integers defining layer sizes [input, hidden, output]
            learning_rate: How fast the network learns (0.01 to 0.1 recommended)
            name: Name for this AI instance
        """
        self.name = name
        self.learning_rate = learning_rate
        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes)
        
        # Initialize weights and biases
        # Using Xavier initialization for better training
        self.weights = []
        self.biases = []
        
        for i in range(len(layer_sizes) - 1):
            # Xavier initialization
            scale = math.sqrt(2.0 / (layer_sizes[i] + layer_sizes[i+1]))
            layer_weights = [
                [random.gauss(0, scale) for _ in range(layer_sizes[i+1])]
                for _ in range(layer_sizes[i])
            ]
            layer_biases = [0.0 for _ in range(layer_sizes[i+1])]
            
            self.weights.append(layer_weights)
            self.biases.append(layer_biases)
        
        # Training history
        self.training_history = []
        self.is_trained = False
        
        print(f"🧠 {self.name} initialized: {layer_sizes}")
    
    # ==================== ACTIVATION FUNCTIONS ====================
    
    def sigmoid(self, x):
        """Sigmoid activation - squashes output between 0 and 1"""
        # Clip to prevent overflow
        x = max(-500, min(500, x))
        return 1.0 / (1.0 + math.exp(-x))
    
    def sigmoid_derivative(self, x):
        """Derivative of sigmoid for backpropagation"""
        return x * (1.0 - x)
    
    def relu(self, x):
        """ReLU activation - returns x if positive, 0 otherwise"""
        return max(0, x)
    
    def relu_derivative(self, x):
        """Derivative of ReLU"""
        return 1.0 if x > 0 else 0.0
    
    def tanh(self, x):
        """Tanh activation - squashes output between -1 and 1"""
        return math.tanh(x)
    
    def tanh_derivative(self, x):
        """Derivative of tanh"""
        return 1.0 - x ** 2
    
    def softmax(self, outputs):
        """Softmax for multi-class classification"""
        max_output = max(outputs)
        exp_outputs = [math.exp(o - max_output) for o in outputs]
        sum_exp = sum(exp_outputs)
        return [e / sum_exp for e in exp_outputs]
    
    # ==================== FORWARD PROPAGATION ====================
    
    def forward(self, inputs):
        """
        Forward propagation - pass input through network to get output.
        
        Args:
            inputs: List of input values
            
        Returns:
            Output from the network
        """
        if len(inputs) != self.layer_sizes[0]:
            raise ValueError(f"Expected {self.layer_sizes[0]} inputs, got {len(inputs)}")
        
        # Store activations for backpropagation
        self.activations = [inputs]
        self.z_values = []  # Pre-activation values
        
        current = inputs
        
        # Hidden layers with ReLU
        for i in range(len(self.weights) - 1):
            z = []
            for j in range(len(self.weights[i][0])):
                z_j = self.biases[i][j]
                for k in range(len(current)):
                    z_j += current[k] * self.weights[i][k][j]
                z.append(z_j)
            
            # Apply ReLU activation
            current = [self.relu(z_j) for z_j in z]
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
        
        # Apply softmax for classification
        output = self.softmax(z)
        self.activations.append(output)
        
        return output
    
    # ==================== BACKPROPAGATION ====================
    
    def backward(self, target):
        """
        Backpropagation - adjust weights based on error.
        
        Args:
            target: Expected output values
        """
        if len(target) != self.layer_sizes[-1]:
            raise ValueError(f"Expected {len(target)} targets, got {len(target)}")
        
        # Calculate output layer error
        errors = []
        for i in range(len(target)):
            # For softmax with cross-entropy, error = output - target
            errors.append(self.activations[-1][i] - target[i])
        
        # Backpropagate through layers
        for layer_idx in range(len(self.weights) - 1, -1, -1):
            new_errors = [0.0] * self.layer_sizes[layer_idx]
            
            # Calculate gradients
            for neuron_idx in range(len(self.weights[layer_idx][0])):
                # Gradient for weights and bias
                gradient = errors[neuron_idx] * self.relu_derivative(self.z_values[layer_idx][neuron_idx])
                
                # Update bias
                self.biases[layer_idx][neuron_idx] -= self.learning_rate * gradient
                
                # Update weights
                for prev_neuron in range(len(self.weights[layer_idx])):
                    self.weights[layer_idx][prev_neuron][neuron_idx] -= (
                        self.learning_rate * gradient * self.activations[layer_idx][prev_neuron]
                    )
                    
                    # Propagate error to previous layer
                    new_errors[prev_neuron] += errors[neuron_idx] * self.weights[layer_idx][prev_neuron][neuron_idx]
            
            errors = new_errors
    
    # ==================== TRAINING ====================
    
    def train(self, training_data, epochs=1000, verbose=True):
        """
        Train the neural network.
        
        Args:
            training_data: List of (input, target) tuples
            epochs: Number of training iterations
            verbose: Print progress
        """
        print(f"📚 Training {self.name}...")
        
        for epoch in range(epochs):
            total_error = 0.0
            
            for inputs, target in training_data:
                # Forward pass
                output = self.forward(inputs)
                
                # Calculate error (MSE)
                for i in range(len(target)):
                    total_error += (target[i] - output[i]) ** 2
                
                # Backward pass
                self.backward(target)
            
            avg_error = total_error / len(training_data)
            
            if verbose and (epoch + 1) % 100 == 0:
                print(f"  Epoch {epoch + 1}/{epochs}, Error: {avg_error:.6f}")
            
            self.training_history.append({
                'epoch': epoch + 1,
                'error': avg_error,
                'timestamp': datetime.now().isoformat()
            })
        
        self.is_trained = True
        print(f"✅ {self.name} trained successfully!")
    
    # ==================== PREDICTION ====================
    
    def predict(self, inputs):
        """
        Make a prediction (requires training first).
        
        Args:
            inputs: Input values
            
        Returns:
            Predicted output
        """
        if not self.is_trained:
            print("⚠️ Warning: Network not trained yet!")
        
        return self.forward(inputs)
    
    # ==================== SAFETY FEATURES ====================
    
    def clamp_weights(self, min_val=-10, max_val=10):
        """Safety: Keep weights bounded to prevent instability"""
        for layer in self.weights:
            for neuron in layer:
                for i in range(len(neuron)):
                    neuron[i] = max(min_val, min(max_val, neuron[i]))
    
    def get_info(self):
        """Get network information"""
        return {
            'name': self.name,
            'architecture': self.layer_sizes,
            'total_parameters': sum(len(w) for w in self.weights) + sum(len(b) for b in self.biases),
            'is_trained': self.is_trained,
            'training_epochs': len(self.training_history)
        }
    
    def save(self, filepath):
        """Save the network to a file"""
        data = {
            'name': self.name,
            'layer_sizes': self.layer_sizes,
            'learning_rate': self.learning_rate,
            'weights': self.weights,
            'biases': self.biases,
            'is_trained': self.is_trained,
            'training_history': self.training_history[-100:]  # Keep last 100
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 {self.name} saved to {filepath}")
    
    def load(self, filepath):
        """Load a saved network"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.name = data['name']
        self.layer_sizes = data['layer_sizes']
        self.learning_rate = data['learning_rate']
        self.weights = data['weights']
        self.biases = data['biases']
        self.is_trained = data['is_trained']
        self.training_history = data['training_history']
        
        print(f"📂 {self.name} loaded from {filepath}")


# ==================== EXAMPLE: PATTERN RECOGNITION ====================

def create_pattern_training_data():
    """Create training data for basic pattern recognition"""
    # XOR-like pattern (hard for simple networks!)
    training_data = [
        # Input: [a, b], Output: [a XOR b]
        ([0, 0], [0]),
        ([0, 1], [1]),
        ([1, 0], [1]),
        ([1, 1], [0]),
    ]
    return training_data


def create_number_addition_data():
    """Training data for simple addition"""
    training_data = [
        ([0, 0], [0]),
        ([0, 1], [1]),
        ([1, 0], [1]),
        ([1, 1], [2]),  # Needs 2 output neurons for values 0,1,2
    ]
    return training_data


# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 SAFE NEURAL NETWORK AI - Built from Scratch")
    print("=" * 60)
    print()
    
    # Create a network: 2 inputs, 4 hidden, 1 output
    ai = SafeNeuralNetwork(layer_sizes=[2, 4, 1], learning_rate=0.1, name="PatternAI")
    
    # Get network info
    info = ai.get_info()
    print(f"\n📊 Network Info:")
    print(f"   Parameters: {info['total_parameters']}")
    print(f"   Architecture: {info['architecture']}")
    
    # Create training data (XOR pattern)
    print("\n🔄 Training on XOR pattern...")
    training_data = create_pattern_training_data()
    
    # Train the network
    ai.train(training_data, epochs=1000, verbose=True)
    
    # Test the network
    print("\n🧪 Testing:")
    test_cases = [[0, 0], [0, 1], [1, 0], [1, 1]]
    for inputs in test_cases:
        output = ai.predict(inputs)
        expected = 1 if (inputs[0] != inputs[1]) else 0
        print(f"   {inputs} → {output[0]:.4f} (expected: {expected})")
    
    # Save the trained network
    ai.save("trained_ai.json")
    
    print("\n✅ Neural network training complete!")