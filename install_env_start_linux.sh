#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Uninstall all packages
pip freeze | xargs pip uninstall -y

# Install required packages
pip install pygame-cards
pip uninstall -y pygame
pip install pygame-gui
pip install requests pillow opencv-python tqdm graphviz

# Run the main script
python main.py
