import math
import config

def separation(enemy, enemies, radius):
    sx, sy = 0, 0
    for other in enemies:
        dx, dy = enemy.x - other.x, enemy.y - other.y
        d = math.hypot(dx, dy)
        if 0 < d < radius:
            strength = (radius - d) / radius
            sx += dx / d * strength
            sy += dy / d * strength

    return sx, sy

def clearPath(board, x0, y0, x1, y1, stepSize = 0.25):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    samples = max(1, int(length / stepSize))
    for i in range(1, samples + 1):
        t = i / samples
        tx, ty = math.floor(x0 + dx * t), math.floor(y0 + dy * t)
        tool = board.toolAt(tx, ty)
        if (tool and not getattr(tool, "corrupted", False)) or (tx, ty) in board.plasmaTiles:
            return False

    return True


def separation(enemy, enemies, radius):
    refSize = 2 * config.ENEMY_STATS["bug"]["size"]
    sx, sy = 0, 0
    for other in enemies:
        dx, dy = enemy.x - other.x, enemy.y - other.y
        d = math.hypot(dx, dy)
        pairRadius = radius * (enemy.size + other.size) / refSize
        if 0 < d < pairRadius:
            strength = (pairRadius - d) / pairRadius
            sx += dx / d * strength
            sy += dy / d * strength
    return sx, sy