Memory Card Matching Game
A fun and interactive memory game built using Python, Pygame, and Scikit-Image, with development powered by Amazon Q CLI — Amazon's AI-powered coding assistant. Test your memory and matching skills with beautifully rendered playing cards in two grid-based difficulty modes!

🎮 Gameplay Overview
In Memory Card Matching Game, players are presented with cards laid face down. The objective is to:

Click on cards to flip them over

Match them in pairs by remembering their positions

Complete the grid by matching all pairs

💡 Once all pairs are matched, a “Game Over – All Tiles Matched!” message appears and you can restart to try again.

🧩 Features
✅ Difficulty Levels:

4x4 Grid: Casual, quick-play mode (8 pairs)

6x6 Grid: Challenging mode (18 pairs)

✅ Classic Card Symbols:

Ranks: A, K, Q, J, 10, 9, 8, 7

Suits: ♥ ♦ ♣ ♠

Procedurally drawn using Scikit-Image

✅ Modern UI & Animations:

Fullscreen support

Clean layout and padding

Flip animations, highlighted matches

Dynamic resizing and button controls

✅ AI-Generated Code:

Developed with Amazon Q CLI using natural language prompts

Rapid iteration and debugging with AI-assisted workflow

🧠 What I Learned
Crafting effective prompts for AI coding

Structuring a scalable game using Python + Pygame

Balancing layout, symbol rendering, and gameplay logic

Leveraging Scikit-Image for dynamic asset generation

🚀 Getting Started
🔧 Requirements
Python 3.8+

Pygame

Scikit-Image

Install dependencies:

pip install pygame scikit-image

▶️ Run the Game
python main.py


📂 File Structure
memory_match_game/
├── main.py               # Entry point
├── game/
│   ├── board.py          # Grid layout and game logic
│   ├── card.py           # Card state, flip logic
│   └── assets.py         # Card symbol generation with Scikit-Image
├── ui/
│   ├── button.py         # Start/Reset button handling
│   └── theme.py          # Colors, font, layout constants
└── README.md             # This file


🙏 Acknowledgements
Big thanks to Amazon Q CLI for making AI-driven development accessible and productive.

🏷️ Tags
#AmazonQCLI #Python #Pygame #AI #GameDev #MemoryGame #BuildWithQ #OpenSource #ScikitImage #CodingWithAI

