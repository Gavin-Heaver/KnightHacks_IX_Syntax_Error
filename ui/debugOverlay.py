import pygame
import config
from ai.flowField import nextStep, INF

ARROW_COLOR = (90, 110, 130)
ARROW_LEN = config.TILE * 0.35



def drawFlowArrows(screen, board, dist):
    for y in range(board.height):
        for x in range(board.width):

            #nothing to draw on occupied cells
            if board.toolAt(x, y) or board.isCpu(x, y) or dist[y][x] == INF:
                continue

            step = nextStep(dist, board, x, y)
            if step is None:
                continue
            dx, dy = step

            cx = config.BOARD_X + (x + 0.5) * config.TILE
            cy = config.BOARD_Y + (y + 0.5) * config.TILE

            length = (dx * dx + dy * dy) ** 0.5
            ex = cx + dx / length * ARROW_LEN
            ey = cy + dy / length * ARROW_LEN

            pygame.draw.line(screen, ARROW_COLOR, (cx, cy), (ex, ey), 1)
            pygame.draw.circle(screen, ARROW_COLOR, (int(ex), int(ey)), 2)