from enum import Enum
import math
import pygame
from typing import List, Tuple, Dict, Set, TypedDict
from sim_data import batsman, Batsman, ShotData, ShotName, shots

RgbColor = Tuple[int, int, int]
Point = Tuple[float, float]

class Segment(TypedDict):
    id: str
    poly: List[Point]
    coverage: int

class Aggression(Enum):
    VERY_DEFENSIVE = 1
    DEFENSIVE = 2
    NEUTRAL = 3
    ATTACKING = 4
    VERY_ATTACKING = 5

def circle_intersects_polygon(circle_center: Point, radius: float, polygon: List[Point]) -> bool:
    # Check if circle center is inside the polygon
    if point_inside_polygon(circle_center, polygon):
        return True
    
    # Check if circle intersects any edge of the polygon
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        if line_intersects_circle(p1, p2, circle_center, radius):
            return True
    
    # Check if any polygon vertex is inside the circle
    for point in polygon:
        dx = point[0] - circle_center[0]
        dy = point[1] - circle_center[1]
        if dx * dx + dy * dy <= radius * radius:
            return True

    return False

def point_inside_polygon(point: Point, polygon: List[Point]) -> bool:
    x, y = point
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    xinters = p1x
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y + 1e-10) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def line_intersects_circle(p1: Point, p2: Point, center: Point, radius: float) -> bool:
    # Vector math: check if circle intersects the line segment
    (x1, y1), (x2, y2) = p1, p2
    (cx, cy) = center
    dx = x2 - x1
    dy = y2 - y1
    fx = x1 - cx
    fy = y1 - cy

    a = dx*dx + dy*dy
    b = 2 * (fx*dx + fy*dy)
    c = fx*fx + fy*fy - radius*radius

    if a == 0:
        # Check if the single point is within the circle
        dist_sq = fx*fx + fy*fy
        return dist_sq <= radius * radius
    
    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return False  # No intersection
    discriminant = math.sqrt(discriminant)

    t1 = (-b - discriminant) / (2*a)
    t2 = (-b + discriminant) / (2*a)

    if (0 <= t1 <= 1) or (0 <= t2 <= 1):
        return True
    return False

def find_weak_areas(segments: List[Segment], threshold: int = 0) -> Set[str]:
    weak_areas: Set[str] = set()
    for segment in segments:
        if segment['coverage'] <= threshold:
            weak_areas.add(segment['id'])
    return weak_areas

def segments_to_areas(segments: List[Segment]) -> Set[str]:
    areas: Set[str] = set()
    for segment in segments:
        areas.add(segment['id'])
    return areas

def get_potential_shots(shots: Dict[ShotName, ShotData], current_line: int, current_length: int) -> Dict[ShotName, ShotData]:
    filtered_shots: Dict[ShotName, ShotData] = {}
    
    for shot, data in shots.items():
        line_min, line_max = data['line']
        length_min, length_max = data['length']

        if not (line_min <= current_line <= line_max):
            continue
        if not (length_min <= current_length <= length_max):
            continue
        
        filtered_shots[shot] = data

    return filtered_shots

def find_potential_shots(segments: List[Segment], current_delivery_line: int, current_delivery_length: int, batsman: Batsman) -> Dict[str, Tuple[float, ShotName]]:
    filtered_shots: Dict[ShotName, ShotData] = get_potential_shots(shots, current_delivery_line, current_delivery_length)

    segment_shot_values: Dict[str, Tuple[float, ShotName]] = {}
    for shot_name, data in filtered_shots.items():
        wedges: List[int] = data['wedges']
        power: Tuple[int, int] = data['power']

        for wedge_val in wedges:
            for power_val in power:
                segment_id: str = f"W{wedge_val}Z{power_val}"
                segment_shot_initial_value: float = batsman['shots'].get(shot_name, 0)
                segment_shot_values[segment_id] = (segment_shot_initial_value, shot_name)
    
    weak_areas: Set[str] = find_weak_areas(segments, threshold=0)
    batsman_judgement_multiplier: float = 1 + (batsman['base_traits']['judgement'] / 100.0)
    for seg_id, seg_shot_val in segment_shot_values.items():
        if seg_id in weak_areas:
            seg_shot_val = (seg_shot_val[0] * batsman_judgement_multiplier, seg_shot_val[1])
            segment_shot_values[seg_id] = seg_shot_val
    
    return segment_shot_values

