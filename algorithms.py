import heapq
import random
import sys
from collections import deque
from grid import Grid

# Tăng giới hạn đệ quy cho Python
sys.setrecursionlimit(5000)

# ==========================================
# 1. PATHFINDING ALGORITHMS (CHO MUMMY)
# ==========================================

def a_star_search(start, goal, grid):
    """Tìm đường ngắn nhất (A*) cho HARD AI"""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: abs(start[0]-goal[0]) + abs(start[1]-goal[1])}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        cx, cy = current
        cell = grid.matrix[cy][cx]
        neighbors = [(0,-1,'top'), (0,1,'bottom'), (-1,0,'left'), (1,0,'right')]
        
        for dx, dy, direction in neighbors:
            if cell.walls[direction]: continue
            neighbor = (cx + dx, cy + dy)
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h = abs(neighbor[0]-goal[0]) + abs(neighbor[1]-goal[1])
                f_score[neighbor] = tentative_g + h
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def dfs_search(start, goal, grid):
    """Tìm đường theo chiều sâu (DFS) cho MEDIUM AI."""
    stack = [(start, [start])]
    visited = set()
    
    while stack:
        (cx, cy), path = stack.pop()
        
        if (cx, cy) == goal:
            return path
        
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        
        neighbors = [(0,-1,'top'), (0,1,'bottom'), (-1,0,'left'), (1,0,'right')]
        random.shuffle(neighbors) # Random để tạo sự khó đoán
        
        for dx, dy, direction in neighbors:
            if not grid.matrix[cy][cx].walls[direction]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited:
                    stack.append(((nx, ny), path + [(nx, ny)]))
    return []

# ==========================================
# 2. MUMMY LOGIC CONTROLLER
# ==========================================

def get_mummy_next_pos(mx, my, tx, ty, grid, difficulty='EASY'):
    """
    QUAN TRỌNG: Trả về DANH SÁCH các bước đi (List of tuples).
    Ví dụ: [(3,4), (3,5)] nghĩa là Mummy sẽ đi qua (3,4) rồi đến (3,5).
    """
    steps_to_take = 2
    path_steps = []

    # --- HARD (A*) ---
    if difficulty == 'HARD':
        # A* trả về [start, step1, step2, step3...]
        full_path = a_star_search((mx, my), (tx, ty), grid)
        # Lấy tối đa 2 bước tiếp theo (bỏ index 0 là vị trí hiện tại)
        if len(full_path) > 1:
            path_steps = full_path[1 : steps_to_take + 1]
        
    # --- MEDIUM (DFS) ---
    elif difficulty == 'MEDIUM':
        full_path = dfs_search((mx, my), (tx, ty), grid)
        if len(full_path) > 1:
            path_steps = full_path[1 : steps_to_take + 1]

    # --- EASY (Greedy) ---
    else:
        cur_c, cur_r = mx, my
        for _ in range(steps_to_take):
            if cur_c == tx and cur_r == ty: break
            
            cell = grid.matrix[cur_r][cur_c]
            moved = False
            
            # Ưu tiên đi Ngang
            if cur_c < tx and not cell.walls['right']: cur_c += 1; moved = True
            elif cur_c > tx and not cell.walls['left']: cur_c -= 1; moved = True
            
            if not moved:
                # Sau đó đi Dọc
                if cur_r < ty and not cell.walls['bottom']: cur_r += 1
                elif cur_r > ty and not cell.walls['top']: cur_r -= 1
            
            # Nếu có di chuyển thì thêm vào list
            if (cur_c, cur_r) != (mx, my):
                # Tránh trường hợp easy AI bị kẹt tại chỗ cũ mà vẫn add vào list
                if not path_steps or path_steps[-1] != (cur_c, cur_r):
                    path_steps.append((cur_c, cur_r))

    # Nếu không tìm được đường hoặc đã ở đích, trả về vị trí hiện tại để code không lỗi
    if not path_steps:
        return [(mx, my)]
        
    return path_steps

# ==========================================
# 3. SOLVER & MAP VALIDATOR (DÙNG ĐỆ QUY)
# ==========================================

def recursive_solve(grid, p_pos, m_pos, e_pos, difficulty, visited):
    """
    Hàm đệ quy tìm đường thắng.
    """
    px, py = p_pos
    mx, my = m_pos

    # 1. Base Case: Thắng
    if (px, py) == e_pos:
        return []

    # 2. Base Case: Thua (Bị bắt ngay tại chỗ)
    if (px, py) == (mx, my):
        return None

    # 3. Base Case: Trạng thái lặp
    state = (px, py, mx, my)
    if state in visited:
        return None
    visited.add(state)

    # 4. Thử đi 4 hướng (Heuristic: Ưu tiên hướng gần đích)
    moves = [('top',0,-1), ('bottom',0,1), ('left',-1,0), ('right',1,0)]
    moves.sort(key=lambda m: abs((px+m[1])-e_pos[0]) + abs((py+m[2])-e_pos[1]))

    for direction, dx, dy in moves:
        # Kiểm tra tường của Player
        if grid.matrix[py][px].walls[direction]:
            continue
        
        n_px, n_py = px + dx, py + dy
        
        # --- LOGIC MỚI: Xử lý Mummy đi từng bước ---
        mummy_steps = get_mummy_next_pos(mx, my, n_px, n_py, grid, difficulty)
        n_mx, n_my = mummy_steps[-1] # Vị trí cuối cùng của Mummy sau lượt đi
        
        # Kiểm tra va chạm trong quá trình di chuyển
        # Nếu Player đi vào ô Mummy đang đứng -> Chết
        if (n_px, n_py) == (mx, my): continue

        # Nếu Mummy đi qua ô Player đang đứng (hoặc trùng đích) -> Chết
        # Kiểm tra từng bước đi của Mummy
        caught = False
        for step in mummy_steps:
            if step == (n_px, n_py):
                caught = True
                break
        if caught: continue
        # -------------------------------------------

        # Đệ quy tiếp
        res = recursive_solve(grid, (n_px, n_py), (n_mx, n_my), e_pos, difficulty, visited)
        
        if res is not None:
            return [direction] + res

    return None

