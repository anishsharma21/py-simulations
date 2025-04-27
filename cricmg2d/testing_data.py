from typing import Dict
from _types import Aggression, Batsman, ShotData, ShotName, Power, Line, Length

shots: Dict[ShotName, ShotData] = {
    ShotName.PULL_SHOT: {
        'wedges': [0, 1, 2, 17],
        'power': (Power.THREE, Power.SEVEN),
        'line': (Line.OUTSIDE_OFF, Line.OUTSIDE_LEG),
        'length': (Length.SHORT, Length.BACK_OFF_A_LENGTH)
    },
    ShotName.SLOG: {
        'wedges': [1, 2],
        'power': (Power.FIVE, Power.SEVEN),
        'line': (Line.OUTSIDE_OFF, Line.STUMPS),
        'length': (Length.BACK_OFF_A_LENGTH, Length.GOOD)
    },
    ShotName.ON_DRIVE: {
        'wedges': [3],
        'power': (Power.FOUR, Power.SEVEN),
        'line': (Line.STUMPS, Line.OUTSIDE_LEG),
        'length': (Length.GOOD, Length.FULL_TOSS)
    },
    ShotName.STRAIGHT_DRIVE: {
        'wedges': [4],
        'power': (Power.FOUR, Power.SEVEN),
        'line': (Line.STUMPS, Line.STUMPS),
        'length': (Length.GOOD, Length.FULL_TOSS)
    },
    ShotName.OFF_DRIVE: {
        'wedges': [5],
        'power': (Power.FOUR, Power.SEVEN),
        'line': (Line.OUTSIDE_OFF, Line.OUTSIDE_OFF),
        'length': (Length.GOOD, Length.FULL_TOSS)
    },
    ShotName.COVER_DRIVE: {
        'wedges': [6, 7, 8],
        'power': (Power.FOUR, Power.SEVEN),
        'line': (Line.WIDE_OFF, Line.OUTSIDE_OFF),
        'length': (Length.GOOD, Length.FULL_TOSS)
    },
    ShotName.CUT: {
        'wedges': [9],
        'power': (Power.TWO, Power.SEVEN),
        'line': (Line.VERY_WIDE_OFF, Line.WIDE_OFF),
        'length': (Length.SHORT, Length.GOOD)
    },
    ShotName.SQUARE_CUT: {
        'wedges': [10],
        'power': (Power.TWO, Power.SEVEN),
        'line': (Line.VERY_WIDE_OFF, Line.WIDE_OFF),
        'length': (Length.SHORT, Length.GOOD)
    },
    ShotName.LATE_CUT: {
        'wedges': [11],
        'power': (Power.TWO, Power.SEVEN),
        'line': (Line.VERY_WIDE_OFF, Line.OUTSIDE_OFF),
        'length': (Length.VERY_SHORT, Length.GOOD)
    },
    ShotName.UPPER_CUT: {
        'wedges': [12, 13],
        'power': (Power.THREE, Power.SEVEN),
        'line': (Line.OUTSIDE_OFF, Line.STUMPS),
        'length': (Length.VERY_SHORT, Length.SHORT)
    },
    ShotName.LEG_GLANCE: {
        'wedges': [14, 15],
        'power': (Power.THREE, Power.SEVEN),
        'line': (Line.OUTSIDE_LEG, Line.OUTSIDE_LEG),
        'length': (Length.BACK_OFF_A_LENGTH, Length.FULL_TOSS)
    },
    ShotName.HOOK: {
        'wedges': [14, 15, 16],
        'power': (Power.FOUR, Power.SEVEN),
        'line': (Line.OUTSIDE_LEG, Line.OUTSIDE_LEG),
        'length': (Length.VERY_SHORT, Length.BACK_OFF_A_LENGTH)
    },
    ShotName.FLICK: {
        'wedges': [0, 1, 16, 17],
        'power': (Power.FIVE, Power.SEVEN),
        'line': (Line.STUMPS, Line.OUTSIDE_LEG),
        'length': (Length.FULL, Length.FULL_TOSS)
    },
    ShotName.BLOCK: {
        'wedges': [1, 2, 3, 4, 5, 6, 7, 8],
        'power': (Power.ONE, Power.ONE),
        'line': (Line.OUTSIDE_OFF, Line.STUMPS),
        'length': (Length.BACK_OFF_A_LENGTH, Length.FULL_TOSS)
    },
    ShotName.TAP: {
        'wedges': [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
        'power': (Power.TWO, Power.TWO),
        'line': (Line.OUTSIDE_OFF, Line.OUTSIDE_LEG),
        'length': (Length.BACK_OFF_A_LENGTH, Length.FULL_TOSS)
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
        'aggression': Aggression.VERY_ATTACKING,
    },
    'shots': {
        ShotName.PULL_SHOT: 80,
        ShotName.SLOG: 80,
        ShotName.ON_DRIVE: 80,
        ShotName.STRAIGHT_DRIVE: 80,
        ShotName.OFF_DRIVE: 80,
        ShotName.COVER_DRIVE: 80,
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