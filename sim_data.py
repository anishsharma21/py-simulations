from enum import Enum
from typing import Any, List, Tuple, Dict, TypedDict

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

shots: Dict[ShotName, ShotData] = {
    ShotName.PULL_SHOT: {
        'wedges': [0, 1, 2, 17],
        'power': (3, 7),
        'line': (3, 5),
        'length': (2, 3)
    },
    ShotName.SLOG: {
        'wedges': [1, 2],
        'power': (5, 7),
        'line': (3, 4),
        'length': (3, 5)
    },
    ShotName.ON_DRIVE: {
        'wedges': [3],
        'power': (4, 7),
        'line': (4, 5),
        'length': (4, 7)
    },
    ShotName.STRAIGHT_DRIVE: {
        'wedges': [4],
        'power': (4, 7),
        'line': (4, 4),
        'length': (4, 7)
    },
    ShotName.OFF_DRIVE: {
        'wedges': [5],
        'power': (4, 7),
        'line': (3, 3),
        'length': (4, 7)
    },
    ShotName.COVER_DRIVE: {
        'wedges': [6, 7, 8],
        'power': (4, 7),
        'line': (2, 3),
        'length': (4, 7)
    },
    ShotName.LOFTED_DRIVE: {
        'wedges': [3, 4, 5],
        'power': (6, 7),
        'line': (3, 5),
        'length': (5, 7)
    },
    ShotName.CUT: {
        'wedges': [9],
        'power': (2, 7),
        'line': (1, 2),
        'length': (2, 4)
    },
    ShotName.SQUARE_CUT: {
        'wedges': [10],
        'power': (2, 7),
        'line': (1, 2),
        'length': (2, 4)
    },
    ShotName.LATE_CUT: {
        'wedges': [11],
        'power': (2, 7),
        'line': (1, 3),
        'length': (1, 4)
    },
    ShotName.UPPER_CUT: {
        'wedges': [12, 13],
        'power': (3, 7),
        'line': (3, 4),
        'length': (1, 2)
    },
    ShotName.LEG_GLANCE: {
        'wedges': [14, 15],
        'power': (3, 7),
        'line': (5, 5),
        'length': (3, 7)
    },
    ShotName.HOOK: {
        'wedges': [14, 15, 16],
        'power': (4, 7),
        'line': (5, 5),
        'length': (1, 3)
    },
    ShotName.FLICK: {
        'wedges': [0, 1, 16, 17],
        'power': (5, 7),
        'line': (4, 5),
        'length': (5, 7)
    },
    ShotName.BLOCK: {
        'wedges': [1, 2, 3, 4, 5, 6, 7, 8],
        'power': (1, 2),
        'line': (3, 4),
        'length': (3, 7)
    },
    ShotName.TAP: {
        'wedges': [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
        'power': (1, 2),
        'line': (3, 5),
        'length': (3, 7)
    }
}

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

batsman: Batsman = {
    'base_traits': {
        'timing': 75,
        'judgement': 70,
        'stamina': 90,
    },
    'in_game_traits': {
        'fatigue': 10,
        'confidence': 30,
        'aggression': 'very defensive',
    },
    'shots': {
        ShotName.PULL_SHOT: 80,
        ShotName.SLOG: 80,
        ShotName.ON_DRIVE: 80,
        ShotName.STRAIGHT_DRIVE: 80,
        ShotName.OFF_DRIVE: 80,
        ShotName.COVER_DRIVE: 80,
        ShotName.LOFTED_DRIVE: 80,
        ShotName.CUT: 80,
        ShotName.SQUARE_CUT: 80,
        ShotName.LATE_CUT: 80,
        ShotName.UPPER_CUT: 80,
        ShotName.LEG_GLANCE: 80,
        ShotName.HOOK: 80,
        ShotName.FLICK: 80,
        ShotName.BLOCK: 80,
        ShotName.TAP: 80
    },
    'traits': {}
}


match_conditions = {
    'fielder_positioning': {
        1: {
            'x': 40,
            'y': 30
        }
    }
}