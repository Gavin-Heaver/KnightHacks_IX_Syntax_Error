import config
from ai.flowField import buildField

def buildFireLayer(board):
    fire = [[0.0] * board.width for _ in range(board.height)]

    for tool in board.allTools():
        dps = getattr(tool, "damage", 0) * getattr(tool, "fireRate", 0)
        if dps <= 0:
            dps = getattr(tool, "dps", 0)
        if dps <= 0:
            continue

        r = tool.range
        reach = int(r) + 1

        for dy in range(-reach, reach + 1):
            for dx in range(-reach, reach + 1):
                tx, ty = tool.x + dx, tool.y + dy
                if not board.inBounds(tx, ty):
                    continue

                if dx * dx + dy * dy <= r * r:
                    fire[ty][tx] += dps

    return fire

def makeCost(board, enemyType, fire, fear, fireWeight = None):
    w = config.AI_WEIGHTS[enemyType]
    if fireWeight is None:
        fireWeight = w["fire"]
    plasma = board.plasmaTiles

    def cost(x, y):
        if (x, y) in plasma:
            return None

        if board.isCpu(x, y):
            return 1.0

        tool = board.toolAt(x, y)

        if enemyType == "injection" and tool is not None and getattr(tool, "kind", "") == "firewall":
            return None

        c = 1.0
        if tool is not None:
            c += w["wall"] * tool.hp / config.BUG_DPS
        c += fireWeight * fire[y][x]
        c += w["fear"] * fear[y][x]
        return c

    return cost


def toolTargetTiles(board):
    targets = set()
    for tool in board.allTools():
        if not getattr(tool, "programmable", False) or getattr(tool, "corrupted", False):
            continue
        for nx, ny in board.neighbors(tool.x, tool.y):
            if board.isBuildable(nx, ny):
                targets.add((nx, ny))
    return list(targets)

def buildFields(board, fear):
    fire = buildFireLayer(board)
    towerGoals = toolTargetTiles(board)
    fields = {"cpu": {}, "tower": {}}
    for enemyType in config.AI_WEIGHTS:
        fields["cpu"][enemyType] = buildField(board, board.cpuTiles, fieldCost(board, "cpu", enemyType, fire, fear))
        if config.TOWER_TARGET_CHANCE.get(enemyType, 0) > 0:
            goals = towerGoals
            if not goals and enemyType != "injection":
                goals = board.cpuTiles
            fields["tower"][enemyType] = buildField(board, goals, fieldCost(board, "tower", enemyType, fire, fear))
    return fields


def fieldCost(board, target, enemyType, fire, fear):
    fireWeight = 0.0 if target == "tower" else None
    return makeCost(board, enemyType, fire, fear, fireWeight)