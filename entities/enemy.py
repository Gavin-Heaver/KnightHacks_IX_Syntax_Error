# entities/enemy.py -- Enemy base (+ Bug, MemoryLeak, ZeroDay, Injection by Tadhg).
# x, y are float TILE units (tile (i, j) center = (i + 0.5, j + 0.5)).
import config
from game import events


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


class FakeEnemy(Enemy):
    """Stub that stands still so turrets/scripts can be tested before real AI exists."""

    def __init__(self, x=0.5, y=0.5):
        super().__init__("bug", x, y)

