# entities/tools.py -- DefenseTool base (+ Turret, Debugger by Gavin; Firewall by Tadhg).
import config
from game import events


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

