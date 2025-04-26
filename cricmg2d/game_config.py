from dataclasses import dataclass

@dataclass
class GameConfig:
    """Configuration for the cricket field simulation"""
    width: int = 800
    height: int = 600
    field_x: float = 150
    field_width: float = 500
    field_y: float = 50
    field_height: float = 500
    num_wedges: int = 18  # 20° wedges
    num_zones: int = 7
    fielder_range: float = 10