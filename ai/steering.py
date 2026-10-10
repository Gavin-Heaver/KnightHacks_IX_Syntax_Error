import math

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