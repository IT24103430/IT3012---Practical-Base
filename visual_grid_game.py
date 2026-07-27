# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A Pacman-style grid environment with food, opponents, walls, and toxic traps."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2,
                 num_traps=5, custom_walls=None):
        if width <= 0 or height <= 0:
            raise ValueError("width and height must both be positive")
        if min(num_food, num_opponents, num_traps) < 0:
            raise ValueError("entity counts cannot be negative")

        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)

        if custom_walls is not None:
            self.walls = {tuple(wall) for wall in custom_walls}
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Keep only valid cells and ensure the agent's starting cell is available.
        self.walls = {
            wall for wall in self.walls
            if 0 <= wall[0] < self.width and 0 <= wall[1] < self.height and wall != (0, 0)
        }

        available_cells = {
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in self.walls and (x, y) != (0, 0)
        }

        required_cells = num_food + num_opponents + num_traps
        if required_cells > len(available_cells):
            raise ValueError(
                "Not enough free cells for the requested food, opponents, and toxic traps."
            )

        # Sample without replacement so food, opponents, and traps never overlap.
        placements = random.sample(sorted(available_cells), required_cells)
        food_cells = placements[:num_food]
        opponent_cells = placements[num_food:num_food + num_opponents]
        trap_cells = placements[num_food + num_opponents:]
        self.food_positions = set(food_cells)

        # Opponents and toxic traps are physical environment state.
        self.opponents = [list(position) for position in opponent_cells]
        self.toxic_traps = set(trap_cells)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        return {
            'agent_pos': list(self.agent_pos),
            'opponent_positions': [list(op) for op in self.opponents],
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        # Traps remain in the environment, so every visit has a cost.
        if tuple_pos in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2,
                 num_traps=5, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            num_traps=num_traps,
            custom_walls=walls,
        )

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # Purple diamond-shaped traps are visible to the human player but are
        # represented to the agent only by the ``smells_toxin`` sensor.
        for tx, ty in self.env.toxic_traps:
            center_x = (tx + 0.5) * self.cell_size
            center_y = (self.env.height - ty - 0.5) * self.cell_size
            radius = self.cell_size * 0.28
            self.canvas.create_polygon(
                center_x, center_y - radius,
                center_x + radius, center_y,
                center_x, center_y + radius,
                center_x - radius, center_y,
                fill="#7e22ce", outline="#581c87", width=2,
            )
            if self.cell_size >= 40:
                self.canvas.create_text(center_x, center_y, text="!", fill="white", font=("Arial", 10, "bold"))

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = random.choice(['Up', 'Down', 'Left', 'Right'])
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size with food, opponents, and toxic traps.
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=3, num_traps=8)
    root.mainloop()
