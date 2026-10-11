# entities/projectile.py -- Linear projectile physics and collision.
import math
import config
from game.audio import audioManager


class Projectile:
    def __init__(self, startX, startY, targetX, targetY, damage, speed=config.PROJECTILE_SPEED, maxRange=6.0, homingTarget=None, targetTool=None, sourceTool=None):
        self.x = float(startX)
        self.y = float(startY)
        self.damage = float(damage)
        self.speed = float(speed)
        self.maxRange = float(maxRange)
        self.distTraveled = 0.0
        self.alive = True
        self.hitRadius = 0.1    # tile distance to register a hit
        self.homingTarget = homingTarget
        self.targetTool = targetTool
        self.sourceTool = sourceTool

        # Calculate normalized straight-line velocity vector
        dx = targetX - startX
        dy = targetY - startY
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = self.speed
            self.vy = 0.0

    def update(self, dt, allEnemies, board=None):
        """Advances projectile in a straight line or homing toward target and checks collisions."""
        if not self.alive:
            return

        # Homing velocity adjustment toward locked bug or tool
        if self.homingTarget is not None:
            isTargetAlive = getattr(self.homingTarget, "alive", True) if hasattr(self.homingTarget, "alive") else (getattr(self.homingTarget, "hp", 1) > 0)
            if isTargetAlive:
                targetX = (self.homingTarget.x + 0.5) if hasattr(self.homingTarget, "kind") else self.homingTarget.x
                targetY = (self.homingTarget.y + 0.5) if hasattr(self.homingTarget, "kind") else self.homingTarget.y
                dx = targetX - self.x
                dy = targetY - self.y
                dist = math.hypot(dx, dy)
                if dist > 0.01:
                    self.vx = (dx / dist) * self.speed
                    self.vy = (dy / dist) * self.speed

        stepX = self.vx * dt
        stepY = self.vy * dt
        stepDist = math.hypot(stepX, stepY)

        self.x += stepX
        self.y += stepY
        self.distTraveled += stepDist

        # Check max range limit or board boundaries
        if self.distTraveled >= self.maxRange:
            self.alive = False
            return

        if board and not board.inBounds(int(self.x), int(self.y)):
            self.alive = False
            return

        if board and board.isCpu(math.floor(self.x), math.floor(self.y)):
            self.alive = False
            return

        # Check collision against good friendly tools if projectile was fired by corrupted tool
        if self.targetTool is not None:
            if board:
                for tool in board.allTools():
                    if tool == self.sourceTool:
                        continue
                    if getattr(tool, "corrupted", False):
                        continue
                    if getattr(tool, "hp", 0) <= 0:
                        continue
                    d = math.hypot(self.x - (tool.x + 0.5), self.y - (tool.y + 0.5))
                    if d <= 0.45:
                        tool.takeDamage(self.damage)
                        audioManager.sfx("hit")
                        board.hpChanged = True
                        self.alive = False
                        break
            return


        # Check collision against enemies
        for enemy in allEnemies:
            if not getattr(enemy, "alive", True):
                continue
            # Distance from bullet (x, y) to enemy center
            d = math.hypot(self.x - enemy.x, self.y - enemy.y)
            if d <= self.hitRadius + enemy.size:
                enemy.takeDamage(self.damage)
                if enemy.alive:
                    audioManager.sfx("hit")   # killing blows get the bugKill sound instead
                self.alive = False
                break
