import pygame
import math
from constants import *
from algorithms import get_mummy_next_pos

class Character:
    def __init__(self, c, r, img_paths=None, speed=4):
        # 1. Toạ độ Logic
        self.c = c
        self.r = r
        
        # 2. Toạ độ Visual
        self.pixel_x = 0 
        self.pixel_y = 0
        self.initialized = False 

        # 3. Chuyển động
        self.speed = speed
        self.is_moving = False

        # 4. Animation
        self.sprites = []
        self.current_frame = 0
        self.flip = False
        self.color = COLOR_PLAYER
        
        self.ANIMATION_STEPS = 9 

        if img_paths:
            for p in img_paths:
                try:
                    img = pygame.image.load(p)
                    self.sprites.append(pygame.transform.scale(img, (int(CELL_SIZE*0.8), int(CELL_SIZE*0.8))))
                except: pass
        
    def get_pixel_target(self, grid, cx, cy):
        start_x = cx - (grid.width_pixel // 2)
        start_y = cy - (grid.height_pixel // 2)
        px = start_x + (self.c * grid.cell_size) + (grid.cell_size // 2)
        py = start_y + (self.r * grid.cell_size) + (grid.cell_size // 2)
        return px, py

    def move(self, direction, grid):
        if self.is_moving: return False

        cell = grid.matrix[self.r][self.c]
        if not cell.walls[direction]:
            if direction == 'top': self.r -= 1
            elif direction == 'bottom': self.r += 1
            elif direction == 'left': 
                self.c -= 1
                self.flip = True  # Lật trái
            elif direction == 'right': 
                self.c += 1
                self.flip = False # Mặt phải
            return True
        return False

    def update_visual(self, grid, cx, cy):
        dest_x, dest_y = self.get_pixel_target(grid, cx, cy)
        
        if not self.initialized:
            self.pixel_x, self.pixel_y = dest_x, dest_y
            self.initialized = True
            return

        dx = dest_x - self.pixel_x
        dy = dest_y - self.pixel_y
        dist = math.sqrt(dx**2 + dy**2)

        if dist > self.speed:
            self.is_moving = True
            angle = math.atan2(dy, dx)
            self.pixel_x += math.cos(angle) * self.speed
            self.pixel_y += math.sin(angle) * self.speed
            
            # Tính frame animation
            progress = (CELL_SIZE - dist) / CELL_SIZE
            progress = max(0.0, min(1.0, progress))
            target_frame_index = int(progress * self.ANIMATION_STEPS)
            if self.sprites:
                self.current_frame = target_frame_index % len(self.sprites)
            
        else:
            self.pixel_x = dest_x
            self.pixel_y = dest_y
            self.is_moving = False
            self.current_frame = 0 

    def draw(self, surface, cx, cy, grid):
        offset_y = -5
        if self.is_moving and self.current_frame % 2 != 0:
            offset_y = -10
            
        draw_x = self.pixel_x
        draw_y = self.pixel_y + offset_y

        if self.sprites:
            img = self.sprites[self.current_frame]
            if self.flip: img = pygame.transform.flip(img, True, False)
            rect = img.get_rect(center=(draw_x, draw_y))
            surface.blit(img, rect)
        else:
            pygame.draw.circle(surface, self.color, (int(draw_x), int(draw_y)), int(CELL_SIZE//3))


class Mummy(Character):
    def __init__(self, c, r, img_paths=None, difficulty='EASY'):
        super().__init__(c, r, img_paths, speed=6)
        self.difficulty = difficulty
        self.color = COLOR_MUMMY
        
        # Hàng đợi chứa các bước đi (List các tuple (col, row))
        self.move_queue = [] 

    def take_turn(self, target, grid):
        """
        Lấy danh sách các bước đi từ algorithms và nạp vào hàng đợi.
        KHÔNG thực hiện logic so sánh/flip ở đây để tránh lỗi.
        """
        # steps là một LIST các tuple: [(3,4), (3,5)]
        steps = get_mummy_next_pos(self.c, self.r, target.c, target.r, grid, self.difficulty)
        
        # Nạp từng bước vào hàng đợi
        for step in steps:
            self.move_queue.append(step)

    def update_visual(self, grid, cx, cy):
        """
        Xử lý di chuyển từng bước và FLIP tại đây
        """
        # Chỉ đi bước tiếp theo khi đã đứng yên
        if not self.is_moving and self.move_queue:
            # Lấy toạ độ bước tiếp theo (Giải nén tuple ra 2 biến int)
            next_c, next_r = self.move_queue.pop(0) 
            
            # --- LOGIC FLIP ĐÃ SỬA ---
            # So sánh 2 số nguyên (int vs int) -> Không còn lỗi
            if next_c < self.c: 
                self.flip = True
            elif next_c > self.c: 
                self.flip = False
            
            # Cập nhật toạ độ Logic để nhân vật bắt đầu trượt
            self.c = next_c
            self.r = next_r

        # Gọi logic trượt của class cha
        super().update_visual(grid, cx, cy)

class Exit:
    def __init__(self, c, r, img_path=None):
        self.c = c
        self.r = r
        self.image = None
        try:
            if img_path:
                i = pygame.image.load(img_path)
                self.image = pygame.transform.scale(i, (CELL_SIZE, CELL_SIZE))
        except: pass

    def draw(self, surface, cx, cy, grid):
        start_x = cx - (grid.width_pixel // 2)
        start_y = cy - (grid.height_pixel // 2)
        px = start_x + (self.c * grid.cell_size) + (grid.cell_size // 2)
        py = start_y + (self.r * grid.cell_size) + (grid.cell_size // 2)
        
        if self.image:
            rect = self.image.get_rect(center=(px, py))
            surface.blit(self.image, rect)
        else:
            size = int(grid.cell_size * 0.6)
            pygame.draw.rect(surface, COLOR_EXIT, (px-size//2, py-size//2, size, size), 0)
            pygame.draw.rect(surface, (0,0,0), (px-size//2, py-size//2, size, size), 2)