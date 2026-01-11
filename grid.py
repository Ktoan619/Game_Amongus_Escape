import pygame
from constants import *

class Cell:
    def __init__(self, c, r):
        self.c = c
        self.r = r
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

class Grid:
    def __init__(self, rows, cols, cell_size):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.matrix = []
        
        self.width_pixel = cols * cell_size
        self.height_pixel = rows * cell_size
        
        # Assets mặc định
        # self.floor_img = pygame.Surface((cell_size, cell_size))
        self.floor_img = pygame.image.load('assets/floor.png').convert()
        self.floor_img = pygame.transform.scale(self.floor_img, (cell_size, cell_size))
        # self.floor_img.fill(COLOR_FLOOR)
        self.wall_img = pygame.Surface((cell_size, 8))
        self.wall_img.fill(COLOR_WALL)

        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                row_cells.append(Cell(c, r))
            self.matrix.append(row_cells)

    # --- THÊM HÀM NÀY ĐỂ SỬA LỖI DEEPCOPY ---
    def clone(self):
        """Tạo một bản sao của Grid mà không crash vì pygame.Surface"""
        # 1. Tạo Grid mới (nó sẽ tự tạo surface mới trong __init__)
        new_grid = Grid(self.rows, self.cols, self.cell_size)
        
        # 2. Sao chép dữ liệu tường từ grid cũ sang grid mới
        new_grid.set_wall_data(self.get_wall_data())
        
        # 3. (Tùy chọn) Nếu grid cũ dùng ảnh load từ file, gán tham chiếu ảnh sang
        # Để không phải load lại từ đĩa cứng
        new_grid.floor_img = self.floor_img
        new_grid.wall_img = self.wall_img
        
        return new_grid
    # ----------------------------------------

    def remove_wall(self, c1, r1, c2, r2):
        dx = c1 - c2
        dy = r1 - r2
        if dx == 1: 
            self.matrix[r1][c1].walls['left'] = False
            self.matrix[r2][c2].walls['right'] = False
        elif dx == -1:
            self.matrix[r1][c1].walls['right'] = False
            self.matrix[r2][c2].walls['left'] = False
        if dy == 1: 
            self.matrix[r1][c1].walls['top'] = False
            self.matrix[r2][c2].walls['bottom'] = False
        elif dy == -1:
            self.matrix[r1][c1].walls['bottom'] = False
            self.matrix[r2][c2].walls['top'] = False

    def get_wall_data(self):
        data = []
        for r in range(self.rows):
            row_data = []
            for c in range(self.cols):
                # Quan trọng: copy dict để không bị tham chiếu trùng
                row_data.append(self.matrix[r][c].walls.copy())
            data.append(row_data)
        return data

    def set_wall_data(self, data):
        for r in range(self.rows):
            for c in range(self.cols):
                self.matrix[r][c].walls = data[r][c].copy()

    def draw_background(self, surface, center_x, center_y):
        start_x = center_x - (self.width_pixel // 2)
        start_y = center_y - (self.height_pixel // 2)

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.matrix[r][c]
                sx = start_x + c * self.cell_size
                sy = start_y + r * self.cell_size

                surface.blit(self.floor_img, (sx, sy))
                if cell.walls['top']: surface.blit(self.wall_img, (sx, sy))
                if cell.walls['left']: 
                    s = pygame.transform.rotate(self.wall_img, 90)
                    surface.blit(s, (sx, sy))
                if cell.walls['right']:
                    s = pygame.transform.rotate(self.wall_img, 90)
                    surface.blit(s, (sx + self.cell_size - s.get_width(), sy))

    def draw_foreground(self, surface, center_x, center_y):
        start_x = center_x - (self.width_pixel // 2)
        start_y = center_y - (self.height_pixel // 2)

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.matrix[r][c]
                sx = start_x + c * self.cell_size
                sy = start_y + r * self.cell_size
                
                if cell.walls['bottom']:
                    surface.blit(self.wall_img, (sx, sy + self.cell_size - self.wall_img.get_height()))