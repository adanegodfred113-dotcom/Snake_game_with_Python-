"""
SnakeGH - A Classic Arcade Game
Lab 2 - Python (Level 200)
Name: Adane Godfred Amofah
"""

import random
import tkinter as tk

# ---------------- Constants ----------------
CELL = 24                  # size of one square in pixels
COLS = 25                  # squares across
ROWS = 20                  # squares down
WIDTH = CELL * COLS        # 600 pixels
HEIGHT = CELL * ROWS       # 480 pixels
START_SPEED = 150          # milliseconds between moves (smaller = faster)
HIGH_SCORE_FILE = "snake_highscore.txt"

DIRECTIONS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
}
OPPOSITE = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
KEYS = {
    "up": "Up", "w": "Up",
    "down": "Down", "s": "Down",
    "left": "Left", "a": "Left",
    "right": "Right", "d": "Right",
}


# ---------------- Pure Logic Functions ----------------
def next_head(head, direction, wrap=False):
    """Return the square the head moves into (wraps around if no-walls mode is on)."""
    dx, dy = DIRECTIONS[direction]
    x, y = head[0] + dx, head[1] + dy
    if wrap:
        return (x % COLS, y % ROWS)
    return (x, y)


def hits_wall(cell):
    """True if the square is outside the board."""
    x, y = cell
    return x < 0 or x >= COLS or y < 0 or y >= ROWS


def hits_self(head, snake):
    """True if the head runs into the body (the tail moves away, so skip it)."""
    return head in snake[:-1]


def random_empty_cell(occupied):
    """Pick a random empty square not in the occupied set/list."""
    free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in occupied]
    return random.choice(free) if free else None


def level_for(score):
    """Level goes up every 5 points."""
    return score // 5 + 1


def speed_for(level):
    """Each level is 15 ms faster, but never faster than 60 ms."""
    return max(60, START_SPEED - (level - 1) * 15)


