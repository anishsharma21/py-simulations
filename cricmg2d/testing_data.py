from typing import Dict
from _types import Batsman, ShotData, ShotName

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