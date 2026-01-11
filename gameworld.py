import pygame

from constants import *
from entities import Character, Mummy, Exit
from grid import Grid
from algorithms import find_solution_path

def draw_img_center(surface, img, x, y):
    if img:
        rect = img.get_rect(center=(x, y))
        surface.blit(img, rect)

class GameWorld:
    def __init__(self, grid_data, p_pos, m_pos, e_pos, p_imgs, m_imgs, difficulty):
        # 1. Tạo bản sao Grid
        self.grid = grid_data.clone()
        
        # Load background
        try:
            self.back = pygame.image.load('assets/back.png').convert()
            self.back = pygame.transform.scale(self.back, (700, 700))
        except:
            self.back = None

        # 2. Khởi tạo thực thể
        self.player = Character(p_pos[0], p_pos[1], p_imgs)
        self.mummy = Mummy(m_pos[0], m_pos[1], m_imgs, difficulty)
        
        # Fallback load ảnh door
        try:
            self.exit_gate = Exit(e_pos[0], e_pos[1], 'assets/vent.png')
            # Resize ảnh vent nếu cần
            if self.exit_gate.image:
                self.exit_gate.image = pygame.transform.scale(self.exit_gate.image, (CELL_SIZE-5, CELL_SIZE-5))
        except:
            self.exit_gate = Exit(e_pos[0], e_pos[1], None)
        
        # 3. Trạng thái Game
        self.state = "PLAYING" # PLAYING, WON, LOST
        self.message = ""
        
        # 4. Lưu vị trí ban đầu
        self.start_p_pos = (p_pos[0], p_pos[1])
        self.start_m_pos = (m_pos[0], m_pos[1])

        # 5. Lưu lịch sử
        self.history = []

        # 6. Biến Auto
        self.auto_moves = []
        self.auto_timer = 0

        # --- TỰ ĐỘNG TẢI ÂM THANH THUA TẠI ĐÂY ---
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.lose_sound = pygame.mixer.Sound("assets/lose.mp3")
        except Exception as e:

            self.lose_sound = None

    def trigger_loss(self):
        """Xử lý khi bị bắt: Dừng game và phát nhạc"""
        if self.state != "LOST": # Chỉ kích hoạt 1 lần
            self.state = "LOST"
            self.auto_moves = []
            self.mummy.move_queue = [] # Dừng Mummy ngay lập tức
            
            # Phát nhạc
            if self.lose_sound:
                self.lose_sound.play()

    def save_state(self):
        snapshot = {
            'p_c': self.player.c, 'p_r': self.player.r, 'p_flip': self.player.flip,
            'm_c': self.mummy.c, 'm_r': self.mummy.r, 'm_flip': self.mummy.flip,
            'game_state': self.state
        }
        self.history.append(snapshot)

    def undo(self):
        if self.player.is_moving or self.mummy.is_moving: return

        if len(self.history) > 0:
            prev = self.history.pop()
            
            self.player.c = prev['p_c']; self.player.r = prev['p_r']; self.player.flip = prev['p_flip']
            self.player.initialized = False
            
            self.mummy.c = prev['m_c']; self.mummy.r = prev['m_r']; self.mummy.flip = prev['m_flip']
            self.mummy.initialized = False

            self.state = prev['game_state']
            self.message = ""
            self.auto_moves = []
            self.mummy.move_queue = [] # Xóa hàng đợi di chuyển cũ của mummy

    def reset_level(self):
        self.player.c = self.start_p_pos[0]; self.player.r = self.start_p_pos[1]; self.player.initialized = False
        self.mummy.c = self.start_m_pos[0]; self.mummy.r = self.start_m_pos[1]; self.mummy.initialized = False
        
        self.state = "PLAYING"
        self.message = ""
        self.history.clear()
        self.auto_moves = []
        self.mummy.move_queue = []

    def solve_level(self):
        if self.state != "PLAYING": return
        print("Solving...")
        path = find_solution_path(
            self.grid, 
            (self.player.c, self.player.r), 
            (self.mummy.c, self.mummy.r), 
            (self.exit_gate.c, self.exit_gate.r),
            self.mummy.difficulty
        )
        if path:
            print(f"Solution found: {len(path)} steps")
            self.auto_moves = path
        else:
            print("No solution found!")
            self.message = "STUCK!"

    def handle_input(self, direction):
        if self.state != "PLAYING" or self.player.is_moving: return
        
        # Chặn input nếu Mummy chưa đi xong lượt cũ (để tránh lỗi logic)
        if self.mummy.move_queue: return

        if not self.grid.matrix[self.player.r][self.player.c].walls[direction]:
            self.save_state()
            moved = self.player.move(direction, self.grid)
            
            if moved:
                # Check Win
                if (self.player.c, self.player.r) == (self.exit_gate.c, self.exit_gate.r):
                    self.state = "WON"; self.auto_moves = []; return
                
                # Mummy Turn (Tính toán bước đi)
                self.mummy.take_turn(self.player, self.grid)
                
                # Check Spawn Kill (Nếu Mummy xuất hiện ngay tại chỗ Player đứng)
                if (self.player.c, self.player.r) == (self.mummy.c, self.mummy.r):
                    self.trigger_loss()

    def update(self, cx, cy):
        # Update Visual
        self.player.update_visual(self.grid, cx, cy)
        self.mummy.update_visual(self.grid, cx, cy)

        # Check Va Chạm Liên Tục (khi đang trượt)
        if self.state == "PLAYING":
            if (self.player.c, self.player.r) == (self.mummy.c, self.mummy.r):
                self.trigger_loss()

        # Auto Move Logic
        if self.auto_moves and self.state == "PLAYING":
            if not self.player.is_moving and not self.mummy.is_moving and not self.mummy.move_queue:
                self.auto_timer += 1
                if self.auto_timer > 5:
                    next_move = self.auto_moves.pop(0)
                    self.handle_input(next_move)
                    self.auto_timer = 0

    def draw(self, screen, cx, cy):
        self.update(cx, cy)
        
        draw_img_center(screen, self.back, cx, cy)
        self.grid.draw_background(screen, cx, cy)
        self.exit_gate.draw(screen, cx, cy, self.grid)
        self.player.draw(screen, cx, cy, self.grid)
        self.mummy.draw(screen, cx, cy, self.grid)
        self.grid.draw_foreground(screen, cx, cy)

        if self.state != "PLAYING" or self.message:
            font = pygame.font.SysFont("arial", 60, bold=True)
            txt_str = ""
            if self.state == "WON": txt_str = "VICTORY!"
            elif self.state == "LOST": txt_str = "CAUGHT!"
            if self.message: txt_str = self.message

            if txt_str:
                color = (255, 215, 0) if self.state == "WON" else (255, 50, 50)
                text_surf = font.render(txt_str, True, color)
                screen.blit(text_surf, (cx - text_surf.get_width()//2, cy - (self.grid.height_pixel//2) - 60))

