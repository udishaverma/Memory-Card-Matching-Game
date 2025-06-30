#!/usr/bin/env python3
"""
Launch the memory game in windowed mode for screen recording.
"""

import sys
import os

# Add the game directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the game
from main import MemoryMatchGame

if __name__ == "__main__":
    print("🎴 Starting Memory Match Game in WINDOWED MODE")
    print("   Perfect for screen recording and screenshots!")
    print("   Press F11 to toggle fullscreen if needed.")
    print()
    
    game = MemoryMatchGame()
    game.run()
