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

def clearPath(board, x0, y0, x1, y1, stepSize = 0.25):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    samples = max(1, int(length / stepSize))
    for i in range(1, samples + 1):
        t = i / samples
        if board.toolAt(math.floor(x0 + dx * t), math.floor(y0 + dy * t)):
            return False

    return True