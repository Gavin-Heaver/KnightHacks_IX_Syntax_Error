# game/corruption.py -- Injects malware code and corrupts programmable tools.
import random


CORRUPTION_INJECTIONS = [
    "# [INJECTION MALWARE] Remove this line to restore tower:\nmalware_payload = >>> SYNTAX_ERROR <<<\n\n",
    "# [INJECTION MALWARE] Remove this line to restore tower:\nwhile True # SyntaxError: missing colon\n\n",
    "# [INJECTION MALWARE] Remove this line to restore tower:\nimport malware_exploit  # Unauthorized import\n\n",
    "# [INJECTION MALWARE] Remove this line to restore tower:\n__trojan_rootkit__ = True  # Forbidden dunder variable\n\n",
    "# [INJECTION MALWARE] Remove this line to restore tower:\ndef broken_exploit(  # SyntaxError: unclosed parenthesis\n\n",
]



def corrupt(tool):
    """Corrupts tool, flips its allegiance, and injects failing code into its compiler."""
    if not getattr(tool, "programmable", False) or getattr(tool, "corrupted", False):
        return
    tool.corrupted = True
    snippet = random.choice(CORRUPTION_INJECTIONS)
    # Prepend malware payload to source code
    tool.script.sourceCode = snippet + tool.script.sourceCode
    tool.script.jammed = True
    tool.script.compiledCode = None
    tool.script.error = "SyntaxError: Injected malware detected. Remove or fix failing code and recompile!"