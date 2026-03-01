import pygame
import sys
import random
import heapq
import time

pygame.init()

# -------------------- Node Class --------------------
class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.g = float('inf')  # Cost from start (A*)
        self.h = 0             # Heuristic cost
        self.f = float('inf')  # Total cost
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f  # required for heapq

# -------------------- Heuristic --------------------
def manhattan(node, goal):
    return abs(node.row - goal[0]) + abs(node.col - goal[1])

# -------------------- Window & Grid --------------------
WIDTH, HEIGHT = 600, 640  # extra 40px for metrics
ROWS, COLS = 20, 20
CELL_SIZE = WIDTH // COLS

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dynamic Pathfinding Agent")

grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

start_pos = (0, 0)
goal_pos = (ROWS-1, COLS-1)
grid[start_pos[0]][start_pos[1]] = 2
grid[goal_pos[0]][goal_pos[1]] = 3

# -------------------- Metrics --------------------
def draw_metrics(path_length=0, nodes_visited=0, exec_time=0):
    font = pygame.font.SysFont(None, 24)
    pygame.draw.rect(window, (220,220,220), (0,0,WIDTH,40))
    texts = [
        f"Path Length: {path_length}",
        f"Nodes Visited: {nodes_visited}",
        f"Execution Time: {exec_time:.2f} ms"
    ]
    for i, text in enumerate(texts):
        img = font.render(text, True, (0,0,0))
        window.blit(img, (10 + i*200, 10))

# -------------------- Grid Drawing --------------------
def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE + 40
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            color = (255,255,255)
            if grid[row][col] == 1:
                color = (0,0,0)
            elif grid[row][col] == 2:
                color = (0,0,255)
            elif grid[row][col] == 3:
                color = (255,0,0)
            pygame.draw.rect(window, color, rect)
            pygame.draw.rect(window, (200,200,200), rect, 1)

# -------------------- Random Grid --------------------
def generate_random_grid(density=0.3):
    for r in range(ROWS):
        for c in range(COLS):
            if (r,c) not in (start_pos, goal_pos):
                grid[r][c] = 1 if random.random() < density else 0

# -------------------- Pathfinding Helpers --------------------
def get_neighbors(node, nodes):
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    neighbors = []
    for dr, dc in directions:
        r, c = node.row + dr, node.col + dc
        if 0 <= r < ROWS and 0 <= c < COLS:
            if grid[r][c] != 1:
                neighbors.append(nodes[r][c])
    return neighbors

def reconstruct_path(end_node):
    path = []
    current = end_node
    while current:
        path.append((current.row, current.col))
        current = current.parent
    path.reverse()
    return path

def draw_search(open_set, visited_set, path=[], nodes_visited=0, exec_time=0):
    window.fill((255,255,255))
    draw_metrics(len(path), nodes_visited, exec_time)

    for row in range(ROWS):
        for col in range(COLS):
            x, y = col*CELL_SIZE, row*CELL_SIZE + 40
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            color = (255,255,255)
            if (row,col) in visited_set:
                color = (255,200,200)
            elif any(node.row==row and node.col==col for _,node in open_set):
                color = (255,255,0)
            elif (row,col) in path:
                color = (0,255,0)
            elif grid[row][col]==1:
                color = (0,0,0)
            elif grid[row][col]==2:
                color = (0,0,255)
            elif grid[row][col]==3:
                color = (255,0,0)
            pygame.draw.rect(window,color,rect)
            pygame.draw.rect(window,(200,200,200),rect,1)

    pygame.display.update()
    pygame.time.delay(20)

# -------------------- GBFS --------------------
def gbfs(start_pos, goal_pos):
    nodes = [[Node(r,c) for c in range(COLS)] for r in range(ROWS)]
    start, goal = nodes[start_pos[0]][start_pos[1]], nodes[goal_pos[0]][goal_pos[1]]
    open_set = [(0,start)]
    visited_set = set()
    nodes_visited = 0

    while open_set:
        _, current = heapq.heappop(open_set)
        nodes_visited +=1
        if (current.row, current.col) == goal_pos:
            return reconstruct_path(current), nodes_visited
        visited_set.add((current.row,current.col))
        for neighbor in get_neighbors(current,nodes):
            if (neighbor.row, neighbor.col) in visited_set:
                continue
            neighbor.h = manhattan(neighbor, goal_pos)
            neighbor.parent = current
            heapq.heappush(open_set,(neighbor.h,neighbor))
        draw_search(open_set, visited_set)
    return None, nodes_visited

