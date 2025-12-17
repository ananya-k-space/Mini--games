# 🎮 Mini Games Collection

A collection of three engaging mini-games built with Python and Tkinter, featuring beautiful UI, multiplayer support, and persistent leaderboards.

🎮 Three addictive mini-games built with Python! Test your memory, speed & reflexes. Play solo or with friends. Track your high scores!

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 🌟 Features

- **Three Unique Games**: Memory Match, Number Rush, and Color Blast
- **Multiplayer Support**: Play with 1-4 players
- **Dynamic UI**: Beautiful, responsive interface with smooth animations
- **Leaderboard System**: Track high scores with persistent storage
- **Customizable Difficulty**: Multiple difficulty levels for each game
- **Theme Options**: Different visual themes for variety

## 🎯 Games Included

### 🧠 Memory Match
Test your memory by finding matching pairs of symbols!
- **Objective**: Find all matching pairs before time runs out
- **Difficulty Levels**: 5 levels (Easy to Expert)
- **Grid Sizes**: 4×4 to 6×6
- **Theme Options**: Animals, Fruits, Nature, Space, Food, Sports
- **Scoring**: Speed and accuracy based with combo bonuses

### ⚡ Number Rush
Click numbers in sequential order as fast as you can!
- **Objective**: Click numbers 1 to N in order
- **Difficulty Levels**: 5 levels (15 to 40 numbers)
- **Time Limits**: 30 to 60 seconds depending on difficulty
- **Scoring**: Speed-based scoring with level multipliers
- **Challenge**: Numbers are randomly positioned each round

### 🎨 Color Blast
Match colors quickly and accurately!
- **Objective**: Click the correct color as fast as possible
- **Difficulty Levels**: 5 levels with increasing speed
- **Multiple Rounds**: Complete sequences of color matches
- **Scoring**: Accuracy and speed combined
- **Visual Feedback**: Instant feedback on correct/incorrect choices

## 🎨 Interface Highlights

### Main Menu
The game features a beautiful card-based interface with three colorful game cards:
- **Memory Match** card with brain emoji (🧠) in purple
- **Number Rush** card with lightning emoji (⚡) in blue  
- **Color Blast** card with paint palette emoji (🎨) in orange
- Each card shows the game name, description, and a "Play Now" button
- Clean white background with smooth hover effects

### Game Setup Dialogs
All three games feature consistent, polished setup screens:

**Memory Match Setup (🧠)**
- Blue header with "Memory Match Setup" title
- Player selection: Radio buttons for 1-4 players
- Dynamic player name fields (only shows fields for selected number of players)
- Theme selection grid: Animals, Fruits, Nature, Space, Food, Sports (with emoji previews)
- 5 difficulty levels with colored indicators:
  - ⭐ Easy - 4×4 Grid (Green)
  - ⭐⭐ Medium - 4×4 Grid (Blue)
  - ⭐⭐⭐ Hard - 5×5 Grid (Orange)
  - ⭐⭐⭐⭐ Very Hard - 6×6 Grid (Red)
  - ⭐⭐⭐⭐⭐ Expert - 6×6 Grid (Purple)
- Large green "START GAME" button at bottom
- Fully scrollable content (650×800 window)

**Number Rush Setup (⚡)**
- Blue header with "Number Rush Setup" title
- Player selection with radio buttons (1-4 players)
- Dynamic name input fields (shows only selected number)
- 5 difficulty levels with time and number details:
  - ⭐ Easy - 15 numbers • 30s (Green)
  - ⭐⭐ Medium - 20 numbers • 35s (Blue)
  - ⭐⭐⭐ Hard - 25 numbers • 40s (Orange)
  - ⭐⭐⭐⭐ Very Hard - 30 numbers • 45s (Red)
  - ⭐⭐⭐⭐⭐ Expert - 40 numbers • 60s (Purple)
- Green "START GAME" button
- Scrollable dialog (600×700 window)

**Color Blast Setup (🎨)**
- Orange header with "Color Blast Setup" title
- Player selection interface (1-4 players)
- Player name fields that adjust to selection
- 5 progressive difficulty levels with visual indicators
- Green "START GAME" button
- Smooth scrolling interface (650×750 window)

### Gameplay Features
- **Memory Match**: Cards flip with smooth animations, matching pairs stay revealed, wrong pairs flip back
- **Number Rush**: Randomly positioned number buttons, visual feedback on clicks, real-time timer, progress indicator
- **Color Blast**: Color options displayed as buttons, instant feedback, score tracking, round progression

### Leaderboard
- Clean scrollable list showing top 10 scores
- Each entry shows: Rank number, Player name, Score, Level, Timestamp
- Top 3 positions highlighted in gold/yellow
- Color-coded by game type

## 📋 Requirements

- Python 3.8 or higher
- Tkinter (usually comes with Python)
- No additional dependencies required!

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ananya-k-space/mini-games-collection.git
cd mini-games-collection
```

2. **Run the game**
```bash
python main.py
```

That's it! No dependencies to install.

### How to Play

1. Launch the game with `python main.py`
2. Select a game from the main menu
3. Choose number of players and enter names
4. Select difficulty level
5. Click "START GAME" and enjoy!

## 🏗️ Project Structure

```
mini-games-collection/
├── main.py                 # Application entry point
├── game_menu.py           # Main menu interface
├── scores.json            # Persistent score storage
├── games/
│   ├── __init__.py
│   ├── memory_match.py    # Memory Match game logic
│   ├── number_rush.py     # Number Rush game logic
│   └── color_blast.py     # Color Blast game logic
└── utils/
    ├── __init__.py
    ├── styles.py          # UI styling and colors
    └── scoreboard.py      # Score management
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Mini Games Collection

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👥 Credits

Built with ❤️ using Python and Tkinter

---

<div align="center">
  <p>⭐ Star this repository if you found it helpful!</p>
</div>
