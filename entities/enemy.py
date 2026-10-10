# entities/enemy.py -- Enemy base (+ Bug, MemoryLeak, ZeroDay, Injection by Tadhg).
# x, y are float TILE units (tile (i, j) center = (i + 0.5, j + 0.5)).
import config
import math
import random
import config
from game import events
from ai.flowField import nextStep
from ai.steering import separation


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
        self.offsetX = random.uniform(-0.3, 0.3)
        self.offsetY = random.uniform(-0.3, 0.3)

    def takeDamage(self, n):
        if not self.alive:
            return
        self.hp -= n
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            events.emit("enemyKilled", self)

    def update(self, dt, board, dist, enemies):
        if not self.alive:
            return

        #finding which tile subject is positioned
        tileX, tileY = int(self.x), int(self.y)

        sepX, sepY = separation(self, enemies, config.SEPARATION_RADIUS)

        #finding the gradient pointing towards the CPU- if none, stay put
        step = nextStep(dist, board, tileX, tileY)
        if step is None:
            return

        dx, dy = step
        targetTX, targetTY = tileX + dx, tileY + dy

        #CPU found, subject attacks and CPU takes damage
        if board.isCpu(targetTX, targetTY):
            events.emit("cpuHit", self, self.dps * dt)
            self._nudge(board, sepX, sepY, dt)
            return

        #tool found, subject attacks and tool takes damage
        tool = board.toolAt(targetTX, targetTY)
        if tool:
            tool.takeDamage(self.dps * dt)
            self._nudge(board, sepX, sepY, dt)
            return

        #finding center of tile
        targetX, targetY = targetTX + 0.5 + self.offsetX, targetTY + 0.5 + self.offsetY
        #calculating vector between source and target
        vx, vy = targetX - self.x, targetY - self.y
        #calculating distance of vector
        distance = math.hypot(vx, vy)
        if distance > 0:
            vx, vy = vx / distance, vy / distance

        dirX = vx + config.SEPARATION_WEIGHT * sepX
        dirY = vy + config.SEPARATION_WEIGHT * sepY
        distance = math.hypot(dirX, dirY)
        if distance == 0:
            return

        #finding maximum distance able to be moved on current frame
        move = self.speed * dt
        self._tryMove(board, self.x + dirX / distance * move, self.y + dirY / distance * move)


    def _nudge(self, board, sepX, sepY, dt):
        distance = math.hypot(sepX, sepY)
        if distance > 1:
            sepX, sepY = sepX / distance, sepY / distance
        push = self.speed * dt * 0.5
        self._tryMove(board, self.x + sepX * push,self.y + sepY * push)

    def _tryMove(self, board, newX, newY):
        if self._walkable(board, newX, self.y):
            self.x = newX
        if self._walkable(board, self.x, newY):
            self.y = newY

    @staticmethod
    def _walkable(board, fx, fy):
        tx, ty = math.floor(fx), math.floor(fy)
        return board.inBounds(tx, ty) and not board.isCpu(tx, ty) and board.toolAt(tx, ty) is None

        

