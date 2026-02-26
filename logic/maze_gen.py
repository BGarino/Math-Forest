"""
Procedural maze generator using Recursive Backtracker (DFS).
Difficulty scales with level number.
"""
import random


class MazeGenerator:
    WALL   = 1
    PATH   = 0
    START  = 2
    END    = 3
    ANIMAL = 4

    def __init__(self, level: int = 1):
        self.level = level
        self.width, self.height = self._size_for_level(level)
        self.grid = [[self.WALL] * self.width for _ in range(self.height)]
        self.animal_positions = []
        # Start is always top-left passable cell, end bottom-right
        self.start_pos = (1, 1)
        self.end_pos   = (self.width - 2, self.height - 2)

    def _size_for_level(self, level):
        # Odd dimensions so DFS carving works correctly
        base_w = 7  + (level // 10) * 2
        base_h = 9  + (level // 10) * 2
        w = min(base_w, 25)
        h = min(base_h, 35)
        # Enforce odd
        if w % 2 == 0: w += 1
        if h % 2 == 0: h += 1
        return w, h

    def generate(self) -> list:
        """Return grid with START, END and ANIMAL cells marked."""
        sx, sy = self.start_pos
        self._carve(sx, sy)
        # Mark start / end
        self.grid[sy][sx] = self.START
        ex, ey = self.end_pos
        self.grid[ey][ex] = self.END
        self._place_animals()
        return self.grid

    def _carve(self, cx, cy):
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        self.grid[cy][cx] = self.PATH
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                if self.grid[ny][nx] == self.WALL:
                    # Carve the wall between current and next
                    self.grid[cy + dy // 2][cx + dx // 2] = self.PATH
                    self._carve(nx, ny)

    def _place_animals(self):
        num_animals = min(3 + self.level // 3, 12)
        path_cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.grid[y][x] == self.PATH
        ]
        random.shuffle(path_cells)
        sx, sy = self.start_pos
        ex, ey = self.end_pos
        placed = 0
        for (x, y) in path_cells:
            if placed >= num_animals:
                break
            if (x, y) not in [(sx, sy), (ex, ey)]:
                self.grid[y][x] = self.ANIMAL
                self.animal_positions.append((x, y))
                placed += 1

    def get_animal_count(self):
        return len(self.animal_positions)
