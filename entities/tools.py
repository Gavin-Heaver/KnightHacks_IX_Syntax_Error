# entities/tools.py -- DefenseTool base (+ Turret, Debugger by Gavin; Firewall by Tadhg).
import config
import math
from game import events
from game.audio import audioManager

from scripting.runner import TowerScript
from scripting.defaults import DEFAULT_DEBUGGER_SCRIPT, DEFAULT_ANTIVIRUS_SCRIPT, DEFAULT_TURRET_SCRIPT
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
        self.corrupted = False

    def takeDamage(self, n):
        if self.hp <= 0:
            return
        self.hp -= n
        if self.hp <= 0:
            self.hp = 0
            audioManager.sfx("toolBreak")
            events.emit("toolDestroyed", self)

    def corrupt(self):
        pass


class FakeTool(DefenseTool):
    """Stub so the AI side can test pathing/costs before real tools exist."""

    def __init__(self, x=0, y=0, programmable=False):
        super().__init__("debugger", x, y)
        self.programmable = programmable

class Debugger(DefenseTool):
    """
    Programmable defense attacker (formerly Turret).
    Executes a Python script to scan for enemies, aim, and shoot projectiles / lasers.
    """
    programmable = True

    def __init__(self, x=0, y=0):
        super().__init__("debugger", x, y)
        
        # 1. Tier setup
        self.tier = 0

        # 2. Load tier stats (damage, range, fireRate, cycleBudget)
        self.applyTierStats()

        # 3. Initialize script with default attack code
        self.script = TowerScript(DEFAULT_DEBUGGER_SCRIPT)

        # 4. Aiming, laser, and weapon timers
        self.aimTarget = None
        self.wantsToFire = False
        self.fireCooldown = 0.0
        self.scriptTimer = 0.0
        self.laserTarget = None
        self.laserDuration = 0.0

    def applyTierStats(self):
        """Loads stats (damage, range, fireRate, cycles, weapon) from config.DEBUGGER_TIERS based on self.tier."""
        tierData = config.DEBUGGER_TIERS[self.tier]
        self.damage = tierData["damage"]
        self.range = tierData["range"]
        self.fireRate = tierData["fireRate"]
        self.cycleBudget = tierData["cycles"]
        self.weapon = tierData.get("weapon", "bullet")

    def upgrade(self):
        """Upgrades the debugger to the next tier if available."""
        if self.tier < len(config.DEBUGGER_TIERS) - 1:
            self.tier += 1
            cost = config.DEBUGGER_TIERS[self.tier]["upgradeCost"]
            self.spent += cost
            self.applyTierStats()
            self.hp = float(self.maxHp)
            return True
        return False

    def update(self, dt, allEnemies, newProjectilesList, unlockedConcepts=None, board=None):

        """
        Runs every frame:
        1. Manages fire cooldown and laser timers.
        2. Ticks the Python script ~8 times a second (or executes corrupted attacks if hacked).
        3. Spawns bullets (Tier 1/2) or fires continuous laser (Tier 3).
        """
        if self.fireCooldown > 0:
            self.fireCooldown -= dt

        if self.laserDuration > 0:
            self.laserDuration -= dt
            if self.laserDuration <= 0:
                self.laserTarget = None

        if getattr(self, "corrupted", False):
            # Corrupted turret attacks good friendly tools at half strength within range
            if board is not None:
                cx, cy = self.x + 0.5, self.y + 0.5
                candidateTools = [
                    t for t in board.allTools()
                    if t != self and getattr(t, "hp", 0) > 0 and not getattr(t, "corrupted", False) and math.hypot((t.x + 0.5) - cx, (t.y + 0.5) - cy) <= self.range
                ]
                candidateTools.sort(key=lambda t: math.hypot((t.x + 0.5) - cx, (t.y + 0.5) - cy))

                if self.tier == 2:
                    # Tier 3 (Laser): Constant laser beam dealing continuous half damage to friendly tool
                    if candidateTools:
                        targetTool = candidateTools[0]
                        if self.laserTarget is not targetTool:
                            audioManager.sfx("laser")   # beam locks onto a new target
                        laserDps = (self.damage * 0.5) * self.fireRate
                        targetTool.takeDamage(laserDps * dt)
                        board.hpChanged = True
                        self.laserTarget = targetTool
                        self.laserDuration = 0.1
                    else:
                        self.laserTarget = None
                else:
                    # Tier 1 & Tier 2: Projectiles (Tier 2 has homing) fired at friendly tools at half damage
                    if self.fireCooldown <= 0 and candidateTools:
                        targetTool = candidateTools[0]
                        homing = targetTool if self.tier == 1 else None
                        bullet = Projectile(
                            startX=cx,
                            startY=cy,
                            targetX=targetTool.x + 0.5,
                            targetY=targetTool.y + 0.5,
                            damage=self.damage * 0.5,
                            speed=config.PROJECTILE_SPEED,
                            maxRange=self.range,
                            homingTarget=homing,
                            targetTool=targetTool,
                            sourceTool=self
                        )
                        newProjectilesList.append(bullet)
                        audioManager.sfx("laser")
                        self.fireCooldown = 1.0 / self.fireRate
            return


        # Update script timer:
        self.scriptTimer += dt
        tickInterval = 1.0 / config.SCRIPT_TICKS_PER_SECOND
        if self.scriptTimer >= tickInterval:
            self.scriptTimer = 0.0
            self.script.runTick(self, allEnemies, self.cycleBudget, unlockedConcepts)

        # Weapon firing logic
        if self.tier == 2:
            # Tier 3 (Laser): Constant laser beam dealing continuous damage
            if self.wantsToFire and self.aimTarget and getattr(self.aimTarget, "alive", True):
                cx, cy = self.x + 0.5, self.y + 0.5
                dist = math.hypot(self.aimTarget.x - cx, self.aimTarget.y - cy)
                if dist <= self.range:
                    if self.laserTarget is not self.aimTarget:
                        audioManager.sfx("laser")   # beam locks onto a new target
                    laserDps = self.damage * self.fireRate
                    self.aimTarget.takeDamage(laserDps * dt)
                    self.laserTarget = self.aimTarget
                    self.laserDuration = 0.1
                else:
                    self.laserTarget = None
            else:
                self.laserTarget = None
            self.wantsToFire = False

        else:
            # Tier 1 & Tier 2: Projectiles (Tier 2 has homing)
            if self.wantsToFire and self.fireCooldown <= 0 and self.aimTarget:
                if getattr(self.aimTarget, "alive", True):
                    homing = self.aimTarget if self.tier == 1 else None
                    bullet = Projectile(
                        startX=self.x + 0.5,
                        startY=self.y + 0.5,
                        targetX=self.aimTarget.x,
                        targetY=self.aimTarget.y,
                        damage=self.damage,
                        speed=config.PROJECTILE_SPEED,
                        maxRange=self.range,
                        homingTarget=homing
                    )
                    newProjectilesList.append(bullet)
                    audioManager.sfx("laser")
                    self.fireCooldown = 1.0 / self.fireRate
                self.wantsToFire = False


