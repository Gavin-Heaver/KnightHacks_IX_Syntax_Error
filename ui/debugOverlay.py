import pygame
import config
from ai.flowField import nextStep, INF

ARROW_COLOR = (90, 110, 130)
ARROW_LEN = config.TILE * 0.35      # how far each arrow reaches from its tile center


def drawFlowArrows(screen, board, dist):
    for y in range(board.height):
        for x in range(board.width):

            # nothing to draw on occupied or unreachable tiles
            if board.toolAt(x, y) or board.isCpu(x, y) or dist[y][x] == INF:
                continue

            step = nextStep(dist, board, x, y)
            if step is None:
                continue
            dx, dy = step

            # pixel center of this tile
            cx = config.BOARD_X + (x + 0.5) * config.TILE
            cy = config.BOARD_Y + (y + 0.5) * config.TILE

            # normalize so diagonal arrows are the same length as straight ones
            length = (dx * dx + dy * dy) ** 0.5
            ex = cx + dx / length * ARROW_LEN
            ey = cy + dy / length * ARROW_LEN

            pygame.draw.line(screen, ARROW_COLOR, (cx, cy), (ex, ey), 1)
            pygame.draw.circle(screen, ARROW_COLOR, (int(ex), int(ey)), 2)   # dot = arrowhead


def drawHeatmap(screen, grid, color=(255, 60, 60)):
    peak = max(max(row) for row in grid)
    if peak <= 0.01:
        return

    # draw onto a see-through layer, then put the whole layer on screen at once
    layer = pygame.Surface((config.BOARD_PX_W, config.BOARD_PX_H), pygame.SRCALPHA)
    for y, row in enumerate(grid):
        for x, v in enumerate(row):
            if v > 0.01:
                alpha = int(180 * min(1.0, v / peak))
                layer.fill((*color, alpha), (x * config.TILE, y * config.TILE, config.TILE, config.TILE))
    screen.blit(layer, (config.BOARD_X, config.BOARD_Y))