# scripting/api.py -- EnemyView and execution context API for towers.
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class EnemyView:
    """Read-only view of an enemy exposed to player scripts."""
    hp: float
    distance: float
    speed: float
    type: str

    def __repr__(self):
        return f"EnemyView(hp={self.hp:.1f}, dist={self.distance:.1f}, speed={self.speed:.1f}, type='{self.type}')"


def createEnemyView(enemy, toolX, toolY):
    """Factory creating an EnemyView relative to a tool's position."""
    # enemy.x, enemy.y are in tile coordinates (center is x, y or x+0.5, y+0.5)
    # tool center is toolX + 0.5, toolY + 0.5
    dx = enemy.x - (toolX + 0.5)
    dy = enemy.y - (toolY + 0.5)
    dist = math.hypot(dx, dy)
    revealed_type = enemy.type if getattr(enemy, "revealed", False) else "unknown"
    return EnemyView(
        hp=float(enemy.hp),
        distance=round(dist, 2),
        speed=float(enemy.speed),
        type=revealed_type
    )


SAFE_BUILTINS = {
    "len": len,
    "min": min,
    "max": max,
    "abs": abs,
    "range": range,
    "sorted": sorted,
    "sum": sum,
    "bool": bool,
    "int": int,
    "float": float,
    "round": round,
    "True": True,
    "False": False,
    "None": None,
}