Turret = Debugger  # alias for backwards compatibility


class Firewall(DefenseTool):

    """Heavy defensive wall that connects plasma barriers."""
    programmable = False

    def __init__(self, x=0, y=0):
        super().__init__("firewall", x, y)
        self.tier = 0
        self.applyTierStats()

    def applyTierStats(self):
        tierData = config.FIREWALL_TIERS[self.tier]
        self.maxLen = tierData["maxLen"]
        self.isDamaging = tierData.get("isDamaging", False)
        self.dps = tierData.get("dps", 0.0)

    def upgrade(self):
        if self.tier < len(config.FIREWALL_TIERS) - 1:
            self.tier += 1
            cost = config.FIREWALL_TIERS[self.tier]["upgradeCost"]
            self.spent += cost
            self.applyTierStats()
            self.hp = float(self.maxHp)
            return True
        return False

    def update(self, dt, allEnemies, newProjectilesList, unlockedConcepts=None, board=None):
        pass

class Antivirus(DefenseTool):
    """
    Programmable support tower (formerly Debugger).
    Reveals hidden enemy types, emits a passive damage aura, and slows bugs.
    """
    programmable = True

    def __init__(self, x=0, y=0):
        super().__init__("antivirus", x, y)
        self.tier = 0
        self.applyTierStats()
        self.script = TowerScript(DEFAULT_ANTIVIRUS_SCRIPT)
        self.scriptTimer = 0.0
        self.aimTarget = None
        self.wantsToSlow = False
        self.scanAngle = 0.0

    def applyTierStats(self):
        """Loads stats (range, slowFactor, passiveSlow, dps, cycles) from config.ANTIVIRUS_TIERS based on self.tier."""
        tierData = config.ANTIVIRUS_TIERS[self.tier]
        self.range = tierData["range"]
        self.slowFactor = tierData["slowFactor"]
        self.passiveSlow = tierData.get("passiveSlow", 1.0)
        self.dps = tierData.get("dps", 4.0)
        self.cycleBudget = tierData["cycles"]

    def upgrade(self):
        """Upgrades the antivirus to the next tier if available."""
        if self.tier < len(config.ANTIVIRUS_TIERS) - 1:
            self.tier += 1
            cost = config.ANTIVIRUS_TIERS[self.tier]["upgradeCost"]
            self.spent += cost
            self.applyTierStats()
            self.hp = float(self.maxHp)
            return True
        return False


    def update(self, dt, allEnemies, newProjectilesList, unlockedConcepts=None, board=None):
        # 1. Update radar sweep angle
        self.scanAngle = (self.scanAngle + 3.0 * dt) % (2 * math.pi)

        cx, cy = self.x + 0.5, self.y + 0.5

        if getattr(self, "corrupted", False):
            # Corrupted Debugger:
            # - Does NO damage to bugs.
            # - Deals small damage (20% of tier dps) to friendly tools in range.
            # - Reverses slowdown on bugs inside its sphere (speeds them up at the same rate).
            if board is not None and self.dps > 0:
                corruptedDps = self.dps * 0.20
                for t in board.allTools():
                    if t != self and getattr(t, "hp", 0) > 0 and not getattr(t, "corrupted", False):
                        if math.hypot((t.x + 0.5) - cx, (t.y + 0.5) - cy) <= self.range:
                            t.takeDamage(corruptedDps * dt)
                            board.hpChanged = True

            revPassive = (1.0 + (1.0 - self.passiveSlow)) if self.passiveSlow < 1.0 else 1.0
            revTarget = (1.0 + (1.0 - self.slowFactor)) if self.slowFactor < 1.0 else 1.0

            closestEnemy = None
            closestDist = 999.0

            for enemy in allEnemies:
                if getattr(enemy, "alive", True):
                    dist = math.hypot(enemy.x - cx, enemy.y - cy)
                    if dist <= self.range:
                        enemy.revealed = True
                        if revPassive > 1.0:
                            enemy.applySlow(factor=revPassive, duration=0.2)
                        if dist < closestDist:
                            closestDist = dist
                            closestEnemy = enemy

            if closestEnemy is not None:
                self.aimTarget = closestEnemy
                if revTarget > 1.0:
                    self.aimTarget.applySlow(factor=revTarget, duration=0.35)
            else:
                self.aimTarget = None
            self.wantsToSlow = False
            return

        # 2. Run Python script ~8x/sec
        self.scriptTimer += dt
        tickInterval = 1.0 / config.SCRIPT_TICKS_PER_SECOND
        if self.scriptTimer >= tickInterval:
            self.scriptTimer = 0.0
            self.script.runTick(self, allEnemies, self.cycleBudget, unlockedConcepts)

        # 3. Support Aura: reveal all enemies within scanner range, deal passive damage, and slow (if unlocked)
        for enemy in allEnemies:
            if getattr(enemy, "alive", True):
                dist = math.hypot(enemy.x - cx, enemy.y - cy)
                if dist <= self.range:
                    enemy.revealed = True
                    # Passive sphere damage over time
                    if self.dps > 0:
                        enemy.takeDamage(self.dps * dt)
                    # Base passive slow inside the sphere (only if unlocked by tier >= 1)
                    if self.passiveSlow < 1.0:
                        enemy.applySlow(factor=self.passiveSlow, duration=0.2)

        # 4. Focused tether slow (only if unlocked by tier >= 1)
        if self.aimTarget is not None and getattr(self.aimTarget, "alive", True):
            dist = math.hypot(self.aimTarget.x - cx, self.aimTarget.y - cy)
            if dist <= self.range:
                if self.slowFactor < 1.0:
                    self.aimTarget.applySlow(factor=self.slowFactor, duration=0.35)
            else:
                self.aimTarget = None
        self.wantsToSlow = False