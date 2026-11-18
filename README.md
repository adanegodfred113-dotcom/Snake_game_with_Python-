# SnakeGH 🐍

A classic Snake arcade game built with Python and Tkinter. Made for Lab 2 (Python, Level 200) at Ghana Communication Technology University.

## Features

- Smooth game loop using root.after(), so the window never freezes
- Arrow keys or WASD to move, with U-turn protection
- Score, level and speed that rise every 5 points
- Wall and self collision with game over and restart
- Pause and resume
- High score saved to a file and loaded on the next run

### Bonus features

- Golden Jollof: appears every 10 seconds, worth 3 points, disappears after 5 seconds
- No-walls mode: the snake wraps around to the other side
- Obstacles: grey blocks appear from level 3
- Snake eyes that face the direction of travel
- Object-oriented design with a SnakeGame class

## Requirements

- Python 3.10 or newer
- Tkinter (included with Python on Windows)

## How to run

    git clone https://github.com/<your-username>/SnakeGH.git
    cd SnakeGH
    python snakegh.py

## Controls

| Key | Action |
|-----|--------|
| Arrows / WASD | Move |
| Space | Start or play again |
| P | Pause or resume |
| N | Toggle no-walls mode |

## How it works

The snake is a list of (column, row) tuples on a 25 x 20 grid. Each tick, a new head is inserted at the front and the tail is removed. If the head lands on food, the tail is kept and the snake grows.

## Author

Adane Godfred Amofah
BSc. Computer Engineering (Level 200)
Ghana Communication Technology University 