def load_high_score():
    """Read the saved high score, or 0 if there is none yet."""
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    """Write the new high score to the file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))


# ---------------- Main Game Class (Bonus: OOP Refactor) ----------------
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("SnakeGH - Classic Arcade Game")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1b2a")

        # Game state
        self.snake = []
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = (0, 0)
        self.golden_food = None
        self.obstacles = []
        self.score = 0
        self.level = 1
        self.high_score = load_high_score()
        self.running = False
        self.paused = False
        self.no_walls = False

        # Timer IDs
        self.loop_id = None
        self.golden_spawn_id = None
        self.golden_despawn_id = None

        # Build UI
        self._build_ui()
        self._bind_keys()
        self.draw_grid()
        self.update_labels()
        self.show_message("SnakeGH", "Press Space to start")

    def _build_ui(self):
        tk.Label(
            self.root,
            text="SnakeGH",
            font=("Segoe UI", 22, "bold"),
            fg="#66bb6a",
            bg="#0d1b2a",
        ).pack(pady=(10, 0))

        self.score_label = tk.Label(
            self.root,
            text="",
            font=("Consolas", 12, "bold"),
            fg="white",
            bg="#0d1b2a",
        )
        self.score_label.pack(pady=(0, 8))

        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH,
            height=HEIGHT,
            bg="#121212",
            highlightthickness=0,
        )
        self.canvas.pack(padx=15)

        tk.Label(
            self.root,
            text="Arrows/WASD = move  |  P = pause  |  N = no walls  |  Space = start",
            font=("Segoe UI", 10),
            fg="#90a4ae",
            bg="#0d1b2a",
        ).pack(pady=8)

    def _bind_keys(self):
        self.root.bind("<Key>", self.on_key)
        self.root.bind("<space>", self.on_space)
        self.root.bind("p", self.toggle_pause)
        self.root.bind("P", self.toggle_pause)
        self.root.bind("n", self.toggle_no_walls)
        self.root.bind("N", self.toggle_no_walls)

    # ---------------- Drawing Methods ----------------
    def draw_grid(self):
        """Draw faint grid lines once, at the start."""
        for x in range(0, WIDTH, CELL):
            self.canvas.create_line(x, 0, x, HEIGHT, fill="#1e1e1e")
        for y in range(0, HEIGHT, CELL):
            self.canvas.create_line(0, y, WIDTH, y, fill="#1e1e1e")

    def update_labels(self):
        walls_status = "OFF" if self.no_walls else "ON"
        self.score_label.config(
            text=f"Score: {self.score}   Level: {self.level}   Best: {self.high_score}   Walls: {walls_status}"
        )

    def draw(self):
        """Clear old game pieces and redraw obstacles, food, golden jollof, and snake."""
        self.canvas.delete("piece", "message")

        # 1. Draw Obstacles (Bonus: Grey blocks from Level 3)
        for ox, oy in self.obstacles:
            self.canvas.create_rectangle(
                ox * CELL + 1, oy * CELL + 1,
                ox * CELL + CELL - 1, oy * CELL + CELL - 1,
                fill="#78909c", outline="#546e7a", tags="piece"
            )

        # 2. Draw Regular Food
        fx, fy = self.food
        self.canvas.create_oval(
            fx * CELL + 4, fy * CELL + 4,
            fx * CELL + CELL - 4, fy * CELL + CELL - 4,
            fill="#e53935", outline="", tags="piece"
        )

        # 3. Draw Golden Jollof (Bonus: Worth 3 points)
        if self.golden_food is not None:
            gx, gy = self.golden_food
            self.canvas.create_oval(
                gx * CELL + 2, gy * CELL + 2,
                gx * CELL + CELL - 2, gy * CELL + CELL - 2,
                fill="#ffd600", outline="#ffab00", width=2, tags="piece"
            )

        # 4. Draw Snake Body & Head with Eyes (Bonus)
        for index, (x, y) in enumerate(self.snake):
            colour = "#1b5e20" if index == 0 else "#43a047"
            self.canvas.create_rectangle(
                x * CELL + 1, y * CELL + 1,
                x * CELL + CELL - 1, y * CELL + CELL - 1,
                fill=colour, outline="", tags="piece"
            )
            if index == 0:
                self._draw_eyes(x, y)

        self.update_labels()

    def _draw_eyes(self, x, y):
        """Draw 2 small white eyes on the snake's head facing the direction of travel."""
        px, py = x * CELL, y * CELL
        r = 3  # eye radius
        offsets = {
            "Up":    [(6, 6), (CELL - 6, 6)],
            "Down":  [(6, CELL - 6), (CELL - 6, CELL - 6)],
            "Left":  [(6, 6), (6, CELL - 6)],
            "Right": [(CELL - 6, 6), (CELL - 6, CELL - 6)],
        }
        for ox, oy in offsets[self.direction]:
            self.canvas.create_oval(
                px + ox - r, py + oy - r,
                px + ox + r, py + oy + r,
                fill="white", outline="", tags="piece"
            )

    def show_message(self, title, subtitle):
        """Write a big message in the middle of the board."""
        self.canvas.delete("message")
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 20,
            text=title, fill="white",
            font=("Segoe UI", 28, "bold"), tags="message"
        )
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 20,
            text=subtitle, fill="#bbbbbb",
            font=("Segoe UI", 12), tags="message"
        )

    # ---------------- Bonus Mechanics ----------------
    def _cancel_timers(self):
        for timer_id in (self.loop_id, self.golden_spawn_id, self.golden_despawn_id):
            if timer_id is not None:
                self.root.after_cancel(timer_id)
        self.loop_id = None
        self.golden_spawn_id = None
        self.golden_despawn_id = None

    def schedule_golden_food(self):
        """Spawn Golden Jollof every 10 seconds."""
        if self.running and not self.paused:
            self.golden_spawn_id = self.root.after(10000, self.spawn_golden_food)

    def spawn_golden_food(self):
        if not self.running or self.paused:
            return
        occupied = set(self.snake) | set(self.obstacles) | {self.food}
        self.golden_food = random_empty_cell(occupied)
        self.draw()
        # Disappears after 5 seconds
        self.golden_despawn_id = self.root.after(5000, self.remove_golden_food)

    def remove_golden_food(self):
        self.golden_food = None
        if self.running and not self.paused:
            self.draw()
            self.schedule_golden_food()

    def update_obstacles(self):
        """From level 3, add grey obstacle blocks safely away from snake and food."""
        if self.level < 3:
            self.obstacles = []
            return
        target_count = min(12, (self.level - 2) * 3)
        hx, hy = self.snake[0]
        # Keep a 3-cell safe zone around the snake's head so it doesn't get trapped unfairly
        safe_zone = {(hx + dx, hy + dy) for dx in range(-2, 3) for dy in range(-2, 3)}
        occupied = set(self.snake) | set(self.obstacles) | {self.food} | safe_zone
        if self.golden_food:
            occupied.add(self.golden_food)

        while len(self.obstacles) < target_count:
            cell = random_empty_cell(occupied)
            if cell is None:
                break
            self.obstacles.append(cell)
            occupied.add(cell)

    # ---------------- Core Game Flow ----------------
    def start_game(self):
        self._cancel_timers()
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.obstacles = []
        self.golden_food = None
        self.score = 0
        self.level = 1
        self.food = random_empty_cell(self.snake)
        self.running = True
        self.paused = False

        self.draw()
        self.loop_id = self.root.after(speed_for(self.level), self.game_loop)
        self.schedule_golden_food()

    def game_loop(self):
        """One tick: move, eat, draw, then schedule the next tick."""
        if not self.running or self.paused:
            return

        self.direction = self.next_direction
        head = next_head(self.snake[0], self.direction, wrap=self.no_walls)

        # Check collisions (walls only kill if no_walls is False)
        hit_boundary = (not self.no_walls) and hits_wall(head)
        if hit_boundary or hits_self(head, self.snake) or head in self.obstacles:
            self.game_over()
            return

        self.snake.insert(0, head)
        ate_something = False

        # Check regular food (+1 point)
        if head == self.food:
            self.score += 1
            ate_something = True
            occupied = set(self.snake) | set(self.obstacles)
            if self.golden_food:
                occupied.add(self.golden_food)
            self.food = random_empty_cell(occupied)

        # Check Golden Jollof (+3 points)
        elif self.golden_food is not None and head == self.golden_food:
            self.score += 3
            ate_something = True
            self.golden_food = None
            if self.golden_despawn_id is not None:
                self.root.after_cancel(self.golden_despawn_id)
                self.golden_despawn_id = None
            self.schedule_golden_food()

        if ate_something:
            new_level = level_for(self.score)
            if new_level > self.level:
                self.level = new_level
                self.update_obstacles()
        else:
            self.snake.pop()

        self.draw()
        self.loop_id = self.root.after(speed_for(self.level), self.game_loop)

    def game_over(self):
        self._cancel_timers()
        self.running = False
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
            self.show_message("NEW HIGH SCORE!", f"You scored {self.score}. Press Space to play again")
        else:
            self.show_message("GAME OVER", f"You scored {self.score}. Press Space to play again")
        self.update_labels()

    # ---------------- Event Handlers ----------------
    def on_key(self, event):
        new_direction = KEYS.get(event.keysym.lower())
        if new_direction is None or not self.running or self.paused:
            return
        if new_direction != OPPOSITE[self.direction]:
            self.next_direction = new_direction

    def on_space(self, event=None):
        if not self.running:
            self.start_game()

    def toggle_pause(self, event=None):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self._cancel_timers()
            self.show_message("PAUSED", "Press P to continue")
        else:
            self.canvas.delete("message")
            self.loop_id = self.root.after(speed_for(self.level), self.game_loop)
            if self.golden_food is not None:
                self.golden_despawn_id = self.root.after(3000, self.remove_golden_food)
            else:
                self.schedule_golden_food()

    def toggle_no_walls(self, event=None):
        """Bonus: Toggle No Walls mode on/off with N."""
        self.no_walls = not self.no_walls
        self.update_labels()


# ---------------- Entry Point ----------------
if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
