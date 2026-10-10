# ui/gameOver.py -- Thematic terminal crash dump with interactive hacker handle input.
import pygame
import config
import random


class GameOverTerminal:
    FORTUNES = [
        "YOU ARE ADMIRED FOR YOUR ADVENTUROUS SPIRIT",
        "YOU WILL BE REWARDED FOR YOUR PATIENCE AND UNDERSTANDING",
        "DO YOU KNOW HOW TO DAP UP BRO?",
    ]
    def __init__(self, screenW, screenH):
        self.screenW = screenW
        self.screenH = screenH
        # Panel geometry
        self.panelW = 760
        self.panelH = 540
        self.panelX = (self.screenW - self.panelW) // 2
        self.panelY = (self.screenH - self.panelH) // 2
        # Fonts
        self.titleFont = pygame.font.SysFont("consolas", 15, bold=True)
        self.codeFont = pygame.font.SysFont("consolas", 16)
        self.codeBold = pygame.font.SysFont("consolas", 16, bold=True)
        self.promptFont = pygame.font.SysFont("consolas", 18, bold=True)
        self.hintFont = pygame.font.SysFont("consolas", 14)
        # State
        self.wave = 1
        self.bytesEarned = 0
        self.kills = 0
        self.playerName = ""
        self.cursorTimer = 0.0
        self.showCursor = True
        self.fortune = ""

    def open(self, wave, bytesEarned, kills):
        self.wave = wave
        self.bytesEarned = bytesEarned
        self.kills = kills
        self.playerName = ""
        self.cursorTimer = 0.0
        self.showCursor = True
        self.fortune = random.choice(self.FORTUNES)

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                finalName = self.playerName.strip() or "Hacker"
                self.playerName = finalName
                return "submitted"

            elif event.key == pygame.K_ESCAPE:
                return "quit"

            elif event.key == pygame.K_BACKSPACE:
                self.playerName = self.playerName[:-1]

            else:
                # Accept letters, numbers, spaces, underscores, hyphens up to 14 chars
                if len(self.playerName) < 14 and event.unicode.isprintable():
                    self.playerName += event.unicode

        return None

    def fortune(self):
        fortune_choice = random.choice(GameOverTerminal.fortunes)

        return None

    def draw(self, screen, dt=0.016):
        # Update cursor blink
        self.cursorTimer += dt
        if self.cursorTimer >= 0.4:
            self.cursorTimer = 0.0
            self.showCursor = not self.showCursor

        # Dim background
        dim = pygame.Surface((self.screenW, self.screenH), pygame.SRCALPHA)
        dim.fill((10, 12, 18, 210))
        screen.blit(dim, (0, 0))

        px, py = self.panelX, self.panelY
        pw, ph = self.panelW, self.panelH

        # Terminal outer window
        pygame.draw.rect(screen, (12, 16, 22), (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(screen, (220, 60, 60), (px, py, pw, ph), 2, border_radius=8)

        # Title bar
        titleH = 32
        pygame.draw.rect(screen, (22, 28, 38), (px, py, pw, titleH), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, (45, 55, 75), (px, py + titleH), (px + pw, py + titleH), 1)

        # macOS/Unix window buttons
        pygame.draw.circle(screen, (255, 95, 86), (px + 18, py + 16), 6)   # red
        pygame.draw.circle(screen, (255, 189, 46), (px + 36, py + 16), 6)  # yellow
        pygame.draw.circle(screen, (39, 201, 63), (px + 54, py + 16), 6)   # green

        # Title bar text
        titleText = self.titleFont.render("crash_dump.log - [FATAL CORE EXCEPTION] - zsh", True, (160, 180, 205))
        screen.blit(titleText, (px + 72, py + 8))

        # Terminal content lines
        lines = [
            ("[CRITICAL] CPU INTEGRITY 0% -- MEMORY CORRUPTION IN CORE", (255, 85, 85), True),
            ("Traceback (most recent call last):", (140, 160, 185), False),
            ("  File \"kernel/cpu.py\", line 404, in execute_cycle", (160, 180, 205), False),
            ("    raise SystemCrashError(\"Firewall breached; malicious packets flood CPU\")", (220, 140, 140), False),
            ("SystemCrashError: Core overflowed by malicious payload.", (255, 100, 100), True),
            (f"Fortune Cookie: {self.fortune}", (255, 100, 100), False),
            ("", (0, 0, 0), False),
            ("====================== RUNTIME DIAGNOSTICS ======================", (70, 140, 210), True),
            (f"  [+] Final Wave Survived : Wave {self.wave}", (100, 220, 140), False),
            (f"  [+] Bugs Eliminated     : {self.kills}", (240, 200, 80), False),
            (f"  [+] Total Bytes Mined   : {self.bytesEarned} B", (100, 200, 255), False),
            ("  [+] Kernel Diagnostic   : EXECUTION HALTED (DUMP RECORDED)", (255, 120, 120), False),
            ("=================================================================", (70, 140, 210), True),
        ]

        textY = py + titleH + 16
        for text, color, isBold in lines:
            if text:
                font = self.codeBold if isBold else self.codeFont
                surf = font.render(text, True, color)
                screen.blit(surf, (px + 24, textY))
            textY += 22

        # Prompt input section
        promptBoxY = textY + 10
        promptText = self.promptFont.render("root@defense-net:~# enter_handle --save", True, (80, 230, 130))
        screen.blit(promptText, (px + 24, promptBoxY))

        # Input box
        inputRect = pygame.Rect(px + 24, promptBoxY + 30, pw - 48, 40)
        pygame.draw.rect(screen, (18, 24, 34), inputRect, border_radius=4)
        pygame.draw.rect(screen, (70, 200, 120), inputRect, 1, border_radius=4)

        # Render typed name with cursor
        cursorChar = "_" if self.showCursor else " "
        displayStr = f"> {self.playerName}{cursorChar}"
        nameSurf = self.promptFont.render(displayStr, True, (240, 255, 240))
        screen.blit(nameSurf, (inputRect.x + 12, inputRect.y + 10))

        # Bottom instruction hint
        hintSurf = self.hintFont.render(
            "[ENTER] Save Score to Local Scoreboard    |    [ESC] Exit to Menu",
            True,
            (120, 150, 180)
        )
        screen.blit(hintSurf, (px + 24, py + ph - 28))

