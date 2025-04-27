from enum import Enum, IntEnum
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
    CUT = 7
    SQUARE_CUT = 8
    LATE_CUT = 9
    UPPER_CUT = 10
    LEG_GLANCE = 11
    HOOK = 12
    FLICK = 13
    BLOCK = 14
    TAP = 15
    OUT = 16
    LEAVE = 17
    MISS = 18
    LEG_BYES = 19

class Power(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

class Line(IntEnum):
    VERY_WIDE_OFF = 1
    WIDE_OFF = 2
    OUTSIDE_OFF = 3
    STUMPS = 4
    OUTSIDE_LEG = 5
    WIDE_LEG = 6
    VERY_WIDE_LEG = 7

class Length(IntEnum):
    VERY_SHORT = 1
    SHORT = 2
    BACK_OFF_A_LENGTH = 3
    GOOD = 4
    FULL = 5
    YORKER = 6
    FULL_TOSS = 7

class ShotData(TypedDict):
    wedges: List[int]
    power: Tuple[Power, Power]
    line: Tuple[Line, Line]
    length: Tuple[Length, Length]

class BatsmanBaseTraits(TypedDict):
    timing: int
    judgement: int
    stamina: int

class BatsmanInGameTraits(TypedDict):
    fatigue: int
    confidence: int
    aggression: Aggression

class Batsman(TypedDict):
    base_traits: BatsmanBaseTraits
    in_game_traits: BatsmanInGameTraits
    shots: Dict[ShotName, int]
    traits: Any