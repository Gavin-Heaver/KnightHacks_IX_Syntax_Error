# scripting/defaults.py -- working default scripts for programmable tools.
 
DEFAULT_DEBUGGER_SCRIPT = """def tick():
    targets = enemiesInRange()
    if len(targets) > 0:
        aim(targets[0])
        fire()
"""

DEFAULT_ANTIVIRUS_SCRIPT = """def tick():
    targets = enemiesInRange()
    if len(targets) > 0:
        # Antivirus reveals enemy types and slows them down
        aim(targets[0])
        slow()
"""

DEFAULT_TURRET_SCRIPT = DEFAULT_DEBUGGER_SCRIPT  # alias


