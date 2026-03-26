#!/usr/bin/env python3
"""
SETUP SCRIPT FOR CLOUD TRAINING
Run this locally to prepare for cloud deployment
"""

import os
import json

print("=" * 60)
print("☁️ CLOUD TRAINING SETUP")
print("=" * 60)

# Check what's available
print("\n📋 Checking available tools...")

tools = {
    'Python': 'python3 --version',
    'PyTorch': 'python3 -c "import torch; print(torch.__version__)"',
    'TensorFlow': 'python3 -c "import tensorflow; print(tensorflow.__version__)"',
    'NumPy': 'python3 -c "import numpy; print(numpy.__version__)"',
}

for name, cmd in tools.items():
    try:
        result = os.popen(cmd).read().strip()
        print(f"   ✅ {name}: {result}")
    except:
        print(f"   ❌ {name}: Not installed")

# Create setup files
print("\n📁 Creating setup files...")

# requirements.txt for cloud
requirements = """
torch>=2.0.0
numpy>=1.20.0
transformers>=4.30.0
"""

with open('/root/.openclaw/workspace/money-system/requirements.txt', 'w') as f:
    f.write(requirements)
print("   ✅ requirements.txt created")

# Colab launcher
colab_code = """# @title 🚀 Quick Start - Click Play to Run

# Install dependencies
!pip install torch transformers numpy

# Clone repository
!git clone https://github.com/Loran4vr/jekstore.git
%cd jekstore

# Run training
!python3 cloud_lm.py
"""

with open('/root/.openclaw/workspace/money-system/run_on_colab.py', 'w') as f:
    f.write(colab_code)
print("   ✅ run_on_colab.py created")

# Kaggle launcher
kaggle_code = """# Kaggle: Cloud Training Setup
# Copy this to a Kaggle notebook

# Install packages
!pip install torch transformers numpy

# Clone
!git clone https://github.com/Loran4vr/jekstore.git
import os
os.chdir('jekstore')

# Run
!python3 cloud_lm.py
"""

with open('/root/.openclaw/workspace/money-system/run_on_kaggle.py', 'w') as f:
    f.write(kaggle_code)
print("   ✅ run_on_kaggle.py created")

# Config for scaling
config = {
    "model": {
        "vocab_size": 50000,
        "d_model": 512,
        "n_heads": 8,
        "n_layers": 8,
        "d_ff": 2048,
        "max_len": 512
    },
    "training": {
        "batch_size": 32,
        "learning_rate": 0.0001,
        "epochs": 100,
        "warmup_steps": 1000
    },
    "data": {
        "sources": [
            " wikipedia dump",
            " common crawl",
            " bookcorpus",
            " custom data"
        ]
    },
    "cloud": {
        "colab": {"gpu": "T4", "ram": "16GB", "storage": "100GB"},
        "kaggle": {"gpu": "P100", "ram": "16GB"},
        "gradient": {"gpu": "A100", "ram": "30GB"}
    }
}

with open('/root/.openclaw/workspace/money-system/scale_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print("   ✅ scale_config.json created")

# GitHub instructions
instructions = """
☁️ TO TRAIN ON CLOUD (FREE GPU):

OPTION 1: Google Colab (Easiest)
--------------------------------
1. Go to: https://colab.research.google.com
2. Click "New Notebook"
3. Paste code from cloud_lm.py
4. Click Runtime → Change Runtime Type → Select GPU
5. Press Play

OPTION 2: Kaggle
----------------
1. Go to: https://kaggle.com/notebooks
2. Create new notebook
3. Enable GPU in settings
4. Run the code

OPTION 3: Gradient
------------------
1. Go to: https://gradient.run
2. Create notebook with GPU
3. Run the code

To Scale Up:
------------
Edit these values in cloud_lm.py:
- d_model: 128 → 512 (or 1024)
- n_layers: 2 → 6 (or 12)  
- n_heads: 4 → 8 (or 16)
- Add more training data
"""

with open('/root/.openclaw/workspace/money-system/CLOUD_INSTRUCTIONS.txt', 'w') as f:
    f.write(instructions)
print("   ✅ CLOUD_INSTRUCTIONS.txt created")

print("\n" + "=" * 60)
print("✅ SETUP COMPLETE!")
print("=" * 60)
print("""
NEXT STEPS:
1. Copy cloud_lm.py to Google Colab
2. Enable GPU in settings
3. Run the code
4. The model can then scale up to millions of parameters!

Files created:
- requirements.txt (Python dependencies)
- run_on_colab.py (Ready to paste in Colab)
- run_on_kaggle.py (Ready for Kaggle)
- scale_config.json (Configuration for scaling)
- CLOUD_INSTRUCTIONS.txt (How to use)
""")