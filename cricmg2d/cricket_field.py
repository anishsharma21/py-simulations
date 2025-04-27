import sys
import math
import pygame
from typing import List, Tuple, Dict
from watchdog_config import watch_for_changes, restart_program
from game_config import GameConfig
from geometry import GeometryUtils
from shot_analyzer import ShotAnalyzer
from testing_data import batsman
from _types import Aggression, Point, RgbColor, RgbaColor, Segment

class CricketField:
    """Main class for cricket field simulation"""
    
    def __init__(self, config: GameConfig = GameConfig()):
        # Store configuration
        self.config = config
        
        # Colors
        self.colors: Dict[str, RgbColor | RgbaColor] = {
            'DARK_BG': (18, 18, 18),
            'DARK_GREEN': (34, 87, 45),
            'PITCH_COLOUR': (176, 163, 127),
            'LIGHT_GRAY': (150, 150, 150),
            'WHITE': (255, 255, 255),
            'RED': (255, 0, 0),
            'GRID_COLOR': (50, 50, 50),
            'ZONE_COLOR': (100, 100, 100),
            'COVERAGE_COLOR': (255, 255, 255, 32)
        }
        
        # Display settings
        self.grid_enabled = False
        self.zones_enabled = True
        self.inner_circle_enabled = True
        self.fielder_coverage_enabled = False

        # Watchdog settings
        self.observer, self.event_handler = watch_for_changes()
     
        # Game state
        self.current_delivery_line = 4
        self.current_delivery_length = 5
        self.aggression_level = Aggression.NEUTRAL
        self.selected_wedge = 0
        self.selected_fielder = None
        self.offset_x = 0
        self.offset_y = 0
        self.running = True
        
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption("Cricket Field")
        self.font = pygame.font.SysFont('Arial', 10)
        
        # Create surfaces
        self.highlight_surface = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        self.coverage_surface = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        
        # Field elements
        self.batsman_pos = (700, 360)
        self.ellipse_cx = 700
        self.ellipse_cy = 400
        self.ellipse_rx = 240
        self.ellipse_ry = 240
        
        # Input handling
        self.input_active = {"line": False, "length": False}
        self.input_text = {"line": str(self.current_delivery_line), "length": str(self.current_delivery_length)}
        self.input_boxes = {
            "line": pygame.Rect(600, 20, 60, 24),
            "length": pygame.Rect(600, 60, 60, 24)
        }
        self.input_colors = {
            "line": pygame.Color('lightskyblue3'),
            "length": pygame.Color('lightskyblue3')
        }
        
        # Initialize field segments
        self._init_field_elements()
        self._calculate_segment_coverage()
        
        # Calculate initial shot probabilities
        self._update_shot_probabilities()

    def _init_field_elements(self):
        """Initialize field elements, segments, and fielders"""
        # Calculate wedge angles
        self.wedge_angles = [i * 360/self.config.num_wedges for i in range(self.config.num_wedges)]
        
        # Calculate radial lines
        self.radial_lines: List[Tuple[Point, Point]] = []
        for angle in self.wedge_angles:
            rad = math.radians(angle)
            dx, dy = math.cos(rad), math.sin(rad)

            # Solve for ellipse intersection
            denom = math.sqrt((dx*dx)/(self.ellipse_rx*self.ellipse_rx) +
                            (dy*dy)/(self.ellipse_ry*self.ellipse_ry))
            t = 1.0 / denom

            end_x = self.ellipse_cx + dx * t
            end_y = self.ellipse_cy + dy * t

            self.radial_lines.append((self.batsman_pos, (end_x, end_y)))
        
        # Create segments
        self.segments: List[Segment] = []
        for i in range(self.config.num_wedges):
            start_ray = self.radial_lines[i]
            end_ray = self.radial_lines[(i + 1) % self.config.num_wedges]

            for z in range(self.config.num_zones):
                t0 = z / self.config.num_zones
                t1 = (z+1) / self.config.num_zones

                # Four corners of that wedge-zone
                p1_inner = GeometryUtils.lerp(*start_ray, t0)
                p1_outer = GeometryUtils.lerp(*start_ray, t1)
                p2_outer = GeometryUtils.lerp(*end_ray, t1)
                p2_inner = GeometryUtils.lerp(*end_ray, t0)

                poly = [p1_inner, p1_outer, p2_outer, p2_inner]
                self.segments.append({
                    'id': f"W{i}Z{z}",
                    'poly': poly,
                    'coverage': 0
                })
        
        # Default fielder positions
        self.fielders = [
            (700, 300),  # Wicket-keeper
            (630, 500),  # Mid-off
            (650, 410),  # Short cover
            (500, 300),  # Deep point
            (685, 290),  # 1st slip
            (670, 292),  # 2nd slip
            (655, 298),  # 3rd slip
            (790, 425),  # Midwicket
            (850, 225),  # Fine leg
            (750, 625),  # Long on
        ]

    def _calculate_segment_coverage(self):
        """Calculate which segments are covered by fielders"""
        # Reset coverage
        for segment in self.segments:
            segment['coverage'] = 0
        
        # Update segment coverage based on fielders
        for fielder in self.fielders:
            # Calculate distance from the batsman
            distance_to_batsman = math.sqrt(
                (fielder[0] - self.batsman_pos[0])**2 + 
                (fielder[1] - self.batsman_pos[1])**2
            )
            
            # Adjust coverage radius based on distance to batsman
            adjusted_range = max(10, self.config.fielder_range + int(distance_to_batsman * 0.25))

            for segment in self.segments:
                if segment['id'] in ['W4Z0', 'W4Z1', 'W4Z2']:
                    segment['coverage'] = 1
                if GeometryUtils.circle_intersects_polygon(fielder, adjusted_range, segment['poly']):
                    segment['coverage'] += 1

    def _update_shot_probabilities(self):
        """Update shot probabilities based on current game state"""
        self.potential_shots = ShotAnalyzer.find_potential_shots(
            self.segments,
            self.current_delivery_line, 
            self.current_delivery_length, 
            batsman
        )
        self.adjusted_potential_shots = ShotAnalyzer.adjust_potential_shots(
            self.potential_shots, 
            self.aggression_level
        )
        self.shot_probabilities = ShotAnalyzer.calculate_potential_shot_probabilities(
            self.adjusted_potential_shots
        )
        # Sort the shot probabilities in descending order
        self.shot_probabilities = dict(sorted(
            self.shot_probabilities.items(), 
            key=lambda item: item[1], 
            reverse=True
        ))
        
        # Calculate zone probabilities
        self.zones_probabilities: Dict[str, float] = {}
        for segment_id, probability in self.shot_probabilities.items():
            if segment_id.startswith('W'):
                zone = segment_id.split('Z')[1]
                if zone not in self.zones_probabilities:
                    self.zones_probabilities[zone] = 0
                self.zones_probabilities[zone] += probability

    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up()

            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event)
            
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event)

    def _handle_mouse_down(self, event: pygame.event.Event):
        """Handle mouse down events"""
        mouse_pos = pygame.mouse.get_pos()
        for i, fielder in enumerate(self.fielders):
            fx, fy = fielder
            if math.hypot(mouse_pos[0] - fx, mouse_pos[1] - fy) < 10:
                self.selected_fielder = i
                self.offset_x = fx - mouse_pos[0]
                self.offset_y = fy - mouse_pos[1]
                break
        for key in self.input_boxes:
            if self.input_boxes[key].collidepoint(event.pos):
                self.input_active[key] = True
            else:
                self.input_active[key] = False

    def _handle_mouse_up(self):
        """Handle mouse up events"""
        if self.selected_fielder is not None:
            self.selected_fielder = None
            # Recalculate segment coverage
            self._calculate_segment_coverage()
            self._update_shot_probabilities()
            self.print_shot_analysis()

    def _handle_mouse_motion(self, event: pygame.event.Event):
        """Handle mouse motion events"""
        if self.selected_fielder is not None:
            mouse_x, mouse_y = event.pos
            self.fielders[self.selected_fielder] = (mouse_x + self.offset_x, mouse_y + self.offset_y)

    def _handle_key_down(self, event: pygame.event.Event):
        """Handle key down events"""
        if event.key == pygame.K_RIGHT:
            self.selected_wedge = (self.selected_wedge + 1) % self.config.num_wedges
        elif event.key == pygame.K_LEFT:
            self.selected_wedge = (self.selected_wedge - 1) % self.config.num_wedges
        elif event.key == pygame.K_g:
            self.grid_enabled = not self.grid_enabled
        elif event.key == pygame.K_z:
            self.zones_enabled = not self.zones_enabled
        elif event.key == pygame.K_f:
            self.fielder_coverage_enabled = not self.fielder_coverage_enabled
        
        for key in self.input_active:
            if self.input_active[key]:
                if event.key == pygame.K_RETURN:
                    self.input_active[key] = False
                    self._update_shot_probabilities()
                    self.print_shot_analysis()
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text[key] = self.input_text[key][:-1]
                elif event.unicode.isdigit():
                    self.input_text[key] += event.unicode

    def _draw(self):
        """Draw all elements to the screen"""
        self._update_input_values()
        self._clear_surfaces()
        self._draw_background()
        
        if self.grid_enabled:
            self._draw_grid()
        
        if self.zones_enabled:
            self._draw_zones()
        
        if self.fielder_coverage_enabled:
            self._draw_fielder_coverage()
        
        self._draw_highlights()
        self._draw_pitch()
        self._draw_players()
        self._draw_zone_probabilities()
        self._draw_segment_probabilities()
        self._draw_ui()
        
        # Final compositing
        self.screen.blit(self.coverage_surface, (0, 0))
        self.screen.blit(self.highlight_surface, (0, 0))
        
        pygame.display.flip()

    def _update_input_values(self):
        """Update game values from input boxes"""
        if self.input_text["line"] and self.input_text["length"]:
            try:
                self.current_delivery_line = int(self.input_text["line"])
                self.current_delivery_length = int(self.input_text["length"])
            except ValueError:
                pass  # Ignore invalid values

    def _clear_surfaces(self):
        """Clear the transparent surfaces"""
        self.coverage_surface.fill((0, 0, 0, 0))
        self.highlight_surface.fill((0, 0, 0, 0))
        self.screen.fill(self.colors['DARK_BG'])

    def _draw_background(self):
        """Draw the basic field background"""
        # Draw oval ground
        pygame.draw.ellipse(
            self.screen, 
            self.colors['DARK_GREEN'], 
            (
                self.config.field_x, 
                self.config.field_y, 
                self.config.field_width, 
                self.config.field_height
            )
        )
        
        # Draw boundary line
        pygame.draw.ellipse(self.screen, self.colors['LIGHT_GRAY'], (460, 160, 480, 480), 2)

        # Draw inner circle
        if self.inner_circle_enabled:
            pygame.draw.circle(self.screen, self.colors['LIGHT_GRAY'], (700, 400), 130, 2)

    def _draw_grid(self):
        """Draw coordinate grid"""
        # Draw grid lines and numbers
        for x in range(0, self.config.width, 25):
            pygame.draw.line(self.screen, self.colors['GRID_COLOR'], (x, 0), (x, self.config.height))
            text = self.font.render(str(x), True, self.colors['LIGHT_GRAY'])
            self.screen.blit(text, (x, 5))
            
        for y in range(0, self.config.height, 25):
            pygame.draw.line(self.screen, self.colors['GRID_COLOR'], (0, y), (y, self.config.height))
            text = self.font.render(str(y), True, self.colors['LIGHT_GRAY'])
            self.screen.blit(text, (5, y))

    def _draw_zones(self):
        """Draw zone divisions on the field"""
        # Draw radial lines
        for ray in self.radial_lines:
            pygame.draw.line(self.screen, self.colors['ZONE_COLOR'], ray[0], ray[1], 1)

        # Draw zones by connecting pairs of wedge lines
        for i in range(len(self.radial_lines)):
            start_ray = self.radial_lines[i]
            next_ray = self.radial_lines[(i+1) % len(self.radial_lines)]
            for z in range(self.config.num_zones):
                t0 = z / self.config.num_zones
                t1 = (z+1) / self.config.num_zones

                # lerp from batsman_pos → boundary_point
                p1_i = GeometryUtils.lerp(start_ray[0], start_ray[1], t0)
                p1_o = GeometryUtils.lerp(start_ray[0], start_ray[1], t1)
                p2_o = GeometryUtils.lerp(next_ray[0], next_ray[1], t1)
                p2_i = GeometryUtils.lerp(next_ray[0], next_ray[1], t0)

                pygame.draw.polygon(
                    self.screen, self.colors['ZONE_COLOR'],
                    [p1_i, p1_o, p2_o, p2_i], 1
                )

    def _draw_fielder_coverage(self):
        """Draw fielder coverage areas"""
        for pos in self.fielders:
            distance_to_batsman = math.sqrt((pos[0] - self.batsman_pos[0])**2 + (pos[1] - self.batsman_pos[1])**2)
            
            # Adjust coverage radius based on distance to batsman
            adjusted_range = max(10, self.config.fielder_range + int(distance_to_batsman * 0.25))
            
            pygame.draw.circle(self.coverage_surface, self.colors['COVERAGE_COLOR'], pos, adjusted_range)

    def _draw_highlights(self):
        """Draw highlighted segments"""
        # Draw coverage highlights
        for seg in self.segments:
            if seg['coverage'] > 0:
                alpha = min(255, int(255 * (seg['coverage'] / len(self.fielders))))
                color = (255, 255, 0, alpha)
                pygame.draw.polygon(self.highlight_surface, color, seg['poly'])
        
        # Highlight the selected wedge
        for segment in self.segments:
            if segment['id'].startswith(f"W{self.selected_wedge}Z"):
                pygame.draw.polygon(self.screen, (0, 200, 255), segment['poly'], 2)  # cyan outline

    def _draw_pitch(self):
        """Draw the cricket pitch"""
        # Draw pitch
        pygame.draw.rect(self.screen, self.colors['PITCH_COLOUR'], (693, 350, 15, 100))
        
        # Draw crease lines
        pygame.draw.line(self.screen, self.colors['LIGHT_GRAY'], (690, 350), (710, 350), 1)
        pygame.draw.line(self.screen, self.colors['LIGHT_GRAY'], (690, 450), (710, 450), 1)

    def _draw_players(self):
        """Draw all players and ball"""
        # Draw fielders
        for pos in self.fielders:
            pygame.draw.circle(self.screen, self.colors['WHITE'], pos, 4)
        
        # Draw batsman
        pygame.draw.circle(self.screen, self.colors['RED'], self.batsman_pos, 4)

        # Draw bowler
        pygame.draw.circle(self.screen, self.colors['WHITE'], (695, 525), 4)

        # Draw ball
        ball_pos = (700, 375)
        pygame.draw.circle(self.screen, self.colors['WHITE'], ball_pos, 2)

    def _draw_zone_probabilities(self):
        """Draw zone probabilities on the left side of the screen"""
        # Background panel - make it slimmer
        panel_rect = pygame.Rect(10, 50, 120, 280)  # Reduced width from 140 to 120, moved left from 20 to 10
        panel_color = (40, 40, 40)  # Slightly lighter than background
        pygame.draw.rect(self.screen, panel_color, panel_rect)
        pygame.draw.rect(self.screen, self.colors['LIGHT_GRAY'], panel_rect, 1)  # Border
        
        # Title
        title_font = pygame.font.SysFont('Arial', 13)  # Slightly smaller font
        title = title_font.render("Zone Probabilities", True, self.colors['WHITE'])
        self.screen.blit(title, (panel_rect.x + 5, panel_rect.y + 5))
        
        # Sort zone probabilities in descending order
        sorted_zones = sorted(
            self.zones_probabilities.items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        
        # Display each zone with its probability
        y_offset = 35  # Reduced from 40
        zone_font = pygame.font.SysFont('Arial', 12)  # Smaller font
        
        for zone, probability in sorted_zones:
            # Create color based on probability (higher = more green)
            green_value = min(255, int(255 * probability * 5))
            zone_color = (255 - green_value, green_value, 0)
            
            # Zone label
            zone_text = zone_font.render(f"Zone {zone}:", True, self.colors['WHITE'])
            self.screen.blit(zone_text, (panel_rect.x + 5, panel_rect.y + y_offset))
            
            # Probability value
            prob_text = zone_font.render(f"{probability:.3f}", True, zone_color)  # Show 3 decimals instead of 4
            self.screen.blit(prob_text, (panel_rect.x + 65, panel_rect.y + y_offset))  # Adjusted position
            
            # Progress bar background - made narrower
            bar_rect = pygame.Rect(panel_rect.x + 5, panel_rect.y + y_offset + 18, 110, 6)  # Slimmer bar
            pygame.draw.rect(self.screen, (70, 70, 70), bar_rect)
            
            # Probability bar
            bar_width = int(110 * probability)  # Adjusted to match new width
            if bar_width > 0:
                prob_bar_rect = pygame.Rect(panel_rect.x + 5, panel_rect.y + y_offset + 18, bar_width, 6)
                pygame.draw.rect(self.screen, zone_color, prob_bar_rect)
            
            y_offset += 32  # Slightly reduce spacing between entries

    def _draw_segment_probabilities(self):
        """Draw top 10 segment probabilities on the right side of the screen"""
        # Background panel
        panel_rect = pygame.Rect(1270, 10, 120, 400)  # Right side of screen
        panel_color = (40, 40, 40)  # Same as zone probabilities panel
        pygame.draw.rect(self.screen, panel_color, panel_rect)
        pygame.draw.rect(self.screen, self.colors['LIGHT_GRAY'], panel_rect, 1)  # Border
        
        # Title
        title_font = pygame.font.SysFont('Arial', 14)
        title = title_font.render("Top Segments", True, self.colors['WHITE'])
        self.screen.blit(title, (panel_rect.x + 5, panel_rect.y + 5))
        
        # Get top 10 segments (filter out special segments like OUT, LEAVE, etc.)
        top_segments = [
            (seg_id, prob) for seg_id, prob in self.shot_probabilities.items()
            if seg_id.startswith('W')  # Only include actual field segments
        ][:10]  # Take only top 10
        
        # Display each segment with its probability
        y_offset = 35
        segment_font = pygame.font.SysFont('Arial', 12)
        
        for segment_id, probability in top_segments:
            # Create color based on probability (higher = more green)
            green_value = min(255, int(255 * probability * 5))
            segment_color = (255 - green_value, green_value, 0)
            
            # Segment label
            segment_text = segment_font.render(f"{segment_id}:", True, self.colors['WHITE'])
            self.screen.blit(segment_text, (panel_rect.x + 5, panel_rect.y + y_offset))
            
            # Probability value
            prob_text = segment_font.render(f"{probability:.3f}", True, segment_color)
            self.screen.blit(prob_text, (panel_rect.x + 65, panel_rect.y + y_offset))
            
            # Progress bar background
            bar_rect = pygame.Rect(panel_rect.x + 5, panel_rect.y + y_offset + 18, 110, 6)
            pygame.draw.rect(self.screen, (70, 70, 70), bar_rect)
            
            # Probability bar
            bar_width = int(110 * probability)
            if bar_width > 0:
                prob_bar_rect = pygame.Rect(panel_rect.x + 5, panel_rect.y + y_offset + 18, bar_width, 6)
                pygame.draw.rect(self.screen, segment_color, prob_bar_rect)
            
            y_offset += 32

    def _draw_ui(self):
        """Draw UI elements"""
        # Display current wedge index
        wedge_text = self.font.render(f"Wedge: W{self.selected_wedge}", True, (255, 255, 255))
        self.screen.blit(wedge_text, (20, 20))  # Top-left corner

        # Draw input boxes
        for key in self.input_boxes:
            pygame.draw.rect(self.screen, self.input_colors[key], self.input_boxes[key], 2)
            txt_surface = self.font.render(self.input_text[key], True, (255, 255, 255))
            self.screen.blit(txt_surface, (self.input_boxes[key].x + 5, self.input_boxes[key].y + 5))

        # Add labels for input boxes
        line_label = self.font.render("Line:", True, (255, 255, 255))
        self.screen.blit(line_label, (560, 24))
        length_label = self.font.render("Length:", True, (255, 255, 255))
        self.screen.blit(length_label, (550, 64))

    def run(self):
        """Main game loop"""
        self.print_shot_analysis()
        while self.running:
            if self.event_handler.is_modified():
                self.observer.stop()
                self.observer.join()
                pygame.quit()
                restart_program()
            self._handle_events()
            self._draw()
        
        self.observer.stop()
        self.observer.join()
        pygame.quit()
        sys.exit()
        pygame.quit()

    def print_shot_analysis(self):
        """Print analysis of shot probabilities"""
        sorted_potential_shots = sorted(
            self.potential_shots.items(),
            key=lambda item: item[1][0],  # Sort by shot value (first element in the tuple)
            reverse=True  # Descending order
        )
        print("Potential shots based on current delivery line and length:")
        for segment_id, (shot_value, shot_name) in sorted_potential_shots:
            print(f"Segment: {segment_id}, Shot Value: {shot_value}, Shot Name: {shot_name}")