import tkinter as tk
import tkinter.messagebox
import random
import copy

# Initialize a 4x4 game grid with zeros
def initialize_grid():
    grid = [[0] * 4 for _ in range(4)]
    add_new_tile(grid)
    add_new_tile(grid)
    return grid

# Function to add a new tile (2 or 4) to an empty cell
def add_new_tile(grid):
    empty_cells = [(i, j) for i in range(4) for j in range(4) if grid[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        grid[i][j] = 2 if random.random() < 0.9 else 4

# Slide tiles in a row to the left and merge if necessary
def slide_and_merge_row(row):
    new_row = [num for num in row if num != 0]
    score = 0
    for i in range(len(new_row) - 1):
        if new_row[i] == new_row[i + 1]:
            new_row[i] *= 2
            score += new_row[i]
            new_row[i + 1] = 0
    new_row = [num for num in new_row if num != 0]
    return new_row + [0] * (4 - len(new_row)), score

# Move tiles left in the entire grid
def move_left(grid):
    score = 0
    for i in range(4):
        grid[i], row_score = slide_and_merge_row(grid[i])
        score += row_score
    return score

# Move tiles right by reversing, sliding, and reversing back
def move_right(grid):
    score = 0
    for i in range(4):
        grid[i], row_score = slide_and_merge_row(grid[i][::-1])
        score += row_score
        grid[i] = grid[i][::-1]
    return score

# Move tiles up by transposing, sliding, and transposing back
def move_up(grid):
    transpose_grid = [list(row) for row in zip(*grid)]
    score = 0
    for i in range(4):
        transpose_grid[i], row_score = slide_and_merge_row(transpose_grid[i])
        score += row_score
    grid[:] = [list(row) for row in zip(*transpose_grid)]
    return score

# Move tiles down by transposing, sliding right, and transposing back
def move_down(grid):
    transpose_grid = [list(row) for row in zip(*grid)]
    score = 0
    for i in range(4):
        transpose_grid[i], row_score = slide_and_merge_row(transpose_grid[i][::-1])
        score += row_score
        transpose_grid[i] = transpose_grid[i][::-1]
    grid[:] = [list(row) for row in zip(*transpose_grid)]
    return score

# Check if 2048 tile is on the grid (win condition)
def check_win(grid):
    for row in grid:
        if 2048 in row:
            return True
    return False

# Check if there are any moves left (loss condition)
def check_loss(grid):
    if any(0 in row for row in grid):
        return False
    for i in range(4):
        for j in range(4):
            if (j < 3 and grid[i][j] == grid[i][j + 1]) or (i < 3 and grid[i][j] == grid[i + 1][j]):
                return False
    return True

# Enhanced evaluation function using smoothness, monotonicity, and empty tiles
def evaluate_grid(grid):
    smoothness = sum(-abs(grid[i][j] - grid[i + di][j + dj])
                     for i in range(4) for j in range(4)
                     for di, dj in [(0, 1), (1, 0)] if 0 <= i + di < 4 and 0 <= j + dj < 4)
    monotonicity = 0
    max_tile = max(max(row) for row in grid)
    for i in range(4):
        for j in range(4):
            tile_value = grid[i][j]
            if tile_value == max_tile and (i, j) == (0, 0):
                monotonicity += 10000
            if i > 0 and grid[i - 1][j] >= tile_value:
                monotonicity += tile_value
            if j > 0 and grid[i][j - 1] >= tile_value:
                monotonicity += tile_value

    empty_tiles = sum(row.count(0) for row in grid)
    return smoothness + monotonicity + empty_tiles * 500

# Function to get the best move for the AI (evaluates all moves and selects the best one)
def best_move(grid):
    moves = ['Up', 'Down', 'Left', 'Right']
    best_score = float('-inf')
    best_move = None

    for move in moves:
        test_grid = copy.deepcopy(grid)
        if move == 'Up':
            move_up(test_grid)
        elif move == 'Down':
            move_down(test_grid)
        elif move == 'Left':
            move_left(test_grid)
        elif move == 'Right':
            move_right(test_grid)

        score = evaluate_grid(test_grid)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move

# GUI Class for 2048 Game
class Game2048:
    def __init__(self, root):
        self.root = root
        self.root.title("2048 Game")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        self.grid = initialize_grid()
        self.score = 0
        self.auto_playing = False
        self.setup_ui()

    def setup_ui(self):
        # Score label
        self.score_label = tk.Label(self.root, text="Score: 0", font=("Helvetica", 16))
        self.score_label.pack(pady=10)
        
        # Game grid
        self.frame = tk.Frame(self.root, bg="#bbada0")
        self.frame.place(relx=0.5, rely=0.45, anchor="center")
        self.tiles = [[None] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                label = tk.Label(self.frame, text="", width=4, height=2, font=("Helvetica", 24, "bold"), bg="#cdc1b4", fg="#776e65")
                label.grid(row=i, column=j, padx=5, pady=5)
                self.tiles[i][j] = label

        self.update_grid()

        # Create a frame for buttons to organize their layout
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="bottom",pady=20)

        # AI Button
        self.ai_button = tk.Button(self.button_frame, text="Suggest Move", command=self.suggest_move, font=("Helvetica", 12), width=12, height=2, bg="#4CAF50", fg="white", relief="flat", borderwidth=1)
        self.ai_button.grid(row=0, column=0, padx=5, pady=10)

        # Auto-Play Button
        self.auto_play_button = tk.Button(self.button_frame, text="Start Auto-Play", command=self.toggle_auto_play, font=("Helvetica", 12), width=12, height=2, bg="#FF5722", fg="white", relief="flat", borderwidth=1)
        self.auto_play_button.grid(row=0, column=1, padx=5, pady=10)

        # Restart Button
        self.restart_button = tk.Button(self.button_frame, text="Restart", command=self.restart_game, font=("Helvetica", 12), width=12, height=2, bg="#2196F3", fg="white", relief="flat", borderwidth=1)
        self.restart_button.grid(row=0, column=2, padx=5, pady=10)

        self.root.bind("<Key>", self.handle_keypress)

    def update_grid(self):
        for i in range(4):
            for j in range(4):
                tile_value = self.grid[i][j]
                self.tiles[i][j].config(
                    text=str(tile_value) if tile_value != 0 else "",
                    bg=self.get_tile_color(tile_value),
                    fg="#776e65" if tile_value < 8 else "#f9f6f2"
                )
        self.score_label.config(text=f"Score: {self.score}")

    def suggest_move(self):
        action = best_move(self.grid)
        if action:
            self.perform_move(action)

    def perform_move(self, action):
        moves = {'Up': move_up, 'Down': move_down, 'Left': move_left, 'Right': move_right}
        move = moves.get(action)
        if move:
            old_grid = copy.deepcopy(self.grid)
            score = move(self.grid)
            add_new_tile(self.grid)
            self.score += score
            self.update_grid()

            if self.check_game_over():
                self.display_game_over()

    def handle_keypress(self, event):
        if event.keysym == "Left":
            self.perform_move("Left")
        elif event.keysym == "Right":
            self.perform_move("Right")
        elif event.keysym == "Up":
            self.perform_move("Up")
        elif event.keysym == "Down":
            self.perform_move("Down")

    def toggle_auto_play(self):
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.auto_play_button.config(text="Stop Auto-Play", bg="#f44336")
            self.auto_play()
        else:
            self.auto_play_button.config(text="Start Auto-Play", bg="#FF5722")

    def auto_play(self):
        if self.auto_playing:
            action = best_move(self.grid)
            self.perform_move(action)
            self.root.after(500, self.auto_play)

    def restart_game(self):
        self.grid = initialize_grid()
        self.score = 0
        self.update_grid()

    def get_tile_color(self, value):
        colors = {
            2: "#eee4da", 4: "#ede0c8", 8: "#f2b179", 16: "#f59563",
            32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72", 256: "#edcc61",
            512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
        }
        return colors.get(value, "#cdc1b4")

    def check_game_over(self):
        if check_win(self.grid):
            tk.messagebox.showinfo("You Win!", "Congratulations, you reached 2048!")
            return True
        if check_loss(self.grid):
            tk.messagebox.showinfo("Game Over", "No more moves available!")
            return True
        return False

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()