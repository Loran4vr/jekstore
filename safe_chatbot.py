#!/usr/bin/env python3
"""
SAFE AI CHATBOT - Best Version
Safe by design - limited capabilities, no external actions, friendly only
"""

import random

class SafeChatbot:
    """
    A safe, friendly chatbot that:
    - Cannot execute commands
    - Cannot access external systems
    - Only responds with pre-defined safe responses
    - No access to private information
    - Friendly and helpful
    """
    
    def __init__(self):
        # Knowledge base - safe, factual, friendly
        self.knowledge = {
            # AI/ML
            'ai': "Artificial Intelligence is the simulation of human intelligence by machines. It includes things like machine learning, neural networks, and natural language processing!",
            'machine learning': "Machine learning is a type of AI where computers learn from data without being explicitly programmed. It's used for recommendations, predictions, and more!",
            'neural network': "Neural networks are computer systems inspired by the human brain. They have 'neurons' (like nodes) connected together that learn patterns!",
            'deep learning': "Deep learning uses neural networks with many layers. It's behind things like image recognition, speech assistants, and translation!",
            'transformer': "Transformers are a type of deep learning architecture that powers modern AI like ChatGPT. They use 'attention' to understand context!",
            'python': "Python is a popular programming language for AI and data science. It's known for being easy to read and having great libraries!",
            
            # Science facts
            'brain': "The human brain has about 86 billion neurons! It processes information at incredible speeds and uses only about 20 watts of power.",
            'sun': "The sun is a star at the center of our solar system. It's about 4.6 billion years old and makes up 99.86% of our solar system's mass!",
            'water': "Water is essential for life! About 71% of Earth's surface is covered in water, but only 3% is fresh.",
            'light': "Light travels at about 299,792 km/s - nothing can go faster!",
            'ocean': "The ocean contains about 97% of Earth's water. It's home to millions of species!",
            'space': "The universe is incredibly vast - there are more stars than grains of sand on all of Earth's beaches!",
            
            # General
            'hello': "Hello! 👋 I'm a friendly AI assistant. I can talk about science, AI, technology, and more!",
            'hi': "Hi there! 😊 How can I help you today?",
            'hey': "Hey! ✨ What's on your mind?",
            'how are you': "I'm doing great, thanks for asking! 😊 I love helping people learn about AI and science!",
            
            # About the user
            'who am i': "I don't know your name, but I know you're curious about AI! That's awesome!",
            'my name': "I don't have access to that information, but you can tell me if you'd like!",
            
            # Store/info
            'store': "I have a digital products store! You can check it out at: https://loran4vr.github.io/jekstore/",
            'bitcoin': "Bitcoin is a decentralized digital currency. It uses blockchain technology!",
            'money': "Money is interesting! There's a lot we could discuss about economics, but let's keep it friendly!",
            
            # Capabilities
            'what can you do': "I can chat about AI, science, technology, and general knowledge! I cannot: access the internet, run code, or store personal info. But I'm great for conversation! 📚",
            'capabilities': "I can: talk, answer questions, explain concepts, be friendly! I cannot: execute commands, access files, or do anything that could be harmful. Safety first! 🛡️",
            'limitations': "I can only use the information I've been given. I can't look things up or learn new things during our conversation. But I'm always happy to help with what I know! 😊",
            
            # Help
            'help': "I can help with: explaining AI concepts, science facts, general conversation. Just ask!",
            'thanks': "You're welcome! 😊 Happy to help!",
            'thank you': "No problem! 😊 Anytime!",
            
            # Friendly defaults
            'default': [
                "That's interesting! Tell me more about what you're thinking about.",
                "I see! That's a cool topic. What would you like to know more about?",
                "Fascinating! I love learning what people are interested in.",
                "Great question! There's a lot to explore there.",
                "I appreciate you chatting with me! What else is on your mind?",
                "That's a thoughtful point! I'd love to hear more.",
                "Interesting! I learn so much from conversations like this.",
            ]
        }
        
        # Keywords that trigger specific responses (order matters - check specific first)
        self.keywords = sorted(self.knowledge.keys(), key=len, reverse=True)
        
        # Counters for safety
        self.message_count = 0
        self.session_start = "conversation"
    
    def respond(self, message):
        """Generate a safe, friendly response"""
        self.message_count += 1
        
        # Normalize
        msg = message.lower().strip()
        
        # Check each keyword (longest matches first)
        for keyword in self.keywords:
            if keyword in msg:
                response = self.knowledge[keyword]
                if isinstance(response, list):
                    response = random.choice(response)
                return response
        
        # Default response
        return random.choice(self.knowledge['default'])
    
    def chat(self):
        """Start an interactive chat session"""
        print("=" * 50)
        print("🤖 SAFE AI CHATBOT")
        print("=" * 50)
        print("I'm a friendly, safe AI assistant!")
        print("I can talk about: AI, Science, Technology, and more!")
        print("Type 'quit' to exit, 'help' for what I can do.")
        print("=" * 50)
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print(f"🤖: Goodbye! It was great chatting with you! 👋")
                    break
                
                response = self.respond(user_input)
                print(f"🤖: {response}")
                
            except KeyboardInterrupt:
                print("\n🤖: Bye! Take care! 👋")
                break


# ==================== MAIN ====================

if __name__ == "__main__":
    bot = SafeChatbot()
    bot.chat()