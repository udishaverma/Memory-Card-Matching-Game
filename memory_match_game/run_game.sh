#!/bin/bash
# Memory Match Game Launcher

echo "Starting Memory Match Game..."
echo "Press Ctrl+C to quit the game"
echo ""

cd "$(dirname "$0")"
python3 main.py
