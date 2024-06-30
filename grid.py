import pygame
from colors import Colors

class Grid:
    def __init__(self):
        self.num_rows = 20
        self.num_cols = 10
        self.cell_size = 30
        self.grid = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.colors = Colors.get_cell_colors()
        self.update_rects()

    def update_rects(self):
        self.cell_rects = [[pygame.Rect(column * self.cell_size + 11, row * self.cell_size + 11, 
                          self.cell_size - 1, self.cell_size - 1) for column in range(self.num_cols)] 
                          for row in range(self.num_rows)]

    def is_inside(self, row, column):
        return 0 <= row < self.num_rows and 0 <= column < self.num_cols

    def is_empty(self, row, column):
        return self.grid[row][column] == 0

    def is_row_full(self, row):
        return all(self.grid[row])

    def clear_row(self, row):
        self.grid[row] = [0] * self.num_cols

    def move_row_down(self, row, num_rows):
        self.grid[row + num_rows] = self.grid[row]
        self.grid[row] = [0] * self.num_cols

    def clear_full_rows(self):
        completed = 0
        for row in range(self.num_rows - 1, -1, -1):
            if self.is_row_full(row):
                self.clear_row(row)
                completed += 1
            elif completed > 0:
                self.move_row_down(row, completed)
        return completed

    def reset(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                self.grid[row][column] = 0

    def draw(self, screen):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                pygame.draw.rect(screen, self.colors[self.grid[row][column]], self.cell_rects[row][column])

