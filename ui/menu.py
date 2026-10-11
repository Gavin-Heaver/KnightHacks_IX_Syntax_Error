# ui/menu.py -- Title screen, Scoreboard, and Guide overlays.
import os
import json
import pygame
import config


SCOREBOARD_FILE = "scoreboard.json"


def getScoreboard():
    """Load local scoreboard records, creating defaults if not found."""
    if os.path.exists(SCOREBOARD_FILE):
        try:
            with open(SCOREBOARD_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass

    defaultScores = [
        {"name": "RootAdmin", "wave": 10, "bytes": 1420, "kills": 95},
        {"name": "KernelHacker", "wave": 7, "bytes": 850, "kills": 54},
        {"name": "ScriptKiddie", "wave": 4, "bytes": 410, "kills": 28},
        {"name": "NullPointer", "wave": 2, "bytes": 180, "kills": 12},
    ]
    saveScoreboard(defaultScores)
    return defaultScores


def saveScoreboard(scores):
    try:
        with open(SCOREBOARD_FILE, "w") as f:
            json.dump(scores, f, indent=2)
    except Exception as e:
        print("Failed to save scoreboard:", e)


def recordNewScore(name, wave, bytesEarned, kills):
    scores = getScoreboard()
    scores.append({"name": name, "wave": wave, "bytes": bytesEarned, "kills": kills})
    scores.sort(key=lambda s: (s.get("wave", 0), s.get("bytes", 0)), reverse=True)
    scores = scores[:10]
    saveScoreboard(scores)


class MenuButton:
    def __init__(self, rect, text, actionKey):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.actionKey = actionKey
        self.isHovered = False

    def checkHover(self, mousePos):
        self.isHovered = self.rect.collidepoint(mousePos)
        return self.isHovered

    def draw(self, screen, font):
        bg = (24, 38, 54) if not self.isHovered else (45, 75, 110)
        border = (70, 200, 120) if self.isHovered else (50, 100, 160)
        textCol = (240, 255, 245) if self.isHovered else (200, 220, 240)

        pygame.draw.rect(screen, bg, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=6)

        txtSurf = font.render(self.text, True, textCol)
        txtRect = txtSurf.get_rect(center=self.rect.center)
        screen.blit(txtSurf, txtRect)


class StartMenu:
    def __init__(self, screenW=config.SCREEN_W, screenH=config.SCREEN_H):
        self.screenW = screenW
        self.screenH = screenH
        self.state = "main"    # "main", "scoreboard", "guide"

        # Fonts
        self.titleFont = pygame.font.SysFont("consolas", 68, bold=True)
        self.subFont = pygame.font.SysFont("consolas", 24, bold=True)
        self.btnFont = pygame.font.SysFont("consolas", 26, bold=True)
        self.bodyFont = pygame.font.SysFont("consolas", 18)
        self.headerFont = pygame.font.SysFont("consolas", 22, bold=True)

        # Load and scale game logo (scaled up to 150x150)
        self.logo = None
        logoPath = os.path.join("assets", "pixil-frame-0-trans.png")
        if not os.path.exists(logoPath):
            logoPath = os.path.join("assets", "pixil-frame-0.png")
        if os.path.exists(logoPath):
            try:
                rawLogo = pygame.image.load(logoPath).convert_alpha()
                self.logo = pygame.transform.smoothscale(rawLogo, (150, 150))
            except Exception as e:
                print("Failed to load logo:", e)

        # Scaled Up Buttons
        btnW, btnH = 380, 54
        startX = (screenW - btnW) // 2
        startY = 296
        gap = 68

        self.mainButtons = [
            MenuButton((startX, startY, btnW, btnH), "PLAY GAME", "play"),
            MenuButton((startX, startY + gap, btnW, btnH), "SCOREBOARD", "scoreboard"),
            MenuButton((startX, startY + gap * 2, btnW, btnH), "GUIDE & MANUAL", "guide"),
            MenuButton((startX, startY + gap * 3, btnW, btnH), "QUIT GAME", "quit"),
        ]

        # Modal Back Button
        self.backBtn = MenuButton((startX, screenH - 110, btnW, 46), "BACK TO MENU", "back")

    def handleEvent(self, event):
        """Processes events. Returns action string: 'play', 'quit', or None."""
        if event.type == pygame.MOUSEMOTION:
            mpos = event.pos
            if self.state == "main":
                for b in self.mainButtons:
                    b.checkHover(mpos)
            else:
                self.backBtn.checkHover(mpos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mpos = event.pos
            if self.state == "main":
                for b in self.mainButtons:
                    if b.rect.collidepoint(mpos):
                        if b.actionKey == "play":
                            return "play"
                        elif b.actionKey == "quit":
                            return "quit"
                        elif b.actionKey in ("scoreboard", "guide"):
                            self.state = b.actionKey
                            return None
            else:
                if self.backBtn.rect.collidepoint(mpos):
                    self.state = "main"
                    return None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state != "main":
                    self.state = "main"
                    return None
                else:
                    return "quit"

        return None

    def draw(self, screen):
        # Background cyber circuit styling
        screen.fill(config.COLOR_BG)
        self._drawDecorations(screen)

        if self.state == "main":
            self._drawMainView(screen)
        elif self.state == "scoreboard":
            self._drawScoreboardView(screen)
        elif self.state == "guide":
            self._drawGuideView(screen)

    def _drawDecorations(self, screen):
        # Subtle circuit grid lines
        gridCol = (20, 28, 38)
        step = 40
        for x in range(0, self.screenW, step):
            pygame.draw.line(screen, gridCol, (x, 0), (x, self.screenH), 1)
        for y in range(0, self.screenH, step):
            pygame.draw.line(screen, gridCol, (0, y), (self.screenW, y), 1)

    def _drawMainView(self, screen):
        # Game Logo at top (scaled up to 150x150)
        if self.logo:
            logoRect = self.logo.get_rect(center=(self.screenW // 2, 85))
            screen.blit(self.logo, logoRect)

        # Title Glow & Text: SYNTAX ERROR (68pt bold)
        titleText = "SYNTAX ERROR"
        glowSurf = self.titleFont.render(titleText, True, (40, 140, 90))
        textSurf = self.titleFont.render(titleText, True, config.COLOR_CPU)
        tRect = textSurf.get_rect(center=(self.screenW // 2, 195))
        screen.blit(glowSurf, tRect.move(3, 3))
        screen.blit(textSurf, tRect)

        # Subtitle: CODE TOWER DEFENSE (24pt bold)
        subText = "CODE TOWER DEFENSE // KNIGHT HACKS IX // PYTHON 3"
        subSurf = self.subFont.render(subText, True, (120, 160, 190))
        sRect = subSurf.get_rect(center=(self.screenW // 2, 246))
        screen.blit(subSurf, sRect)

        # Scaled up decorative bracket frame around buttons (460x300)
        bracketW = 460
        bracketH = 300
        bx = (self.screenW - bracketW) // 2
        by = 280
        pygame.draw.rect(screen, (30, 48, 68), (bx, by, bracketW, bracketH), 1, border_radius=8)

        # Buttons
        for b in self.mainButtons:
            b.draw(screen, self.btnFont)

    def _drawScoreboardView(self, screen):
        # Panel container (expanded to 880 px for clean column spacing)
        panelW, panelH = 880, 520
        px = (self.screenW - panelW) // 2
        py = 55
        pygame.draw.rect(screen, (18, 25, 35), (px, py, panelW, panelH), border_radius=8)
        pygame.draw.rect(screen, (70, 200, 120), (px, py, panelW, panelH), 2, border_radius=8)
        # Header
        title = self.titleFont.render("LOCAL SCOREBOARD", True, config.COLOR_CPU)
        screen.blit(title, title.get_rect(center=(self.screenW // 2, py + 40)))
        sub = self.subFont.render("Persisted on-device: top hacking simulations survived", True, (140, 170, 200))
        screen.blit(sub, sub.get_rect(center=(self.screenW // 2, py + 75)))
        # Table Column Definitions: (label, xOffset, alignment)
        colY = py + 115
        headers = [
            ("RANK", px + 65, "center"),
            ("HANDLE", px + 150, "left"),
            ("WAVE REACHED", px + 440, "center"),
            ("BYTES", px + 620, "center"),
            ("BUGS KILLED", px + 760, "center"),
        ]
        for text, hx, align in headers:
            txt = self.headerFont.render(text, True, (100, 180, 255))
            if align == "center":
                rect = txt.get_rect(center=(hx, colY))
            else:
                rect = txt.get_rect(midleft=(hx, colY))
            screen.blit(txt, rect)
        # Divider line under column headers
        pygame.draw.line(screen, (40, 70, 100), (px + 30, colY + 20), (px + panelW - 30, colY + 20), 2)
        # Records
        scores = getScoreboard()
        rowY = colY + 36
        for i, s in enumerate(scores[:10]):
            # Subtle alternating row background for clean arcade leaderboard styling
            if i % 2 == 0:
                stripeRect = pygame.Rect(px + 30, rowY - 4, panelW - 60, 28)
                pygame.draw.rect(screen, (24, 34, 46), stripeRect, border_radius=4)
            rankCol = (255, 215, 0) if i == 0 else ((200, 220, 240) if i < 3 else (140, 160, 180))
            rTxt = self.bodyFont.render(f"#{i+1}", True, rankCol)
            nTxt = self.bodyFont.render(str(s.get("name", "Unknown")), True, (220, 235, 250))
            wTxt = self.bodyFont.render(f"Wave {s.get('wave', 0)}", True, (70, 200, 120))
            bTxt = self.bodyFont.render(f"{s.get('bytes', 0)} B", True, (255, 180, 80))
            kTxt = self.bodyFont.render(str(s.get("kills", 0)), True, (255, 100, 100))
            # Draw precisely aligned to each column
            screen.blit(rTxt, rTxt.get_rect(center=(px + 65, rowY + 10)))
            screen.blit(nTxt, nTxt.get_rect(midleft=(px + 150, rowY + 10)))
            screen.blit(wTxt, wTxt.get_rect(center=(px + 440, rowY + 10)))
            screen.blit(bTxt, bTxt.get_rect(center=(px + 620, rowY + 10)))
            screen.blit(kTxt, kTxt.get_rect(center=(px + 760, rowY + 10)))
            rowY += 32
        self.backBtn.draw(screen, self.btnFont)

    def _drawGuideView(self, screen):
        # Panel container
        panelW, panelH = 920, 560
        px = (self.screenW - panelW) // 2
        py = 50
        pygame.draw.rect(screen, (18, 25, 35), (px, py, panelW, panelH), border_radius=8)
        pygame.draw.rect(screen, (90, 160, 255), (px, py, panelW, panelH), 2, border_radius=8)

        # Title
        title = self.titleFont.render("OPERATOR MANUAL & GUIDE", True, (90, 180, 255))
        screen.blit(title, title.get_rect(center=(self.screenW // 2, py + 40)))

        # Guide Sections
        sections = [
            ("GOAL & CORE LOOP", [
                "Protect your CPU core on the circuit board against 10 escalating bug waves.",
                "1. Build Phase: Place defense tools, program their Python scripts, and buy upgrades.",
                "2. Wave Phase: Bugs pathfind using Dijkstra flow fields and pheromones.",
            ]),
            ("CONTROLS", [
                "• Left Click: Place selected defense tool on grid.",
                "• Right Click: Remove / sell existing tool (recovers 50% bytes).",
                "• [ENTER]: Begin wave immediately.",
                "• [ESC]: Pause / Back to Menu.",
            ]),
            ("PROGRAMMING YOUR TOWERS", [
                "Each programmable tower executes real Python via a tick() function (~8x/sec):",
                "  targets = enemiesInRange()  # Read-only EnemyViews, sorted nearest first",
                "  aim(targets[0]); fire()     # Lock on and shoot",
                "Watch your Cycle Budget! Excessive loops cause Towers to Jam.",
            ]),
            ("ADAPTIVE SWARM INTELLIGENCE", [
                "• Flow Fields: Bugs recalculate Dijkstra fields outward from the CPU.",
                "• Fear Pheromones: Bugs leave death trails, actively routing around kill zones!",
                "• Zero-Days can leap over firewalls; Injections corrupt your Python scripts.",
            ]),
        ]

        curY = py + 85
        for heading, lines in sections:
            hSurf = self.headerFont.render(heading, True, config.COLOR_CPU)
            screen.blit(hSurf, (px + 35, curY))
            curY += 26
            for line in lines:
                lSurf = self.bodyFont.render(line, True, (210, 225, 240))
                screen.blit(lSurf, (px + 50, curY))
                curY += 21
            curY += 8

        self.backBtn.draw(screen, self.btnFont)

