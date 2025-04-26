import pygame
import sys
import random
import math

# initialise pygame
pygame.init()

# setup display
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cell Simulation")

# clock for controlling fps
clock = pygame.time.Clock()

# cell properties
cell_radius = 10
cell_speed = 1
base_direction_change_interval = 60
direction_change_variance = 30
max_angle_change = math.pi / 4
points_to_replicate = 5
cell_lifetime = 10000  # 5 seconds in milliseconds
MAX_CELLS = 250

# triangle properties
triangle_size = 3
spawn_range = 100
min_spawn_time = 1000
max_spawn_time = 5000
MAX_NUTRIENTS = 1000

def create_cell(x=None, y=None):
    if x is None:
        x = random.randint(cell_radius, WIDTH - cell_radius)
    if y is None:
        y = random.randint(cell_radius, HEIGHT - cell_radius)
    
    angle = random.uniform(0, 2 * math.pi)
    return {
        'x': x,
        'y': y,
        'angle': angle,
        'dx': math.cos(angle) * cell_speed,
        'dy': math.sin(angle) * cell_speed,
        'timer': 0,
        'direction_change_interval': base_direction_change_interval + random.randint(-direction_change_variance, direction_change_variance),
        'points': 0,
        'birth_time': pygame.time.get_ticks()
    }

def create_triangle_vertices(x, y, size):
    angle = 0
    vertices = []
    for i in range(3):
        vx = x + size * math.cos(angle + (i * 2 * math.pi / 3))
        vy = y + size * math.sin(angle + (i * 2 * math.pi / 3))
        vertices.append((int(vx), int(vy)))
    return vertices

def create_triangle(x, y):
    return {
        'x': x,
        'y': y,
        'vertices': create_triangle_vertices(x, y, triangle_size),
        'spawn_timer': random.randint(min_spawn_time, max_spawn_time),
        'last_spawn_time': pygame.time.get_ticks()
    }

def spawn_nutrient_near(parent):
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, spawn_range)
    x = parent['x'] + math.cos(angle) * distance
    y = parent['y'] + math.sin(angle) * distance
    x = max(triangle_size, min(WIDTH - triangle_size, x))
    y = max(triangle_size, min(HEIGHT - triangle_size, y))
    return create_triangle(x, y)

def check_cell_collision(c1, c2):
    dx = c1['x'] - c2['x']
    dy = c1['y'] - c2['y']
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance < cell_radius * 2:
        overlap = (cell_radius * 2) - distance
        move_x = (overlap * dx) / distance
        move_y = (overlap * dy) / distance
        
        c1['x'] += move_x / 2
        c1['y'] += move_y / 2
        c2['x'] -= move_x / 2
        c2['y'] -= move_y / 2
        
        temp_dx, temp_dy = c1['dx'], c1['dy']
        c1['dx'], c1['dy'] = c2['dx'], c2['dy']
        c2['dx'], c2['dy'] = temp_dx, temp_dy

def check_cell_nutrient_collision(cell, nutrient):
    dx = cell['x'] - nutrient['x']
    dy = cell['y'] - nutrient['y']
    distance = math.sqrt(dx * dx + dy * dy)
    return distance < cell_radius + triangle_size

# Create initial cells and triangles
cells = [create_cell() for _ in range(50)]
triangles = [create_triangle(
    random.randint(triangle_size, WIDTH - triangle_size),
    random.randint(triangle_size, HEIGHT - triangle_size)
) for _ in range(100)]

# Font for displaying points
font = pygame.font.Font(None, 20)

running = True
while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Process nutrient spawning
    new_triangles = []
    if len(triangles) < MAX_NUTRIENTS:  # Only spawn if under limit
        for triangle in triangles:
            if current_time - triangle['last_spawn_time'] >= triangle['spawn_timer']:
                new_triangles.append(spawn_nutrient_near(triangle))
                triangle['spawn_timer'] = random.randint(min_spawn_time, max_spawn_time)
                triangle['last_spawn_time'] = current_time
                if len(triangles) + len(new_triangles) >= MAX_NUTRIENTS:
                    break
    triangles.extend(new_triangles)

    # Process cells
    cells_to_remove = []
    new_cells = []

    for i, cell in enumerate(cells):
        # Check cell death
        if current_time - cell['birth_time'] >= cell_lifetime and cell['points'] < points_to_replicate:
            cells_to_remove.append(cell)
            continue

        # Check replication
        if cell['points'] >= points_to_replicate and len(cells) + len(new_cells) < MAX_CELLS:
            new_cell = create_cell(
                x=cell['x'] + random.randint(-20, 20),
                y=cell['y'] + random.randint(-20, 20)
            )
            new_cells.append(new_cell)
            cell['points'] = 0
            cell['birth_time'] = current_time

        # Update direction
        cell['timer'] += 1
        if cell['timer'] >= cell['direction_change_interval']:
            current_angle = math.atan2(cell['dy'], cell['dx'])
            angle_change = random.uniform(-max_angle_change, max_angle_change)
            new_angle = current_angle + angle_change
            cell['dx'] = math.cos(new_angle) * cell_speed
            cell['dy'] = math.sin(new_angle) * cell_speed
            cell['timer'] = 0
            cell['direction_change_interval'] = base_direction_change_interval + random.randint(-direction_change_variance, direction_change_variance)

        # Update position
        cell['x'] += cell['dx']
        cell['y'] += cell['dy']

        # Handle wall collisions
        if cell['x'] - cell_radius <= 0 or cell['x'] + cell_radius >= WIDTH:
            cell['dx'] *= -1
        if cell['y'] - cell_radius <= 0 or cell['y'] + cell_radius >= HEIGHT:
            cell['dy'] *= -1

        # Check cell-cell collisions
        for j in range(i + 1, len(cells)):
            check_cell_collision(cell, cells[j])

        # Check nutrient collisions
        triangles_to_remove = [t for t in triangles if check_cell_nutrient_collision(cell, t)]
        if triangles_to_remove:
            cell['points'] += len(triangles_to_remove)
            for triangle in triangles_to_remove:
                triangles.remove(triangle)

    # Update cell list
    for cell in cells_to_remove:
        cells.remove(cell)
    cells.extend(new_cells)

    # Draw everything
    screen.fill((0, 0, 0))

    # Draw entity counts
    counts_text = f"Cells: {len(cells)}/{MAX_CELLS} Nutrients: {len(triangles)}/{MAX_NUTRIENTS}"
    counts_surface = font.render(counts_text, True, (255, 255, 255))
    screen.blit(counts_surface, (10, 10))
    
    # Draw triangles
    for triangle in triangles:
        pygame.draw.polygon(screen, (255, 255, 0), triangle['vertices'])
    
    # Draw cells and their points
    for cell in cells:
        pygame.draw.circle(screen, (255, 0, 0), (int(cell['x']), int(cell['y'])), cell_radius)
        points_text = str(cell['points'])
        text_surface = font.render(points_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(int(cell['x']), int(cell['y'])))
        screen.blit(text_surface, text_rect)
    
    pygame.display.flip()

pygame.quit()
sys.exit()