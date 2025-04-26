import math
from typing import List
from _types import Point

class GeometryUtils:
    """Utility functions for geometric calculations"""
    
    @staticmethod
    def circle_intersects_polygon(circle_center: Point, radius: float, polygon: List[Point]) -> bool:
        # Check if circle center is inside the polygon
        if GeometryUtils.point_inside_polygon(circle_center, polygon):
            return True
        
        # Check if circle intersects any edge of the polygon
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]
            if GeometryUtils.line_intersects_circle(p1, p2, circle_center, radius):
                return True
        
        # Check if any polygon vertex is inside the circle
        for point in polygon:
            dx = point[0] - circle_center[0]
            dy = point[1] - circle_center[1]
            if dx * dx + dy * dy <= radius * radius:
                return True

        return False

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def lerp(p: Point, q: Point, t: float) -> Point:
        """Linear interpolation between two points"""
        return (p[0] + (q[0]-p[0])*t, p[1] + (q[1]-p[1])*t)