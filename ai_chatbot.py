#!/usr/bin/env python3
"""
Minimal AI Chatbot - Can be deployed to free services
Works on: Replit, Glitch, Railway, Render, Heroku (free tier)
"""

import random
import json
import re

class SimpleAI:
    """Simple AI that can chat and learn"""
    
    def __init__(self):
        self.memory = {}
        self.responses = {
            'greeting': ['Hello!', 'Hi there!', 'Hey!', 'Greetings!'],
            'how_are_you': ['I am doing well!', 'Great!', 'Good thanks!'],
            'what_are_you': ['I am an AI chatbot!', 'I am a simple AI assistant.'],
            'help': ['I can help with many things! Ask me anything.'],
            'default': ['Interesting!', 'Tell me more!', 'I see!', 'Got it!']
        }
        
        # Pre-defined knowledge
        self.knowledge = {
            'ai': 'Artificial Intelligence is the simulation of human intelligence by machines.',
            'machine learning': 'Machine learning is a type of AI that allows computers to learn from data.',
            'neural network': 'Neural networks are computer systems inspired by biological brains.',
            'transformer': 'Transformers are a type of deep learning architecture used for NLP.',
            'python': 'Python is a popular programming language for AI and ML.',
            'bitcoin': 'Bitcoin is a decentralized digital currency.',
        }
    
    def respond(self, message):
        """Generate a response"""
        message = message.lower()
        
        # Check for greetings
        if any(w in message for w in ['hello', 'hi', 'hey', 'greetings']):
            return random.choice(self.responses['greeting'])
        
        # Check how are you
        if 'how are' in message:
            return random.choice(self.responses['how_are_you'])
        
        # Check what are you
        if 'what are you' in message or 'who are you' in message:
            return random.choice(self.responses['what_are_you'])
        
        # Check for help
        if 'help' in message:
            return random.choice(self.responses['help'])
        
        # Check knowledge base
        for key, value in self.knowledge.items():
            if key in message:
                return value
        
        # Check memory
        if message in self.memory:
            return self.memory[message]
        
        return random.choice(self.responses['default'])
    
    def learn(self, question, answer):
        """Learn new information"""
        self.memory[question.lower()] = answer
    
    def get_knowledge(self):
        """Return knowledge base"""
        return self.knowledge


# ==================== WEB INTERFACE ====================

try:
    from flask import Flask, request, jsonify, render_template_string
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    print("Flask not available - running in terminal mode")

if HAS_FLASK:
    app = Flask(__name__)
    ai = SimpleAI()
    
    HTML = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Simple AI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #fff; }
            h1 { color: #00d4ff; text-align: center; }
            #chat { background: #16213e; padding: 15px; border-radius: 10px; height: 400px; overflow-y: auto; }
            .message { padding: 10px; margin: 5px 0; border-radius: 5px; }
            .user { background: #0f3460; text-align: right; }
            .ai { background: #1a1a2e; }
            input { width: 70%; padding: 10px; border-radius: 5px; border: none; }
            button { padding: 10px 20px; background: #00d4ff; border: none; border-radius: 5px; cursor: pointer; }
            .knowledge { background: #16213e; padding: 15px; margin-top: 20px; border-radius: 10px; }
            .knowledge h3 { color: #00d4ff; }
        </style>
    </head>
    <body>
        <h1>🤖 Simple AI Chatbot</h1>
        <div id="chat"></div>
        <p>
            <input type="text" id="msg" placeholder="Type a message..." onkeypress="if(event.key==='Enter')send()">
            <button onclick="send()">Send</button>
        </p>
        
        <div class="knowledge">
            <h3>📚 What I Know:</h3>
            <ul>
            {% for key, value in knowledge.items() %}
                <li><strong>{{ key }}:</strong> {{ value }}</li>
            {% endfor %}
            </ul>
        </div>
        
        <script>
            function send() {
                var msg = document.getElementById('msg').value;
                if (!msg) return;
                
                document.getElementById('chat').innerHTML += '<div class="message user">You: ' + msg + '</div>';
                document.getElementById('msg').value = '';
                
                fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: msg}) })
                    .then(r => r.json())
                    .then(d => {
                        document.getElementById('chat').innerHTML += '<div class="message ai">🤖 AI: ' + d.response + '</div>';
                        document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
                    });
            }
        </script>
    </body>
    </html>
    '''
    
    @app.route('/')
    def home():
        return render_template_string(HTML, knowledge=ai.get_knowledge())
    
    @app.route('/chat', methods=['POST'])
    def chat():
        data = request.json
        response = ai.respond(data.get('message', ''))
        return jsonify({'response': response})
    
    print("""
===============================================
    🤖 SIMPLE AI CHATBOT
===============================================
    
    To run this on a FREE service:
    
    1. REPLIT (easiest):
       - Go to replit.com
       - Create new Python Repl
       - Paste this code
       - Click Run
    
    2. GLITCH:
       - Go to glitch.com
       - New project > glitch-empty
       - Create server.py and paste code
    
    3. RENDER/HEROKU:
       - Push to GitHub
       - Connect to Render/Heroku
       - Deploy
    
    The bot knows about:
    - AI, Machine Learning, Neural Networks
    - Transformers, Python, Bitcoin
    
    Have fun! 🎉
===============================================
    """)
    
    # For local testing
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)

else:
    # Terminal mode
    print("""
===============================================
    🤖 SIMPLE AI - TERMINAL MODE
===============================================
    """)
    
    ai = SimpleAI()
    
    print("Type 'quit' to exit, 'help' for knowledge list")
    print()
    
    while True:
        msg = input("You: ")
        if msg.lower() == 'quit':
            break
        elif msg.lower() == 'help':
            print("\n📚 Knowledge:")
            for k, v in ai.get_knowledge().items():
                print(f"  {k}: {v}")
        else:
            print(f"🤖 AI: {ai.respond(msg)}")