def adjust_potential_shots(segment_shot_values: Dict[str, Tuple[float, ShotName]], aggression: Aggression) -> Dict[str, Tuple[float, ShotName]]:
    if aggression == Aggression.VERY_DEFENSIVE:
        for seg_id, (shot_value, shot_name) in segment_shot_values.items():
            if shot_name in [ShotName.BLOCK, ShotName.TAP] or seg_id.endswith(("Z1", "Z2", "Z3")):
                segment_shot_values[seg_id] = (shot_value * 3, shot_name)
            elif seg_id.endswith(("Z4", "Z5", "Z6", "Z7")):
                segment_shot_values[seg_id] = (shot_value * 0.5, shot_name)
    elif aggression == Aggression.DEFENSIVE:
        for seg_id, (shot_value, shot_name) in segment_shot_values.items():
            if shot_name in [ShotName.BLOCK, ShotName.TAP] or seg_id.endswith(("Z1", "Z2", "Z3")):
                segment_shot_values[seg_id] = (shot_value * 1.5, shot_name)
            elif seg_id.endswith(("Z4", "Z5", "Z6", "Z7")):
                segment_shot_values[seg_id] = (shot_value * 0.75, shot_name)
    elif aggression == Aggression.ATTACKING:
        for seg_id, (shot_value, shot_name) in segment_shot_values.items():
            if seg_id.endswith(("Z5", "Z6", "Z7")):
                segment_shot_values[seg_id] = (shot_value * 1.5, shot_name)
            elif seg_id.endswith(("Z1", "Z2")):
                segment_shot_values[seg_id] = (shot_value * 0.75, shot_name)
    elif aggression == Aggression.VERY_ATTACKING:
        for seg_id, (shot_value, shot_name) in segment_shot_values.items():
            if seg_id.endswith(("Z5", "Z6", "Z7")):
                segment_shot_values[seg_id] = (shot_value * 3, shot_name)
            elif seg_id.endswith(("Z1", "Z2", "Z3")):
                segment_shot_values[seg_id] = (shot_value * 0.5, shot_name)

    segment_shot_values['OUT'] = (0, ShotName.OUT)
    segment_shot_values['LEAVE'] = (0, ShotName.LEAVE)
    segment_shot_values['MISS'] = (0, ShotName.MISS)
    segment_shot_values['LEG_BYES'] = (0, ShotName.LEG_BYES)
    
    return segment_shot_values

def calculate_potential_shot_probabilities(segment_shot_values: Dict[str, Tuple[float, ShotName]]) -> Dict[str, float]:
    total_value: float = sum(value[0] for value in segment_shot_values.values())
    probabilities: Dict[str, float] = {}
    
    for seg_id, (shot_value, _) in segment_shot_values.items():
        probabilities[seg_id] = shot_value / total_value
    
    return probabilities

def lerp(p: Point, q: Point, t: float) -> Point:
    return (p[0] + (q[0]-p[0])*t,
            p[1] + (q[1]-p[1])*t)

