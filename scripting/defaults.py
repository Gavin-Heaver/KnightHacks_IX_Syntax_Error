# scripting/defaults.py -- working default scripts for programmable tools.

DEFAULT_TURRET_SCRIPT = """def tick():
    targets = enemiesInRange()
    if len(targets) > 0:
        aim(targets[0])
        fire()
"""

DEFAULT_DEBUGGER_SCRIPT = """def tick():
    targets = enemiesInRange()
    if len(targets) > 0:
        # Debugger reveals enemy types and slows them down
        aim(targets[0])
"""

