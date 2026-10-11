import pygame
import config
from ai.flowField import nextStep, INF
from ai.costLayers import buildFireLayer, fieldCost

ARROW_COLOR = (90, 110, 130)
ARROW_LEN = config.TILE * 0.35          # how far each arrow reaches from its tile center
COST_COLOR = (255, 170, 40)
FEAR_COLOR = (255, 60, 60)
COST_SCALE = 16.0                        # extra cost (above the base 1.0) drawn fully opaque
FEAR_SCALE = config.PHEROMONE_DEPOSIT   # one fresh death drawn fully opaque
MODES = ["off", "flow", "cost", "fear"]


class DebugOverlay:
    def __init__(self):
        self.mode = 0
        self.view = 0
        self.layer = None
        self.cacheKey = None
        self.cachedFields = None
        self.cachedFear = None
        self.font = pygame.font.SysFont("consolas", 14)

    def cycleMode(self):
        self.mode = (self.mode + 1) % len(MODES)

    def cycleView(self):
        self.view += 1

    def draw(self, screen, board, fields, fear):
        if MODES[self.mode] == "off":
            return

        views = [(target, enemyType) for target in fields for enemyType in fields[target]]
        target, enemyType = views[self.view % len(views)]

        #fields and the fear grid are new objects after every rebuild / AI tick -> only re-render then
        key = (self.mode, target, enemyType)
        if key != self.cacheKey or fields is not self.cachedFields or fear is not self.cachedFear:
            self.layer = self._render(board, fields[target][enemyType], fear, target, enemyType)
            self.cacheKey, self.cachedFields, self.cachedFear = key, fields, fear

        screen.blit(self.layer, (config.BOARD_X, config.BOARD_Y))
        label = f"{MODES[self.mode].upper()}: {enemyType} -> {target}    [F1 mode  F2 field]"
        screen.blit(self.font.render(label, True, config.COLOR_TEXT), (config.BOARD_X + 4, config.BOARD_Y + 4))

    def _render(self, board, dist, fear, target, enemyType):
        layer = pygame.Surface((config.BOARD_PX_W, config.BOARD_PX_H), pygame.SRCALPHA)
        mode = MODES[self.mode]

        if mode == "cost":
            fire = buildFireLayer(board)
            cost = fieldCost(board, target, enemyType, fire, fear)

        for y in range(board.height):
            for x in range(board.width):
                #nothing to draw on occupied tiles (tools / CPU are drawn by the board)
                if board.toolAt(x, y) or board.isCpu(x, y):
                    continue

                if mode == "flow":
                    if dist[y][x] == INF:
                        continue
                    step = nextStep(dist, board, x, y)
                    if step is None:
                        continue
                    dx, dy = step
                    cx, cy = (x + 0.5) * config.TILE, (y + 0.5) * config.TILE
                    length = (dx * dx + dy * dy) ** 0.5     # diagonals same length as straights
                    ex, ey = cx + dx / length * ARROW_LEN, cy + dy / length * ARROW_LEN
                    pygame.draw.line(layer, ARROW_COLOR, (cx, cy), (ex, ey), 1)
                    pygame.draw.circle(layer, ARROW_COLOR, (int(ex), int(ey)), 2)

                elif mode == "cost":
                    extra = cost(x, y) - 1.0
                    if extra > 0.01:
                        alpha = int(180 * min(1.0, extra / COST_SCALE))
                        layer.fill((*COST_COLOR, alpha), (x * config.TILE, y * config.TILE, config.TILE, config.TILE))

                elif mode == "fear":
                    v = fear[y][x]
                    if v > 0.01:
                        alpha = int(180 * min(1.0, v / FEAR_SCALE))
                        layer.fill((*FEAR_COLOR, alpha), (x * config.TILE, y * config.TILE, config.TILE, config.TILE))

        return layer
