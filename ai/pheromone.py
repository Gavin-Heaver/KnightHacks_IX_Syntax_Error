import math
import config
from game import events

NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class PheromoneMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0.0] * width for _ in range(height)]     # fear[y][x]
        events.subscribe("enemyKilled", self.onEnemyKilled)

    def onEnemyKilled(self, enemy):
        x, y = math.floor(enemy.x), math.floor(enemy.y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] += config.PHEROMONE_DEPOSIT

    def tick(self):
        newGrid = [[0.0] * self.width for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                # average of the 4-way neighbors that are on the board
                total, count = 0.0, 0
                for dx, dy in NEIGHBORS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        total += self.grid[ny][nx]
                        count += 1
                avg = total / count if count else 0.0

                # keep 60% of this tile, take 40% from the neighborhood, then fade
                newGrid[y][x] = config.PHEROMONE_DECAY * (0.6 * self.grid[y][x] + 0.4 * avg)

        self.grid = newGrid

    def carryOver(self):
        for row in self.grid:
            for x in range(self.width):
                row[x] *= config.PHEROMONE_CARRYOVER

    def isActive(self):
        return any(v > 0.01 for row in self.grid for v in row)