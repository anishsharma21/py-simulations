from enum import Enum
from typing import Any, List, Tuple, Dict, TypedDict

RgbColor = Tuple[int, int, int]
RgbaColor = Tuple[int, int, int, int]
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

class ShotName(Enum):
    PULL_SHOT = 1
    SLOG = 2
    ON_DRIVE = 3
    STRAIGHT_DRIVE = 4
    OFF_DRIVE = 5
    COVER_DRIVE = 6
    LOFTED_DRIVE = 7
    CUT = 8
    SQUARE_CUT = 9
    LATE_CUT = 10
    UPPER_CUT = 11
    LEG_GLANCE = 12
    HOOK = 13
    FLICK = 14
    BLOCK = 15
    TAP = 16
    OUT = 17
    LEAVE = 18
    MISS = 19
    LEG_BYES = 20

class Power(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

class Line(Enum):
    VERY_WIDE_OFF = 1
    WIDE_OFF = 2
    OUTSIDE_OFF = 3
    STUMP = 4
    OUTSIDE_LEG = 5
    WIDE_LEG = 6
    VERY_WIDE_LEG = 7

class Length(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7

class ShotData(TypedDict):
    wedges: List[int]
    power: Tuple[int, int]
    line: Tuple[int, int]
    length: Tuple[int, int]

class BatsmanBaseTraits(TypedDict):
    timing: int
    judgement: int
    stamina: int

class BatsmanInGameTraits(TypedDict):
    fatigue: int
    confidence: int
    aggression: str

class Batsman(TypedDict):
    base_traits: BatsmanBaseTraits
    in_game_traits: BatsmanInGameTraits
    shots: Dict[ShotName, int]
    traits: Any