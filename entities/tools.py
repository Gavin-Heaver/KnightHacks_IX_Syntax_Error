# entities/tools.py -- DefenseTool base (+ Turret, Debugger by Gavin; Firewall by Tadhg).
import config
from game import events

from scripting.runner import TowerScript
from scripting.defaults import DEFAULT_TURRET_SCRIPT
from entities.projectile import Projectile


class DefenseTool:
    kind = "tool"
    programmable = False

    def __init__(self, kind, x=0, y=0):
        stats = config.TOOL_STATS[kind]
        self.kind = kind
        self.x = x
        self.y = y
        self.hp = stats["hp"]
        self.maxHp = stats["hp"]
        self.range = stats["range"]
        self.dps = stats["dps"]
        self.spent = stats["cost"]       # total bytes spent (sell refund = 50%)

    def takeDamage(self, n):
        if self.hp <= 0:
            return
        self.hp -= n
        if self.hp <= 0:
            self.hp = 0
            events.emit("toolDestroyed", self)

    def corrupt(self):
        """Called by Injection on contact. Overridden by programmable tools."""
        pass


class FakeTool(DefenseTool):
    """Stub so the AI side can test pathing/costs before real tools exist."""

    def __init__(self, x=0, y=0, programmable=False):
        super().__init__("turret", x, y)
        self.programmable = programmable

class Turret(DefenseTool):
    """
    Programmable defense turret.
    Executes a Python script to scan for enemies, aim, and shoot projectiles.
    """
    programmable = True

    def __init__(self, x=0, y=0):
        super().__init__("turret", x, y)
        
        # 1. Tier setup
        self.tier = 0

        # 2. Load tier stats (damage, range, fireRate, cycleBudget)
        self.applyTierStats()

        # 3. Initialize script with default turret code
        self.script = TowerScript(DEFAULT_TURRET_SCRIPT)

        # 4. Aiming and weapon timers
        self.aimTarget = None
        self.wantsToFire = False
        self.fireCooldown = 0.0
        self.scriptTimer = 0.0

    def applyTierStats(self):
        """Loads stats (damage, range, fireRate, cycles) from config.TURRET_TIERS based on self.tier."""
        # --- PSEUDO-CODE ---
        tierData = config.TURRET_TIERS[self.tier]
        self.damage = tierData["damage"]
        self.range = tierData["range"]
        self.fireRate = tierData["fireRate"]
        self.cycleBudget = tierData["cycles"]

    def upgrade(self):
        """Upgrades the turret to the next tier if available."""
        # --- PSEUDO-CODE ---
        if self.tier < len(config.TURRET_TIERS) - 1:
            self.tier += 1
            cost = config.TURRET_TIERS[self.tier]["upgradeCost"]
            self.spent += cost
            self.applyTierStats()
            return True
        return False

    def update(self, dt, allEnemies, newProjectilesList, unlockedConcepts=None):
        """
        Runs every frame:
        1. Manages fire cooldown timer.
        2. Ticks the Python script ~8 times a second.
        3. Spawns projectiles when the script wants to fire and weapon is ready.
        """
        # --- PSEUDO-CODE ---
        #Decrement self.fireCooldown by dt:
        if self.fireCooldown > 0:
            self.fireCooldown -= dt
        
        #Update script timer:
        self.scriptTimer += dt
        tickInterval = 1.0 / config.SCRIPT_TICKS_PER_SECOND
        if self.scriptTimer >= tickInterval:
            self.scriptTimer = 0.0
            self.script.runTick(self, allEnemies, self.cycleBudget, unlockedConcepts)
        
        #Check if ready to fire:
        if self.wantsToFire and self.fireCooldown <= 0 and self.aimTarget:
            if getattr(self.aimTarget, "alive", True):
                # Spawn projectile from turret center (x+0.5, y+0.5) to aimTarget (x, y)
                bullet = Projectile(
                    startX=self.x + 0.5,
                    startY=self.y + 0.5,
                    targetX=self.aimTarget.x,
                    targetY=self.aimTarget.y,
                    damage=self.damage,
                    speed=config.PROJECTILE_SPEED,
                    maxRange=self.range
                )
                newProjectilesList.append(bullet)
                self.fireCooldown = 1.0 / self.fireRate
            self.wantsToFire = False
