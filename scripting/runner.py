# scripting/runner.py -- TowerScript compilation, AST validation, and sandboxed execution with cycle budget.
import ast
import sys
from scripting.api import SAFE_BUILTINS, EnemyView, createEnemyView


class CyclesExceededError(RuntimeError):
    pass


class ScriptValidationError(Exception):
    pass


class ASTValidator(ast.NodeVisitor):
    def __init__(self, unlockedConcepts=None):
        self.unlocked = set(unlockedConcepts) if unlockedConcepts is not None else {"if"}

    def visit_Import(self, node):
        raise ScriptValidationError("Imports are forbidden in tower scripts.")

    def visit_ImportFrom(self, node):
        raise ScriptValidationError("Imports are forbidden in tower scripts.")

    def visit_Name(self, node):
        if node.id.startswith("__"):
            raise ScriptValidationError(f"Dunder name '{node.id}' is forbidden.")
        if node.id == "memory" and "memory" not in self.unlocked:
            raise ScriptValidationError("'memory' dictionary is not unlocked yet.")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr.startswith("__"):
            raise ScriptValidationError(f"Dunder attribute '{node.attr}' is forbidden.")
        self.generic_visit(node)

    def visit_If(self, node):
        if "if" not in self.unlocked:
            raise ScriptValidationError("If statements are not unlocked yet.")
        self.generic_visit(node)

    def visit_For(self, node):
        if "for" not in self.unlocked:
            raise ScriptValidationError("For loops are not unlocked yet.")
        self.generic_visit(node)

    def visit_While(self, node):
        if "while" not in self.unlocked:
            raise ScriptValidationError("While loops are not unlocked yet.")
        self.generic_visit(node)


class TowerScript:
    def __init__(self, sourceCode: str):
        self.sourceCode = sourceCode
        self.compiledCode = None
        self.memory = {}
        self.console = []        # list of recent print log strings
        self.jammed = False
        self.error = None
        self.outOfCycles = False

    def compile(self, unlockedConcepts=None):
        """Validates AST and compiles the code into bytecode."""
        try:
            tree = ast.parse(self.sourceCode, filename="<tower_script>")
            validator = ASTValidator(unlockedConcepts=unlockedConcepts)
            validator.visit(tree)
            self.compiledCode = compile(tree, filename="<tower_script>", mode="exec")
            self.error = None
            return True
        except Exception as e:
            self.compiledCode = None
            self.error = str(e)
            self.jammed = True
            return False

    def runTick(self, tool, allEnemies, cycleBudget=20, unlockedConcepts=None):
        """
        Executes tick() within the tool script.
        - tool: instance of DefenseTool (Turret, Debugger, etc.)
        - allEnemies: list of active Enemy instances in the game
        - cycleBudget: max 'line' events allowed before CyclesExceededError
        """
        if self.compiledCode is None:
            if not self.compile(unlockedConcepts=unlockedConcepts):
                return False

        # Build execution environment
        toolX, toolY = tool.x, tool.y
        toolRange = getattr(tool, "range", 5.0)

        # Build list of enemies in range with 1-to-1 matching to original enemy objects
        inRangePairs = []
        for enemy in allEnemies:
            if not getattr(enemy, "alive", True):
                continue
            view = createEnemyView(enemy, toolX, toolY)
            if view.distance <= toolRange:
                inRangePairs.append((view, enemy))

        # Closest first
        inRangePairs.sort(key=lambda pair: pair[0].distance)
        targetViews = [pair[0] for pair in inRangePairs]
        viewToEnemy = {id(pair[0]): pair[1] for pair in inRangePairs}

        # API callbacks exposed to player script
        def enemiesInRange():
            return list(targetViews)

        def aim(targetView):
            if isinstance(targetView, EnemyView):
                realEnemy = viewToEnemy.get(id(targetView))
                if realEnemy is not None:
                    tool.aimTarget = realEnemy
            elif targetView is None:
                tool.aimTarget = None

        def fire():
            tool.wantsToFire = True

        def customPrint(*args):
            msg = " ".join(str(a) for a in args)
            self.console.append(msg)
            if len(self.console) > 50:
                self.console.pop(0)

        sandboxGlobals = {
            "__builtins__": dict(SAFE_BUILTINS),
            "enemiesInRange": enemiesInRange,
            "aim": aim,
            "fire": fire,
            "memory": self.memory,
            "print": customPrint,
        }

        # Execute module script to define functions (e.g. tick)
        execLocals = {}
        try:
            exec(self.compiledCode, sandboxGlobals, execLocals)
        except Exception as e:
            self.jammed = True
            self.error = f"Setup error: {e}"
            return False

        tickFunc = execLocals.get("tick") or sandboxGlobals.get("tick")
        if not callable(tickFunc):
            self.jammed = True
            self.error = "Function 'tick()' not defined"
            return False

        # Set up cycle tracer
        lineCount = 0

        def tracer(frame, event, arg):
            nonlocal lineCount
            if event == "line":
                lineCount += 1
                if lineCount > cycleBudget:
                    raise CyclesExceededError("OUT OF CYCLES")
            return tracer

        oldTrace = sys.gettrace()
        sys.settrace(tracer)
        try:
            tickFunc()
            self.jammed = False
            self.error = None
            self.outOfCycles = False
            return True
        except CyclesExceededError:
            self.jammed = True
            self.outOfCycles = True
            self.error = "OUT OF CYCLES"
            self.console.append("[WARN] Out of cycles budget!")
            return False
        except Exception as e:
            self.jammed = True
            self.outOfCycles = False
            self.error = f"Runtime: {e}"
            self.console.append(f"[ERR] {e}")
            return False
        finally:
            sys.settrace(oldTrace)


# For backwards compatibility with main.py initial stub import
def towerScript():
    pass