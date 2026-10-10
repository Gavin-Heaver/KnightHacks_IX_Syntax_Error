# entities/enemy.py -- Enemy base (+ Bug, MemoryLeak, ZeroDay, Injection by Tadhg).
# x, y are float TILE units (tile (i, j) center = (i + 0.5, j + 0.5)).
import config
import math
import random
from game import events
from ai.flowField import nextStep
from ai.steering import separation, clearPath


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
        angle = random.uniform(0, 2 * math.pi)
        cpuCenterX = config.CPU_X + config.CPU_W / 2
        cpuCenterY = config.CPU_Y + config.CPU_H / 2
        ringRadius = max(config.CPU_W, config.CPU_H) / 2 + 0.6   # just outside the CPU
        self.spotX = cpuCenterX + math.cos(angle) * ringRadius
        self.spotY = cpuCenterY + math.sin(angle) * ringRadius

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

        spotFree = board.toolAt(math.floor(self.spotX), math.floor(self.spotY)) is None
        approaching = dist[tileY][tileX] <= config.APPROACH_RANGE and spotFree and clearPath(board, self.x, self.y, self.spotX, self.spotY)

        if approaching:
            sepX, sepY = separation(self, enemies, config.SWARM_SEP_RADIUS)
            sepWeight = config.SWARM_SEP_WEIGHT
        else:
            sepX, sepY = separation(self, enemies, config.SEPARATION_RADIUS)
            sepWeight = config.SEPARATION_WEIGHT

        if approaching:
            if math.hypot(self.spotX - self.x, self.spotY - self.y) <= config.ATTACK_RANGE:
                events.emit("cpuHit", self, self.dps * dt)
                self._nudge(board, sepX, sepY, dt)
            else:
                self._steerToward(board, self.spotX, self.spotY, sepX, sepY, sepWeight, dt)
            return

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


        self._steerToward(board, targetX, targetY, sepX, sepY, sepWeight, dt)


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

    def _steerToward(self, board, targetX, targetY, sepX, sepY, sepWeight,dt):
        """Walk toward (targetX, targetY), blended with separation."""
        vx, vy = targetX - self.x, targetY - self.y
        distance = math.hypot(vx, vy)
        if distance > 0:
            vx, vy = vx / distance, vy / distance
        dirX = vx + sepWeight * sepX
        dirY = vy + sepWeight * sepY
        length = math.hypot(dirX, dirY)
        if length == 0:
            return
        move = self.speed * dt
        self._tryMove(board, self.x + dirX / length * move, self.y + dirY / length * move)

    @staticmethod
    def _walkable(board, fx, fy):
        tx, ty = math.floor(fx), math.floor(fy)
        return board.inBounds(tx, ty) and not board.isCpu(tx, ty) and board.toolAt(tx, ty) is None

        

