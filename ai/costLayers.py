import config
from ai.flowField import buildField

def buildFireLayer(board):
    fire = [[0,0] * board.width for _ in range(board.height)]

    for tool in board.allTools():
        dps = getattr(tool, "damage", 0) * getattr(tool, "fireRate", 0)
        if dps <= 0:
            return

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

def makeCost(board, enemyType, fire):
    w = config.AI_WEIGHTS[enemyType]

    def cost(x, y):
        if board.isCpu(x, y):
            return 1.0

        tool = board.toolAt(x, y)

        if enemyType == "injection" and tool is not None and getattr(tool, "kind", "") == "firewall":
            return None

        c = 1.0
        if tool is not None:
            c += w["wall"] * tool.hp / config.BUG_DPS
        c += w["fire"] * fire[y][x]
        return c

    return cost
        

def buildFields(board):
    fire = buildFireLayer(board)
    fields = {}
    for enemyType in config.AI_WEIGHTS:
        fields[enemyType] = buildField(board, board.cpuTiles, makeCost(board, enemyType, fire))

    return fields