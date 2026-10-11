import config
from game import events

class GameState:

    #initalize variables/attributes
    def __init__(self):
        self.bytes = config.START_BYTES
        self.cpuHp = float(config.CPU_MAX_HP)
        self.cpuMaxHp = float(config.CPU_MAX_HP)
        self.wave = 1
        self.phase = config.PHASE_BUILD
        self.unlockedConcepts = {"if", "for", "while", "memory"}
        self.bugsKilled = 0
        self.totalBytesEarned = config.START_BYTES
        self.encounteredEnemies = {"bug"}

        events.subscribe("enemyKilled", self.onEnemyKilled)
        events.subscribe("cpuHit", self.onCpuHit)

    #check if the player can afford purchase
    def canAfford(self, amount):
        if self.bytes >= amount:
            return True

        else:
            return False

    #spend the players bytes
    def spendBytes(self, amount):
        if self.canAfford(amount):
            self.bytes -= amount
            return True

        else:
            return False

    #add bytes
    def addBytes(self, amount):
        self.bytes += amount
        self.totalBytesEarned += amount

    #refund bytes, but only a percentage of it
    def refundBytes(self, originalCost):
        refund = int(originalCost * config.SELL_REFUND)
        self.bytes += refund
        return refund

    #reward player for killed enemy
    def onEnemyKilled(self, enemy):
        reward = getattr(enemy, "reward", 5)
        self.addBytes(reward)
        self.bugsKilled += 1

    #hurt CPU on damage
    def onCpuHit(self, enemy, damage = 5.0):
        self.cpuHp -= damage
        if (self.cpuHp <= 0):
            self.cpuHp = 0
            self.phase = config.PHASE_GAME_OVER

    def unlockConcept(self, concept):
        cost = config.CODE_UNLOCK_COSTS.get(concept, 0)

        if concept not in self.unlockedConcepts and self.spendBytes(cost):
            self.unlockedConcepts.add(concept)
            return True

        return False

    def upgradeCpuMaxHp(self, amount=25, cost=50):
        """Expands CPU max HP and heals by the amount increased."""
        if self.spendBytes(cost):
            self.cpuMaxHp += amount
            self.cpuHp = min(self.cpuMaxHp, self.cpuHp + amount)
            return True
        return False

    def regenerateCpuBetweenWaves(self, percent=0.25):
        """Restores a percentage of missing CPU health between waves."""
        missing = self.cpuMaxHp - self.cpuHp
        if missing > 0:
            restored = missing * percent
            self.cpuHp = min(self.cpuMaxHp, self.cpuHp + restored)
            return restored
        return 0.0