def draw_cricket_field() -> None:
    pygame.init()
    
    WIDTH: float = 800
    HEIGHT: float = 600
    screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cricket Field")
    
    DARK_BG: RgbColor = (18, 18, 18)
    DARK_GREEN: RgbColor = (34, 87, 45)
    PITCH_COLOUR: RgbColor = (176, 163, 127)
    LIGHT_GRAY: RgbColor = (150, 150, 150)
    
    WHITE: RgbColor = (255, 255, 255)
    RED: RgbColor = (255, 0, 0)
    GRID_COLOR: RgbColor = (50, 50, 50)
    ZONE_COLOR: RgbColor = (100, 100, 100)
    COVERAGE_COLOR: Tuple[int, int, int, int] = (255, 255, 255, 32)
    grid_enabled: bool = False
    zones_enabled: bool = True
    inner_circle_enabled: bool = True
    fielder_coverage_enabed: bool = False

    current_delivery_line = 4
    current_delivery_length = 4
    
    selected_wedge: int = 0
    selected_fielder: int | None = None
    offset_x: float = 0
    offset_y: float = 0

    # Create surfaces for the highlight and coverage
    highlight_surface: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    coverage_surface: pygame.Surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Field dimensions and center for the oval ground
    FIELD_X: float = 150
    FIELD_WIDTH: float = 500
    FIELD_Y: float = 50
    FIELD_HEIGHT: float = 500
    batsman_pos: Point = (400, 260)

    ellipse_cx: float = 400
    ellipse_cy: float = 300
    ellipse_rx: float = 240
    ellipse_ry: float = 240
    NUM_WEDGES: int = 18  # 20° wedges

    # 1a) compute the wedge angles
    wedge_angles: List[float] = [i * 360/NUM_WEDGES for i in range(NUM_WEDGES)]

    # 1b) for each angle, find the exact intersection with the ellipse
    radial_lines: List[Tuple[Point, Point]] = []  # will hold ((bx,by),(ex,ey)) for each wedge
    for angle in wedge_angles:
        rad: float = math.radians(angle)
        dx, dy = math.cos(rad), math.sin(rad)

        # Solve for t so that (cx + dx*t, cy + dy*t) lies on the ellipse:
        #   ((X−cx)/rx)^2 + ((Y−cy)/ry)^2 = 1
        # => (dx^2/rx^2 + dy^2/ry^2) * t^2 = 1
        denom: float = math.sqrt((dx*dx)/(ellipse_rx*ellipse_rx) +
                        (dy*dy)/(ellipse_ry*ellipse_ry))
        t = 1.0 / denom

        end_x: float = ellipse_cx + dx * t
        end_y: float = ellipse_cy + dy * t

        radial_lines.append((batsman_pos, (end_x, end_y)))

    FIELDER_RANGE: float = 10

    NUM_ZONES: int = 7
    segments: List[Segment] = []

    for i in range(NUM_WEDGES):
        start_ray: Tuple[Point, Point] = radial_lines[i]
        end_ray: Tuple[Point, Point]   = radial_lines[(i + 1) % NUM_WEDGES]

        for z in range(NUM_ZONES):
            t0: float = z   / NUM_ZONES
            t1: float = (z+1)/ NUM_ZONES

            # four corners of that wedge-zone
            p1_inner: Point = lerp(*start_ray, t0)
            p1_outer: Point = lerp(*start_ray, t1)
            p2_outer: Point = lerp(*end_ray,   t1)
            p2_inner: Point = lerp(*end_ray,   t0)

            poly: List[Point] = [p1_inner, p1_outer, p2_outer, p2_inner]
            segments.append({
                'id':   f"W{i}Z{z}",
                'poly': poly,
                'coverage': 0
            })

    # Fielder positions (x, y coordinates)
    fielders: List[Point] = [
        (400, 200),  # Wicket-keeper
        (330, 400),  # Mid-off
        (350, 310),  # Short cover
        (200, 200),  # Deep point
        (385, 190),  # 1st slip
        (370, 192),  # 2nd slip
        (355, 198),  # 3rd slip
        (490, 325),  # Midwicket
        (550, 125),  # Fine leg
        (450, 525),  # Long on
    ]

    for segment in segments:
        segment['coverage'] = 0

    # Update segment coverage based on fielders
    for fielder in fielders:
        # Calculate distance from the batsman
        distance_to_batsman: float = math.sqrt((fielder[0] - batsman_pos[0])**2 + (fielder[1] - batsman_pos[1])**2)
        
        # Adjust coverage radius based on distance to batsman
        adjusted_range: float = max(10, FIELDER_RANGE + int(distance_to_batsman * 0.25))

        for segment in segments:
            if segment['id'] in ['W4Z0', 'W4Z1', 'W4Z2']:
                segment['coverage'] = 1
            if circle_intersects_polygon(fielder, adjusted_range, segment['poly']):
                segment['coverage'] += 1

    pygame.font.init()
    font = pygame.font.SysFont('Arial', 10)

    input_active: Dict[str, bool] = {"line": False, "length": False}
    input_text: Dict[str, str] = {"line": "", "length": ""}
    input_boxes: Dict[str, pygame.Rect] = {
        "line": pygame.Rect(600, 20, 60, 24),
        "length": pygame.Rect(600, 60, 60, 24)
    }
    input_colors: Dict[str, pygame.Color] = {
        "line": pygame.Color('lightskyblue3'),
        "length": pygame.Color('lightskyblue3')
    }

    # TODO tidy up this entire code so that simulation refinements can be made more easily
    potential_shots = find_potential_shots(segments, current_delivery_line, current_delivery_length, batsman)
    adjusted_potential_shots = adjust_potential_shots(potential_shots, Aggression.VERY_ATTACKING)
    shot_probabilities = calculate_potential_shot_probabilities(adjusted_potential_shots)
    # Sort the shot probabilities in descending order
    shot_probabilities = dict(sorted(shot_probabilities.items(), key=lambda item: item[1], reverse=True))

    zones_probabilities: Dict[str, float] = {}
    for segment_id, probability in shot_probabilities.items():
        if segment_id.startswith('W'):
            zone = segment_id.split('Z')[1]
            if zone not in zones_probabilities:
                zones_probabilities[zone] = 0
            zones_probabilities[zone] += probability

    print("Probabilities based on zones:")
    for zone_id, probability in zones_probabilities.items():
        print(f"Zone: {zone_id}, Probability: {probability:.5f}")

    print("Potential shots based on current delivery line and length:")
    for segment_id, (shot_value, shot_name) in adjusted_potential_shots.items():
        print(f"Segment: {segment_id}, Shot Value: {shot_value}, Shot Name: {shot_name}")
    print("Shot probabilities:")
    for segment_id, probability in shot_probabilities.items():
        print(f"Segment: {segment_id}, Probability: {probability:.5f}")
    
    # Game loop
    running: bool = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos: Point = pygame.mouse.get_pos()
                for i, fielder in enumerate(fielders):
                    fx, fy = fielder
                    if math.hypot(mouse_pos[0] - fx, mouse_pos[1] - fy) < 10:
                        selected_fielder = i
                        offset_x = fx - mouse_pos[0]
                        offset_y = fy - mouse_pos[1]
                        break
                for key in input_boxes:
                    if input_boxes[key].collidepoint(event.pos):
                        input_active[key] = True
                    else:
                        input_active[key] = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_fielder is not None:
                    selected_fielder = None

                    # recalculate segment coverage here
                    for segment in segments:
                        segment['coverage'] = 0
                    for fielder in fielders:
                        distance_to_batsman = math.sqrt((fielder[0] - batsman_pos[0])**2 + (fielder[1] - batsman_pos[1])**2)
                        adjusted_range = max(10, FIELDER_RANGE + int(distance_to_batsman * 0.25))
                        for segment in segments:
                            if segment['id'] in ['W4Z0', 'W4Z1', 'W4Z2']:
                                segment['coverage'] = 1
                            if circle_intersects_polygon(fielder, adjusted_range, segment['poly']):
                                segment['coverage'] += 1
                    
                    potential_shots = find_potential_shots(segments, current_delivery_line, current_delivery_length, batsman)
                    print("Potential shots based on current delivery line and length:")
                    for segment_id, (shot_value, shot_name) in potential_shots.items():
                        print(f"Segment: {segment_id}, Shot Value: {shot_value}, Shot Name: {shot_name}")

            elif event.type == pygame.MOUSEMOTION:
                if selected_fielder is not None:
                    mouse_x, mouse_y = event.pos
                    fielders[selected_fielder] = (mouse_x + offset_x, mouse_y + offset_y)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    selected_wedge = (selected_wedge + 1) % NUM_WEDGES
                elif event.key == pygame.K_LEFT:
                    selected_wedge = (selected_wedge - 1) % NUM_WEDGES
                
                for key in input_active:
                    if input_active[key]:
                        if event.key == pygame.K_RETURN:
                            print(f"{key.title()} entered: {input_text[key]}")
                            input_active[key] = False
                            potential_shots = find_potential_shots(segments, current_delivery_line, current_delivery_length, batsman)
                            print("Potential shots based on current delivery line and length:")
                            for segment_id, (shot_value, shot_name) in potential_shots.items():
                                print(f"Segment: {segment_id}, Shot Value: {shot_value}, Shot Name: {shot_name}")
                        elif event.key == pygame.K_BACKSPACE:
                            input_text[key] = input_text[key][:-1]
                        elif event.unicode.isdigit():
                            input_text[key] += event.unicode

        if input_text["line"] and input_text["length"]:
            current_delivery_line = int(input_text["line"])
            current_delivery_length = int(input_text["length"])

        coverage_surface.fill((0, 0, 0, 0))
        highlight_surface.fill((0, 0, 0, 0))

        screen.fill(DARK_BG)
        
        # Draw oval ground
        pygame.draw.ellipse(screen, DARK_GREEN, (FIELD_X, FIELD_Y, FIELD_WIDTH, FIELD_HEIGHT))
        
        # Draw boundary line
        pygame.draw.ellipse(screen, LIGHT_GRAY, (160, 60, 480, 480), 2)

        # Draw inner circle
        if inner_circle_enabled:
            pygame.draw.circle(screen, LIGHT_GRAY, (400, 300), 130, 2)
        
        # Draw crease lines
        pygame.draw.line(screen, LIGHT_GRAY, (390, 250), (410, 250), 1)
        pygame.draw.line(screen, LIGHT_GRAY, (390, 350), (410, 350), 1)

        if grid_enabled:
            # Draw grid lines and numbers
            for x in range(0, WIDTH, 25):
                pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
                text = font.render(str(x), True, LIGHT_GRAY)
                screen.blit(text, (x, 5))
                
            for y in range(0, HEIGHT, 25):
                pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))
                text = font.render(str(y), True, LIGHT_GRAY)
                screen.blit(text, (5, y))
        
        if zones_enabled:
            ellipse_cx = 400
            ellipse_cy = 300
            ellipse_rx = 240
            ellipse_ry = 240

            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                dx = math.cos(rad)
                dy = math.sin(rad)

                # Use ellipse parametric boundary formula
                denom = math.sqrt((dx**2 / ellipse_rx**2) + (dy**2 / ellipse_ry**2))
                t = 1 / denom

                end_x = ellipse_cx + dx * t
                end_y = ellipse_cy + dy * t

                pygame.draw.line(screen, ZONE_COLOR, batsman_pos, (end_x, end_y), 1)

            # Draw zones by connecting pairs of wedge lines
            for i in range(len(radial_lines)):
                start_ray = radial_lines[i]
                next_ray  = radial_lines[(i+1)%len(radial_lines)]
                for z in range(NUM_ZONES):
                    t0 = z   / NUM_ZONES
                    t1 = (z+1)/ NUM_ZONES

                    # lerp from batsman_pos → boundary_point
                    p1_i = lerp(start_ray[0], start_ray[1], t0)
                    p1_o = lerp(start_ray[0], start_ray[1], t1)
                    p2_o = lerp(next_ray [0], next_ray [1], t1)
                    p2_i = lerp(next_ray [0], next_ray [1], t0)

                    pygame.draw.polygon(
                        screen, ZONE_COLOR,
                        [p1_i, p1_o, p2_o, p2_i], 1
                    )

        if fielder_coverage_enabed:
            for pos in fielders:
                distance_to_batsman = math.sqrt((pos[0] - batsman_pos[0])**2 + (pos[1] - batsman_pos[1])**2)
                
                # Adjust coverage radius based on distance to batsman
                adjusted_range = max(10, FIELDER_RANGE + int(distance_to_batsman * 0.25))
                
                pygame.draw.circle(coverage_surface, COVERAGE_COLOR, pos, adjusted_range)
        
        # Draw highlight areas
        for seg in segments:
            if seg['coverage'] > 0:
                alpha = int(255 * (seg['coverage']/len(fielders)))
                color = (255,255,0, alpha)
                pygame.draw.polygon(highlight_surface, color, seg['poly'])

        # Draw fielders
        for pos in fielders:
            pygame.draw.circle(screen, WHITE, pos, 4)
        
        # Draw pitch
        pygame.draw.rect(screen, PITCH_COLOUR, (393, 250, 15, 100))

        # Highlight the selected wedge (all 7 zones in that wedge)
        for segment in segments:
            if segment['id'].startswith(f"W{selected_wedge}Z"):
                pygame.draw.polygon(screen, (0, 200, 255), segment['poly'], 2)  # cyan outline

        # Draw batsman
        pygame.draw.circle(screen, RED, batsman_pos, 4)

        # Draw bowler
        pygame.draw.circle(screen, WHITE, (395, 425), 4)

        # Draw ball
        ball_pos = (400, 275)
        pygame.draw.circle(screen, WHITE, ball_pos, 2)

        # Display current wedge index
        wedge_text = font.render(f"Wedge: W{selected_wedge}", True, (255, 255, 255))
        screen.blit(wedge_text, (20, 20))  # Top-left corner

        for key in input_boxes:
            pygame.draw.rect(screen, input_colors[key], input_boxes[key], 2)
            txt_surface = font.render(input_text[key], True, (255, 255, 255))
            screen.blit(txt_surface, (input_boxes[key].x + 5, input_boxes[key].y + 5))

        # Add labels for input boxes
        line_label = font.render("Line:", True, (255, 255, 255))
        screen.blit(line_label, (560, 24))
        length_label = font.render("Length:", True, (255, 255, 255))
        screen.blit(length_label, (550, 64))

        screen.blit(coverage_surface, (0, 0))
        screen.blit(highlight_surface, (0, 0))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    draw_cricket_field()