# -------------------- A* --------------------
def astar(start_pos, goal_pos):
    nodes = [[Node(r,c) for c in range(COLS)] for r in range(ROWS)]
    start, goal = nodes[start_pos[0]][start_pos[1]], nodes[goal_pos[0]][goal_pos[1]]
    start.g = 0
    start.h = manhattan(start,goal_pos)
    start.f = start.g + start.h

    open_set = [(start.f, start)]
    visited_set = set()
    nodes_visited = 0

    while open_set:
        _, current = heapq.heappop(open_set)
        nodes_visited +=1
        if (current.row, current.col) == goal_pos:
            return reconstruct_path(current), nodes_visited
        visited_set.add((current.row,current.col))
        for neighbor in get_neighbors(current,nodes):
            tentative_g = current.g +1
            if tentative_g < neighbor.g:
                neighbor.g = tentative_g
                neighbor.h = manhattan(neighbor,goal_pos)
                neighbor.f = neighbor.g + neighbor.h
                neighbor.parent = current
                if (neighbor.row,neighbor.col) not in visited_set:
                    heapq.heappush(open_set,(neighbor.f,neighbor))
        draw_search(open_set, visited_set)
    return None, nodes_visited

# -------------------- Dynamic Obstacles --------------------
DYNAMIC_PROB = 0.01
dynamic_mode = False
current_path = []
current_algorithm = None

#  track nodes_visited and exec_time separately so the main loop can display them
last_nodes_visited = 0
last_exec_time = 0.0

def spawn_dynamic_obstacles():
    global current_path
    for r in range(ROWS):
        for c in range(COLS):
            if (r,c) in (start_pos,goal_pos):
                continue
            if grid[r][c]==0 and random.random()<DYNAMIC_PROB:
                grid[r][c]=1
                if (r,c) in current_path:
                    replan_path()

def replan_path():
    global current_path
    if current_algorithm=='GBFS':
        path,_ = gbfs(start_pos, goal_pos)
    elif current_algorithm=='A*':
        path,_ = astar(start_pos, goal_pos)
    else:
        return
    if path:
        current_path = path

# -------------------- Main Loop --------------------
running = True
clock = pygame.time.Clock()

while running:
    if dynamic_mode and current_path:
        spawn_dynamic_obstacles()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if pygame.mouse.get_pressed()[0]:
            x,y = pygame.mouse.get_pos()
            col,row = x//CELL_SIZE, (y-40)//CELL_SIZE
            if 0<=row<ROWS and 0<=col<COLS and grid[row][col] not in (2,3):
                grid[row][col]=1
        if pygame.mouse.get_pressed()[2]:
            x,y = pygame.mouse.get_pos()
            col,row = x//CELL_SIZE, (y-40)//CELL_SIZE
            if 0<=row<ROWS and 0<=col<COLS and grid[row][col] not in (2,3):
                grid[row][col]=0
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_r:
                generate_random_grid(0.3)
            if event.key==pygame.K_c:
                for r in range(ROWS):
                    for c in range(COLS):
                        if grid[r][c] not in (2,3):
                            grid[r][c]=0
                # reset metrics when grid is cleared
                current_path = []
                last_nodes_visited = 0
                last_exec_time = 0.0
            if event.key==pygame.K_d:
                dynamic_mode = not dynamic_mode
            if event.key==pygame.K_g:
                current_algorithm='GBFS'
                start_time=time.time()
                path,visited=gbfs(start_pos, goal_pos)
                end_time=time.time()
                
                last_nodes_visited = visited
                last_exec_time = (end_time - start_time) * 1000
                if path:
                    current_path=path
                    draw_search([],set(),current_path,visited,last_exec_time)
            if event.key==pygame.K_a:
                current_algorithm='A*'
                start_time=time.time()
                path,visited=astar(start_pos, goal_pos)
                end_time=time.time()
                last_nodes_visited = visited
                last_exec_time = (end_time - start_time) * 1000
                if path:
                    current_path=path
                    draw_search([],set(),current_path,visited,last_exec_time)

    draw_grid()
    draw_metrics(len(current_path), last_nodes_visited, last_exec_time)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()