def find_solution_path(grid, p_pos, m_pos, e_pos, difficulty):
    """Wrapper gọi hàm đệ quy"""
    visited = set()
    return recursive_solve(grid, p_pos, m_pos, e_pos, difficulty, visited)


# ==========================================
# 4. MAP GENERATOR
# ==========================================

import heapq
import random
import sys
from collections import deque
from grid import Grid # Giả định bạn đã có file grid.py

# ... (Giữ nguyên các hàm a_star_search, dfs_search, get_mummy_next_pos, recursive_solve ở trên) ...

# ==========================================
# 4. MAP GENERATOR (ĐÃ CHỈNH SỬA)
# ==========================================

class MapGenerator:
    @staticmethod
    def generate_valid_level(rows, cols, cell_size, difficulty='HARD', wall_remove_ratio=0.25):
        attempts = 0
        
        # Định nghĩa khoảng cách tối thiểu (ví dụ: 1/3 tổng kích thước bản đồ)
        min_dist = (rows + cols) // 3 

        while True:
            attempts += 1
            grid = Grid(rows, cols, cell_size)
            
            # 1. Tạo mê cung (DFS Backtracker)
            MapGenerator.dfs_maze(grid, 0, 0)
            
            # 2. Phá tường để tạo đường vòng
            current_ratio = wall_remove_ratio
            if attempts > 200: current_ratio += 0.05
            if attempts > 400: current_ratio += 0.1
            
            MapGenerator.remove_random_walls(grid, current_ratio)
            
            # 3. SINH VỊ TRÍ NGẪU NHIÊN (LOGIC MỚI)
            # -----------------------------------------------------
            # Bước A: Random Player bất kỳ
            p_start = (random.randint(0, cols-1), random.randint(0, rows-1))
            
            # Bước B: Random Mummy (phải xa Player)
            while True:
                m_start = (random.randint(0, cols-1), random.randint(0, rows-1))
                dist_pm = abs(m_start[0] - p_start[0]) + abs(m_start[1] - p_start[1])
                # Mummy phải khác Player và khoảng cách đủ lớn
                if m_start != p_start and dist_pm >= min_dist:
                    break
            
            # Bước C: Random Exit (phải xa Player và không trùng Mummy)
            while True:
                exit_pos = (random.randint(0, cols-1), random.randint(0, rows-1))
                dist_pe = abs(exit_pos[0] - p_start[0]) + abs(exit_pos[1] - p_start[1])
                # Exit khác Player, khác Mummy, và xa Player
                if exit_pos != p_start and exit_pos != m_start and dist_pe >= min_dist:
                    break
            # -----------------------------------------------------

            # 4. Kiểm tra tính khả thi
            # Nếu vị trí random quá khó (không giải được), vòng lặp while lớn bên ngoài sẽ chạy lại
            solution = find_solution_path(grid, p_start, m_start, exit_pos, difficulty)
            
            if solution is not None:
                print(f"Map Valid ({difficulty}): {attempts} tries. Solvable in {len(solution)} steps.")
                print(f"Positions -> P:{p_start}, M:{m_start}, E:{exit_pos}")
                return grid, p_start, m_start, exit_pos
            
            if attempts % 100 == 0:
                print(f"Searching for map... ({attempts})")

    @staticmethod
    def dfs_maze(grid, c, r):
        # ... (Giữ nguyên code cũ) ...
        grid.matrix[r][c].visited = True
        dirs = [('top',0,-1), ('bottom',0,1), ('left',-1,0), ('right',1,0)]
        random.shuffle(dirs)
        for d, dx, dy in dirs:
            nx, ny = c+dx, r+dy
            if 0 <= nx < grid.cols and 0 <= ny < grid.rows:
                if not grid.matrix[ny][nx].visited:
                    grid.remove_wall(c, r, nx, ny)
                    MapGenerator.dfs_maze(grid, nx, ny)

    @staticmethod
    def remove_random_walls(grid, ratio):
        # ... (Giữ nguyên code cũ) ...
        for r in range(grid.rows):
            for c in range(grid.cols):
                if c < grid.cols-1 and grid.matrix[r][c].walls['right']:
                    if random.random() < ratio: grid.remove_wall(c, r, c+1, r)
                if r < grid.rows-1 and grid.matrix[r][c].walls['bottom']:
                    if random.random() < ratio: grid.remove_wall(c, r, c, r+1)