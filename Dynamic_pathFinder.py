import pygame
import sys
import random #for random grid

pygame.init()

# Window settings
WIDTH = 600
HEIGHT = 600

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dynamic Pathfinding Agent")

# Grid settings
ROWS = 20
COLS = 20
CELL_SIZE = WIDTH // COLS

grid = []
for row in range(ROWS):
    grid.append([])
    for col in range(COLS):
        grid[row].append(0)
#Goal and start pos
start_pos = (0, 0)
goal_pos = (ROWS - 1, COLS - 1)

grid[start_pos[0]][start_pos[1]] = 2
grid[goal_pos[0]][goal_pos[1]] = 3

# Draw grid function
def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            if grid[row][col] == 0:
                color = (255, 255, 255)
            elif grid[row][col] == 1:
                color = (0, 0, 0)
            elif grid[row][col] == 2:
                color = (0, 0, 255)  # Start (Blue)
            elif grid[row][col] == 3:
                color = (255, 0, 0)  # Goal (Red)

            pygame.draw.rect(window, color, rect)
            pygame.draw.rect(window, (200, 200, 200), rect, 1)
#Draw random grid
def generate_random_grid(density):
    for row in range(ROWS):
        for col in range(COLS):
            if (row, col) == start_pos or (row, col) == goal_pos:
                continue

            if random.random() < density:
                grid[row][col] = 1
            else:
                grid[row][col] = 0
# Main loop
running = True
clock = pygame.time.Clock()

while running:
    window.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if pygame.mouse.get_pressed()[0]:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            col = mouse_pos[0] // CELL_SIZE
            row = mouse_pos[1] // CELL_SIZE

            if 0 <= row < ROWS and 0 <= col < COLS:
                 if grid[row][col] not in (2, 3):
                        grid[row][col] = 1

        if pygame.mouse.get_pressed()[2]:  # Right click
            mouse_pos = pygame.mouse.get_pos()
            col = mouse_pos[0] // CELL_SIZE
            row = mouse_pos[1] // CELL_SIZE

            if 0 <= row < ROWS and 0 <= col < COLS:
                if grid[row][col] not in (2, 3):
                    grid[row][col] = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                generate_random_grid(0.3)  # 30% walls

            if event.key == pygame.K_c:
                for row in range(ROWS):
                    for col in range(COLS):
                        if grid[row][col] not in (2, 3):
                            grid[row][col] = 0

    draw_grid()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()

