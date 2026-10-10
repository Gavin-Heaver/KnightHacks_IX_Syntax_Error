# entities/enemy.py -- Enemy base (+ Bug, MemoryLeak, ZeroDay, Injection by Tadhg).
# x, y are float TILE units (tile (i, j) center = (i + 0.5, j + 0.5)).
import config
import math
from game import events
from ai.flowField import nextStep


class Enemy:
    def __init__(self, enemyType, x, y):
        stats = config.ENEMY_STATS[enemyType]
        self.type = enemyType
        self.x = x
        self.y = y
        self.hp = stats["hp"]
        self.maxHp = stats["hp"]
        self.speed = stats["speed"]
        self.reward = stats["reward"]
        self.dps = stats["dps"]
        self.revealed = False        # set by Debugger
        self.alive = True

    def takeDamage(self, n):
        if not self.alive:
            return
        self.hp -= n
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            events.emit("enemyKilled", self)

    def update(self, dt, board, dist):
        if not self.alive:
            return

        #finding which tile subject is positioned
        tileX, tileY = int(self.x), int(self.y)

        #finding the gradient pointing towards the CPU- if none, stay put
        step = nextStep(dist, board, tileX, tileY)
        if step is None:
            return

        dx, dy = step
        targetTX, targetTY = tileX + dx, tileY + dy

        #CPU found, subject attacks and CPU takes damage
        if board.isCpu(targetTX, targetTY):
            events.emit("cpuHit", self, self.dps * dt)
            return

        #tool found, subject attacks and tool takes damage
        tool = board.toolAt(targetTX, targetTY)
        if tool:
            tool.takeDamage(self.dps * dt)
            return

        #finding center of tile
        targetX, targetY = targetTX + 0.5, targetTY + 0.5
        #calculating vector between source and target
        vx, vy = targetX - self.x, targetY - self.y
        #calculating distance of vector
        distance = math.hypot(vx, vy)
        #finding maximum distance able to be moved on current frame
        move = self.speed * dt

        if move >= distance:
            self.x, self.y = targetX, targetY
        else:
            self.x += vx / distance * move
            self.y += vy / distance * move

class FakeEnemy(Enemy):
    """Stub that stands still so turrets/scripts can be tested before real AI exists."""

    def __init__(self, x=0.5, y=0.5):
        super().__init__("bug", x, y)

