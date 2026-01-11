from re import S
from tkinter import W
import pygame
import os
import sys

# --- IMPORT LOGIC GAME ---
from gameworld import GameWorld
from algorithms import MapGenerator, find_solution_path

# --- XỬ LÝ CONSTANTS ---
# Sử dụng constants.py của bạn
from constants import * # --- CÁC HÀM HỖ TRỢ ---
def draw_img_center(surface, img, x, y):
    if img:
        rect = img.get_rect(center=(x, y))
        surface.blit(img, rect)

# --- CLASS BUTTON ---
class Button:
    def __init__(self, x, y, text_input, font, base_color, hovering_color, image=None, sound=None, scale=1.1):
        self.game_mode = None
        self.x_pos = x
        self.y_pos = y
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self.sound = sound
        self.scale_factor = scale 
        # 1. Xử lý Text
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

        # 2. Xử lý Hình ảnh
        if image is None:
            image = self.text

        self.image_original = image
        
        # Chỉ scale nếu là ảnh (không phải text render)
        if image != self.text:
            width = self.image_original.get_width()
            height = self.image_original.get_height()
            self.image_hover = pygame.transform.scale(self.image_original, (int(width * self.scale_factor), int(height * self.scale_factor)))
        else:
            self.image_hover = self.image_original

        self.image = self.image_original
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_input(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def change_color(self, position):
        if self.check_input(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
            self.image = self.image_hover
            self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
            self.image = self.image_original
            self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def play_sound(self):
        if self.sound:
            self.sound.play()

# --- GAME STATE MANAGER ---
class GameStateManager: 
    def __init__(self, current_state):
        self.game_state = current_state
    
    def change_state(self, new_state):
        self.game_state = new_state
    
    def get_state(self):
        return self.game_state

# --- GAME CONTROLLER ---
class GameController:

    def load_character_assets(self):
        """Hàm này dùng để load lại ảnh nhân vật dựa trên màu da hiện tại"""
        if self.skin_color == "red":
            # List ảnh cho màu đỏ
            self.p1_imgs = [f"assets/char_red/red{i}.png" for i in range(1, 10)]
        elif self.skin_color == "purple":
            # List ảnh cho màu tím (bạn đang dùng folder assets/char_purple)
            self.p1_imgs = [f"assets/char_purple/purple{i}.png" for i in range(1, 10)]

            
        # Lưu ý: Cần đảm bảo file ảnh tồn tại và tên đúng định dạng để tránh lỗi

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Sử dụng RESOLUTION từ constants.py
        self.screen = pygame.display.set_mode(RESOLUTION)
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()

        try:
            # 1. Load file nhạc (nhớ thay đổi tên file cho đúng với file bạn có)
            # Khuyên dùng .mp3 hoặc .ogg cho nhạc nền
            pygame.mixer.music.load("assets/background_music.mp3") 
            
            # 2. Chỉnh âm lượng nhỏ hơn tiếng click button (0.0 đến 1.0)
            pygame.mixer.music.set_volume(0.3) 
            
            # 3. Phát lặp lại vô tận (-1 nghĩa là loop forever)
            pygame.mixer.music.play(loops=-1)
            
        except pygame.error as e:
            pass
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.start_sound = pygame.mixer.Sound("assets/start.mp3")
        except Exception as e:
            self.start_sound = None
        # --- TÍCH HỢP USER MANAGER ---

        self.skin_color = "red"

        self.p1_imgs = []
        if self.skin_color == "red" :
            self.p1_imgs = ["assets/char_red/red1.png", "assets/char_red/red2.png", "assets/char_red/red3.png", "assets/char_red/red4.png"
                       ,"assets/char_red/red5.png", "assets/char_red/red6.png"
                       , "assets/char_red/red7.png", "assets/char_red/red8.png", "assets/char_red/red9.png"]
        
        self.p2_imgs = ["assets/char_purple/purple1.png", "assets/char_purple/purple2.png", "assets/char_purple/purple3.png", "assets/char_purple/purple4.png",
                       "assets/char_purple/purple5.png", "assets/char_purple/purple6.png"
                       , "assets/char_purple/purple7.png", "assets/char_purple/purple8.png", "assets/char_purple/purple9.png"
        ]



        self.m_imgs = ["assets/char_black/black1.png", "assets/char_black/black2.png", "assets/char_black/black3.png", "assets/char_black/black4.png",
                       "assets/char_black/black5.png", "assets/char_black/black6.png"
                       , "assets/char_black/black7.png", "assets/char_black/black8.png", "assets/char_black/black9.png"
        ]
        self.world1 = None
        self.world2 = None
        self.game_mode = "1P" # Mặc định
        self.diff = 'EASY'   # Mặc định
        self.game_state_manager = GameStateManager("Menu")
        self.font_menu = pygame.font.SysFont("assets/fonts/PixeloidSansBold.ttf", 50) 
        self.race_maps = []       # List chứa data của 3 map
        self.p1_map_index = 0     # P1 đang ở map số mấy (0, 1, 2)
        self.p2_map_index = 0     # P2 đang ở map số mấy (0, 1, 2)
        try:
            self.click_sound = pygame.mixer.Sound("assets/button_clicksound.wav") 
        except:
            self.click_sound = None

        # Load menu background
        self.menu_bg = pygame.image.load("assets/menu_back.png").convert_alpha()
        self.menu_bg = pygame.transform.scale(self.menu_bg, (WINDOW_WIDTH, WINDOW_HEIGHT)) if self.menu_bg else None
        
        # Button Image
        btn_img = pygame.image.load("assets/red_button.png").convert_alpha()
        btn_img = pygame.transform.scale(btn_img, (320, 180))
        diff_btn_img = pygame.image.load("assets/red_button.png").convert_alpha()
        diff_btn_img = pygame.transform.scale(diff_btn_img, (300, 100))
        p1_img = pygame.image.load("assets/1p_img.png").convert_alpha()
        p1_img = pygame.transform.scale(p1_img, (320, 180))
        p2_img = pygame.image.load("assets/2p_img.png").convert_alpha()
        p2_img = pygame.transform.scale(p2_img, (320, 180))
        
        setting_img = pygame.image.load("assets/setting.png").convert_alpha()
        setting_img = pygame.transform.scale(setting_img, (100, 100))

        self.ingame_setting_img = pygame.image.load("assets/system_back_2.png").convert_alpha()
        self.ingame_setting_img = pygame.transform.scale(self.ingame_setting_img, (500, 700))
        # Load game name
        self.game_name_img = pygame.image.load("assets/Among_Us_Remastered.png").convert_alpha()
        self.game_name_img = pygame.transform.scale(self.game_name_img, (800, 450))

        self.system_back = pygame.image.load("assets/system_back.png").convert_alpha()
        self.system_back = pygame.transform.scale(self.system_back, (WINDOW_WIDTH-80, WINDOW_HEIGHT-45))

        self.available_skins = ["red", "purple"]
        self.current_skin_index = 0
        self.skin_color = self.available_skins[self.current_skin_index]
        
        # 2. Gọi hàm load assets lần đầu tiên
        self.load_character_assets()

        # 3. Load hình ảnh đại diện cho skin (Lấy ảnh đầu tiên làm ảnh đứng yên)
        # Chúng ta cần load ảnh đại diện cho nút bấm
        self.skin_previews = {}
        try:
            red_img = pygame.image.load("assets/char_red/red1.png").convert_alpha()
            purple_img = pygame.image.load("assets/char_purple/purple1.png").convert_alpha()
            black_img = pygame.image.load("assets/char_black/black1.png").convert_alpha()
            
            # Scale to lên cho đẹp (Ví dụ: gấp 3 lần)
            scale_preview = 2
            self.skin_previews["red"] = pygame.transform.scale(red_img, (red_img.get_width()*scale_preview, red_img.get_height()*scale_preview))
            self.skin_previews["purple"] = pygame.transform.scale(purple_img, (purple_img.get_width()*scale_preview, purple_img.get_height()*scale_preview))
        except:
            print("Lỗi load ảnh preview skin")
            # Tạo ảnh placeholder nếu lỗi
            self.skin_previews = {k: pygame.Surface((50,50)) for k in self.available_skins}
        
        # 4. Tạo nút Skin (Đặt ở bên trái hoặc phải menu)
        # Lấy ảnh tương ứng skin hiện tại
        current_preview_img = self.skin_previews[self.skin_color]
        
        self.btn_skin_change = Button(
            x= 1450, y= 500,  # Vị trí góc trái dưới
            text_input="", font=self.font_menu, # Không cần chữ
            base_color="White", hovering_color="White",
            image=current_preview_img, 
            sound=self.click_sound,
            scale=1.1 # Phóng to nhẹ khi hover
        )

        self.btn_1p = Button(
            x = 400 , y= 450,
            text_input="", font=self.font_menu,
            base_color="White", hovering_color="Green",
            image=p1_img, sound=self.click_sound
        )

        self.btn_2p = Button(
            x = 400 + 320 + 320 , y= 450,
            text_input="", font=self.font_menu,
            base_color="White", hovering_color="Green",
            image=p2_img, sound=self.click_sound
        )
        
        # Khởi tạo nút
        self.btn_start = Button(
            x= WINDOW_WIDTH//2 , y= 500, 
            text_input="START", font=self.font_menu, 
            base_color="White", hovering_color="Green", 
            image=btn_img, sound=self.click_sound
        )
        
        self.btn_quit = Button(
            x= WINDOW_WIDTH//2 , y= 700, 
            text_input="QUIT", font=self.font_menu, 
            base_color="White", hovering_color="Red", 
            image=btn_img, sound=self.click_sound
        )

        self.btn_settings = Button(
            x= 200 , y= WINDOW_HEIGHT//2, 
            text_input="", font=self.font_menu, 
            base_color="White", hovering_color="Yellow", 
            image=setting_img, sound=self.click_sound, scale=1.0
        )
        self.btn_easy = Button(
            x= 700, y=450 - 120, 
            text_input="EASY", font=self.font_menu, 
            base_color="White", hovering_color="Green", 
            image=diff_btn_img, sound=self.click_sound
        )

        self.btn_medium = Button(
            x= 700, y=450, 
            text_input="MEDIUM", font=self.font_menu, 
            base_color="White", hovering_color="Yellow", 
            image=diff_btn_img, sound=self.click_sound
        )

        self.btn_hard = Button(
            x= 700, y = 450 + 120, 
            text_input="HARD", font=self.font_menu, 
            base_color="White", hovering_color="Red", 
            image=diff_btn_img, sound=self.click_sound
        )

        self.btn_easy_ingame = Button(
            x= WINDOW_WIDTH/3 - 150, y=450 - 120, 
            text_input="EASY", font=self.font_menu, 
            base_color="White", hovering_color="Green", 
            image=diff_btn_img, sound=self.click_sound
        )

        self.btn_medium_ingame = Button(
            x= WINDOW_WIDTH/3 - 150, y=450, 
            text_input="MEDIUM", font=self.font_menu, 
            base_color="White", hovering_color="Yellow", 
            image=diff_btn_img, sound=self.click_sound
        )

        self.btn_hard_ingame = Button(
            x= WINDOW_WIDTH/3 - 150, y = 450 + 120, 
            text_input="HARD", font=self.font_menu, 
            base_color="White", hovering_color="Red", 
            image=diff_btn_img, sound=self.click_sound
        )
    # --- CÁC HÀM LOGIC ---

    def handle_skin_change(self):
        self.current_skin_index = (self.current_skin_index + 1) % len(self.available_skins)
        
        # 2. Cập nhật tên màu
        self.skin_color = self.available_skins[self.current_skin_index]
        
        # 3. Load lại bộ asset game (QUAN TRỌNG)
        self.load_character_assets()
        
        # 4. Cập nhật hình ảnh cho cái nút
        new_image = self.skin_previews[self.skin_color]
        
        # Cập nhật trực tiếp vào object button
        self.btn_skin_change.image_original = new_image
        self.btn_skin_change.image = new_image # Cập nhật ảnh hiện tại
        
        # Cập nhật lại ảnh hover (resize lại ảnh mới)
        width = new_image.get_width()
        height = new_image.get_height()
        self.btn_skin_change.image_hover = pygame.transform.scale(
            new_image, 
            (int(width * self.btn_skin_change.scale_factor), int(height * self.btn_skin_change.scale_factor))
        )
        # Reset rect để ảnh không bị lệch
        self.btn_skin_change.rect = self.btn_skin_change.image.get_rect(center=(self.btn_skin_change.x_pos, self.btn_skin_change.y_pos))
    def handle_1player_mode(self):

        raw, p, m, e = MapGenerator.generate_valid_level(ROWS, COLS, CELL_SIZE, difficulty='HARD', wall_remove_ratio=0.5)
        self.world1 = GameWorld(raw, p, m, e, self.p1_imgs, self.m_imgs, 'HARD')
        
        self.world2 = None
        self.game_mode = "1P" 
        self.game_state_manager.change_state("Playing")
    def start_new_game(self, mode):
        self.game_mode = mode
        
        if mode == "1P":
            # Logic cũ cho 1 Player
            diff = self.diff
            raw, p, m, e = MapGenerator.generate_valid_level(ROWS, COLS, CELL_SIZE, difficulty=diff, wall_remove_ratio=0.5)
            self.world1 = GameWorld(raw, p, m, e, self.p1_imgs, self.m_imgs, diff)
            self.world2 = None
            
        elif mode == "2P":
            # --- LOGIC MỚI CHO 2 PLAYERS (RACE MODE) ---
            self.race_maps = [] # Reset list map
            self.p1_map_index = 0
            self.p2_map_index = 0
            
            # Sinh trước 3 Map
            print("Generating 3 maps for Race Mode...")
            for i in range(3):
                # Map đua thường để EASY hoặc MEDIUM cho nhanh
                raw, p, m, e = MapGenerator.generate_valid_level(ROWS, COLS, CELL_SIZE, difficulty='EASY', wall_remove_ratio=0.5)
                self.race_maps.append((raw, p, m, e))
            
            # Load Map đầu tiên (Index 0) cho cả 2 người
            map_data = self.race_maps[0]
            # Unpack data: raw, p, m, e
            self.world1 = GameWorld(map_data[0], map_data[1], map_data[2], map_data[3], self.p1_imgs, self.m_imgs, 'EASY')
            self.world2 = GameWorld(map_data[0], map_data[1], map_data[2], map_data[3], self.p2_imgs, self.m_imgs, 'EASY')

        if self.start_sound:
            self.start_sound.play()
            
        self.game_state_manager.change_state("Playing")
        

            

        self.game_state_manager.change_state("Playing")
    def save_current_game(self):
        """Lưu game 1P đang chơi dở"""
        if self.game_mode == "1P" and self.world1:
            if self.world1.state == "PLAYING":
                self.user_manager.save_game_state(self.world1.export_data())
            else:
                self.user_manager.clear_save()

    def visualize(self):
        current_state = self.game_state_manager.get_state()
        mouse_pos = pygame.mouse.get_pos()
        self.screen.blit(self.menu_bg, (0, 0))

        if current_state == "Menu":

            draw_img_center(self.screen, self.game_name_img, WINDOW_WIDTH//2, 175)
            for button in [self.btn_start, self.btn_quit, self.btn_settings]:
                button.change_color(mouse_pos)
                button.update(self.screen)
            self.btn_skin_change.change_color(mouse_pos)
            self.btn_skin_change.update(self.screen)

        elif current_state == "CHOOSING":
            if self.menu_bg: self.screen.blit(self.menu_bg, (0, 0))
            draw_img_center(self.screen, self.system_back, WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
            
            for button in [self.btn_1p, self.btn_2p]:
                button.change_color(mouse_pos)
                button.update(self.screen)

        elif current_state == "Playing":
            # Sử dụng màu nền hoặc ảnh nền
            self.screen.fill("black") 
            
            if self.game_mode == "1P" and self.world1:
                draw_img_center(self.screen, self.menu_bg, WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
                self.world1.draw(self.screen, WINDOW_WIDTH //3*2, WINDOW_HEIGHT // 2)
                draw_img_center(self.screen, self.ingame_setting_img, WINDOW_WIDTH/3-150, WINDOW_HEIGHT//2)
                for button in [self.btn_easy_ingame, self.btn_medium_ingame, self.btn_hard_ingame]:
                    button.change_color(mouse_pos)
                    button.update(self.screen)

            
            elif self.game_mode == "2P" and self.world1 and self.world2:
                # Vẽ game 2 người (Chia đôi)
                draw_img_center(self.screen, self.menu_bg, WINDOW_WIDTH//4, WINDOW_HEIGHT//2)
                self.world1.draw(self.screen, WINDOW_WIDTH * 0.25, WINDOW_HEIGHT // 2)
                self.world2.draw(self.screen, WINDOW_WIDTH * 0.75, WINDOW_HEIGHT // 2)
                pygame.draw.line(self.screen, "White", (WINDOW_WIDTH // 2, 0), (WINDOW_WIDTH // 2, WINDOW_HEIGHT), 2)
                
                # Logic đua 2 người
                if self.world1.state == "WON" and self.world2.state == "PLAYING":
                    self.world2.state = "LOST"; self.world2.message = "TOO SLOW!"
                elif self.world2.state == "WON" and self.world1.state == "PLAYING":
                    self.world1.state = "LOST"; self.world1.message = "TOO SLOW!"
        elif current_state == "CHOOSING_DIFF":
            # 1. Vẽ hình nền menu chính
            if self.menu_bg: self.screen.blit(self.menu_bg, (0, 0))
            
            # 2. Vẽ tấm bảng system_back (Giống màn hình chọn mode)
            draw_img_center(self.screen, self.system_back, WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
            
            # 4. Vẽ các nút độ khó
            for button in [self.btn_easy, self.btn_medium, self.btn_hard]:
                button.change_color(mouse_pos)
                button.update(self.screen)
        
        pygame.display.update()

    def run(self):
        run = True
        while run:
            mouse_pos = pygame.mouse.get_pos()
            current_state = self.game_state_manager.get_state()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()
                
                # --- XỬ LÝ EVENT MENU ---
                if event.type == pygame.KEYDOWN:
                    # Phím M: Quay về Menu từ bất kỳ đâu (Settings, Choosing, Playing)
                    if event.key == pygame.K_m and current_state != "Menu":
                        self.game_state_manager.change_state("Menu")
                        continue
                if current_state == "Menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.btn_start.check_input(mouse_pos):
                            self.btn_start.play_sound()
                            self.game_state_manager.change_state("CHOOSING")
                        if self.btn_quit.check_input(mouse_pos):
                            self.btn_quit.play_sound()
                            run = False
                            pygame.quit()
                            sys.exit()
                        if self.btn_skin_change.check_input(mouse_pos):
                            self.btn_skin_change.play_sound()
                            self.handle_skin_change()
                
                # --- XỬ LÝ EVENT CHOOSING ---
                elif current_state == "CHOOSING":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.btn_1p.check_input(mouse_pos):
                            self.btn_1p.play_sound()
                            self.game_state_manager.change_state("CHOOSING_DIFF")
                            
                        if self.btn_2p.check_input(mouse_pos):
                            self.btn_2p.play_sound()
                            # Gọi hàm logic thông qua self.
                            self.start_new_game("2P")
                elif current_state == "CHOOSING_DIFF":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        
                        # Xử lý nút EASY
                        if self.btn_easy.check_input(mouse_pos):
                            self.btn_easy.play_sound()
                            self.diff = 'EASY'
                            self.start_new_game("1P")

                        # Xử lý nút MEDIUM
                        elif self.btn_medium.check_input(mouse_pos):
                            self.btn_medium.play_sound()
                            self.diff = 'MEDIUM'
                            self.start_new_game("1P")

                        # Xử lý nút HARD
                        elif self.btn_hard.check_input(mouse_pos):
                            self.btn_hard.play_sound()
                            self.diff = 'HARD'
                            self.start_new_game("1P")
                # --- XỬ LÝ EVENT PLAYING ---
                elif current_state == "Playing":
                    if event.type == pygame.KEYDOWN:
                        # ESC: Lưu và về Menu
                        if event.key == pygame.K_ESCAPE:
                            self.save_current_game()
                            self.game_state_manager.change_state("Menu")
                        
                        # SPACE: Map mới
                        if event.key == pygame.K_SPACE:
                            self.start_new_game(self.game_mode)
                        
                        # ĐIỀU KHIỂN
                        if self.game_mode == "1P" and self.world1:

                            if event.key == pygame.K_UP: self.world1.handle_input('top')
                            elif event.key == pygame.K_DOWN: self.world1.handle_input('bottom')
                            elif event.key == pygame.K_LEFT: self.world1.handle_input('left')
                            elif event.key == pygame.K_RIGHT: self.world1.handle_input('right')
                            elif event.key == pygame.K_u: self.world1.undo()
                            elif event.key == pygame.K_r: self.world1.reset_level()
                            elif event.key == pygame.K_t: self.world1.solve_level()

                            
                        elif self.game_mode == "2P" and self.world1 and self.world2:
                            # P1 (WASD)
                            if event.key == pygame.K_w: self.world1.handle_input('top')
                            elif event.key == pygame.K_s: self.world1.handle_input('bottom')
                            elif event.key == pygame.K_a: self.world1.handle_input('left')
                            elif event.key == pygame.K_d: self.world1.handle_input('right')
                            # P2 (Arrows)
                            if event.key == pygame.K_UP: self.world2.handle_input('top')
                            elif event.key == pygame.K_DOWN: self.world2.handle_input('bottom')
                            elif event.key == pygame.K_LEFT: self.world2.handle_input('left')
                            elif event.key == pygame.K_RIGHT: self.world2.handle_input('right')

                            if self.world1.state == "WON":
                                self.p1_map_index += 1 # Qua màn
                                if self.p1_map_index < 3:
                                    # Load map tiếp theo
                                    print(f"P1 advanced to Map {self.p1_map_index + 1}")
                                    data = self.race_maps[self.p1_map_index]
                                    self.world1 = GameWorld(data[0], data[1], data[2], data[3], self.p1_imgs, self.m_imgs, 'EASY')
                                else:
                                    # P1 đã thắng cả 3 map -> END GAME
                                    self.world1.message = "CHAMPION!"
                                    self.world2.state = "LOST"
                                    self.world2.message = "DEFEAT"
                            
                            elif self.world1.state == "LOST":
                                # Thua map -> Reset lại map hiện tại ngay lập tức
                                print("P1 Died -> Restarting Map")
                                data = self.race_maps[self.p1_map_index]
                                self.world1 = GameWorld(data[0], data[1], data[2], data[3], self.p1_imgs, self.m_imgs, 'EASY')

                            # --- KIỂM TRA NGƯỜI CHƠI 2 ---
                            if self.world2.state == "WON":
                                self.p2_map_index += 1 # Qua màn
                                if self.p2_map_index < 3:
                                    # Load map tiếp theo
                                    print(f"P2 advanced to Map {self.p2_map_index + 1}")
                                    data = self.race_maps[self.p2_map_index]
                                    self.world2 = GameWorld(data[0], data[1], data[2], data[3], self.p2_imgs, self.m_imgs, 'EASY')
                                else:
                                    # P2 đã thắng cả 3 map -> END GAME
                                    self.world2.message = "CHAMPION!"
                                    self.world1.state = "LOST"
                                    self.world1.message = "DEFEAT"
                            elif self.world2.state == "LOST":
                                # Thua map -> Reset lại map hiện tại ngay lập tức
                                print("P2 Died -> Restarting Map")
                                data = self.race_maps[self.p2_map_index]
                                self.world2 = GameWorld(data[0], data[1], data[2], data[3], self.p2_imgs, self.m_imgs, 'EASY')

                elif self.world2.state == "LOST":
                    # Thua map -> Reset lại map hiện tại ngay lập tức
                    print("P2 Died -> Restarting Map")
                    data = self.race_maps[self.p2_map_index]
                    self.world2 = GameWorld(data[0], data[1], data[2], data[3], self.p2_imgs, self.m_imgs, 'EASY')

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Xử lý nút độ khó in-game (chỉ 1P)
                        if self.game_mode == "1P" and self.world1:
                            if self.btn_easy_ingame.check_input(mouse_pos):
                                self.btn_easy_ingame.play_sound()
                                self.diff = 'EASY'
                                self.start_new_game("1P")
                            elif self.btn_medium_ingame.check_input(mouse_pos):
                                self.btn_medium_ingame.play_sound()
                                self.diff = 'MEDIUM'
                                self.start_new_game("1P")
                            elif self.btn_hard_ingame.check_input(mouse_pos):
                                self.btn_hard_ingame.play_sound()
                                self.diff = 'HARD'
                                self.start_new_game("1P")

            self.visualize()
            self.clock.tick(60)

if __name__ == "__main__":
    game = GameController()
    game.run()