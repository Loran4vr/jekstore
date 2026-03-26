# Kaggle: Cloud Training Setup
# Copy this to a Kaggle notebook

# Install packages
!pip install torch transformers numpy

# Clone
!git clone https://github.com/Loran4vr/jekstore.git
import os
os.chdir('jekstore')

# Run
!python3 cloud_lm.py
