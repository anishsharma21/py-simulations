from typing import Dict, List, Set, Tuple
from _types import Aggression, Batsman, Segment, ShotData, ShotName
from testing_data import shots

class ShotAnalyzer:
    """Handles all shot analysis functionality"""
    
    @staticmethod
    def find_weak_areas(segments: List[Segment], threshold: int = 0) -> Set[str]:
        weak_areas: Set[str] = set()
        for segment in segments:
            if segment['coverage'] <= threshold:
                weak_areas.add(segment['id'])
        return weak_areas

    @staticmethod
    def segments_to_areas(segments: List[Segment]) -> Set[str]:
        areas: Set[str] = set()
        for segment in segments:
            areas.add(segment['id'])
        return areas

    @staticmethod
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

    @staticmethod
    def find_potential_shots(segments: List[Segment], current_delivery_line: int, current_delivery_length: int, batsman: Batsman) -> Dict[str, Tuple[float, ShotName]]:
        filtered_shots: Dict[ShotName, ShotData] = ShotAnalyzer.get_potential_shots(shots, current_delivery_line, current_delivery_length)

        segment_shot_values: Dict[str, Tuple[float, ShotName]] = {}
        for shot_name, data in filtered_shots.items():
            wedges: List[int] = data['wedges']
            power: Tuple[int, int] = data['power']

            for wedge_val in wedges:
                for power_val in power:
                    segment_id: str = f"W{wedge_val}Z{power_val}"
                    segment_shot_initial_value: float = batsman['shots'].get(shot_name, 0)
                    segment_shot_values[segment_id] = (segment_shot_initial_value, shot_name)
        
        weak_areas: Set[str] = ShotAnalyzer.find_weak_areas(segments, threshold=0)
        batsman_judgement_multiplier: float = 1 + (batsman['base_traits']['judgement'] / 100.0)
        for seg_id, seg_shot_val in segment_shot_values.items():
            if seg_id in weak_areas:
                seg_shot_val = (seg_shot_val[0] * batsman_judgement_multiplier, seg_shot_val[1])
                segment_shot_values[seg_id] = seg_shot_val
        
        return segment_shot_values

    @staticmethod
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

    @staticmethod
    def calculate_potential_shot_probabilities(segment_shot_values: Dict[str, Tuple[float, ShotName]]) -> Dict[str, float]:
        total_value: float = sum(value[0] for value in segment_shot_values.values())
        probabilities: Dict[str, float] = {}
        
        for seg_id, (shot_value, _) in segment_shot_values.items():
            probabilities[seg_id] = shot_value / total_value if total_value > 0 else 0
        
        return probabilities