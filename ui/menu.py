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
    def __init__(self, rect, text, actionKey, style="default"):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.actionKey = actionKey
        self.isHovered = False
        self.style = style

    def checkHover(self, mousePos):
        self.isHovered = self.rect.collidepoint(mousePos)
        return self.isHovered

    def draw(self, screen, font):
        if self.style == "main":
            # Cyberpunk terminal palette for main menu
            bg = (14, 26, 36) if not self.isHovered else (26, 62, 48)
            border = (85, 250, 145) if self.isHovered else (45, 135, 88)
            textCol = (255, 255, 255) if self.isHovered else (195, 248, 220)
            displayText = f"► {self.text}" if self.isHovered else self.text
        else:
            # Default modal palette for Scoreboard & Guide
            bg = (24, 38, 54) if not self.isHovered else (45, 75, 110)
            border = (70, 200, 120) if self.isHovered else (50, 100, 160)
            textCol = (240, 255, 245) if self.isHovered else (200, 220, 240)
            displayText = self.text

        pygame.draw.rect(screen, bg, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=6)

        txtSurf = font.render(displayText, True, textCol)
        txtRect = txtSurf.get_rect(center=self.rect.center)
        screen.blit(txtSurf, txtRect)


class StartMenu:
    def __init__(self, screenW=config.SCREEN_W, screenH=config.SCREEN_H):
        self.screenW = screenW
        self.screenH = screenH
        self.state = "main"    # "main", "scoreboard", "guide"

        # Fonts
        self.titleFont = pygame.font.SysFont("consolas", 68, bold=True)
        self.modalTitleFont = pygame.font.SysFont("consolas", 40, bold=True)
        self.subFont = pygame.font.SysFont("consolas", 24, bold=True)
        self.modalSubFont = pygame.font.SysFont("consolas", 18)
        self.btnFont = pygame.font.SysFont("consolas", 26, bold=True)
        self.bodyFont = pygame.font.SysFont("consolas", 18)
        self.headerFont = pygame.font.SysFont("consolas", 22, bold=True)

        # Load and scale main menu background
        self.bgImage = None
        bgPath = os.path.join("assets", "Background.png")
        if os.path.exists(bgPath):
            try:
                rawBg = pygame.image.load(bgPath).convert()
                self.bgImage = pygame.transform.smoothscale(rawBg, (screenW, screenH))
            except Exception as e:
                print("Failed to load Background.png:", e)

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
            MenuButton((startX, startY, btnW, btnH), "PLAY GAME", "play", style="main"),
            MenuButton((startX, startY + gap, btnW, btnH), "SCOREBOARD", "scoreboard", style="main"),
            MenuButton((startX, startY + gap * 2, btnW, btnH), "GUIDE & MANUAL", "guide", style="main"),
            MenuButton((startX, startY + gap * 3, btnW, btnH), "QUIT GAME", "quit", style="main"),
        ]

        # Modal Back Button (styled with cyber terminal theme)
        self.backBtn = MenuButton((startX, 608, btnW, 52), "BACK TO MENU", "back", style="main")

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

    def _drawCyberFrame(self, screen, rect, fillAlpha=235):
        """Draws frosted cyber glass panel with wireframe emerald border and neon corner brackets."""
        px, py, pw, ph = rect
        panelSurf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panelSurf.fill((10, 18, 26, fillAlpha))
        screen.blit(panelSurf, (px, py))
        pygame.draw.rect(screen, (50, 150, 95), (px, py, pw, ph), 2, border_radius=8)

        # High-voltage neon corner accent brackets
        cornerLen = 16
        accCol = (80, 245, 140)
        # Top-left
        pygame.draw.line(screen, accCol, (px, py), (px + cornerLen, py), 3)
        pygame.draw.line(screen, accCol, (px, py), (px, py + cornerLen), 3)
        # Top-right
        pygame.draw.line(screen, accCol, (px + pw, py), (px + pw - cornerLen, py), 3)
        pygame.draw.line(screen, accCol, (px + pw, py), (px + pw, py + cornerLen), 3)
        # Bottom-left
        pygame.draw.line(screen, accCol, (px, py + ph), (px + cornerLen, py + ph), 3)
        pygame.draw.line(screen, accCol, (px, py + ph), (px, py + ph - cornerLen), 3)
        # Bottom-right
        pygame.draw.line(screen, accCol, (px + pw, py + ph), (px + pw - cornerLen, py + ph), 3)
        pygame.draw.line(screen, accCol, (px + pw, py + ph), (px + pw, py + ph - cornerLen), 3)

    def draw(self, screen):
        # Background: use Background.png across all views if present
        if self.bgImage:
            screen.blit(self.bgImage, (0, 0))
        else:
            screen.fill(config.COLOR_BG)
            self._drawDecorations(screen)

        if self.state == "main":
            self._drawMainView(screen)
        elif self.state == "scoreboard":
            # Darkened scrim overlay so scoreboard stands out sharply over background
            scrim = pygame.Surface((self.screenW, self.screenH), pygame.SRCALPHA)
            scrim.fill((5, 12, 18, 140))
            screen.blit(scrim, (0, 0))
            self._drawScoreboardView(screen)
        elif self.state == "guide":
            # Darkened scrim overlay so guide text stands out sharply over background
            scrim = pygame.Surface((self.screenW, self.screenH), pygame.SRCALPHA)
            scrim.fill((5, 12, 18, 140))
            screen.blit(scrim, (0, 0))
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
        # Game Logo at top (with soft dark circular backing for high contrast)
        if self.logo:
            logoCenter = (self.screenW // 2, 85)
            backingSurf = pygame.Surface((156, 156), pygame.SRCALPHA)
            pygame.draw.circle(backingSurf, (8, 14, 22, 190), (78, 78), 75)
            pygame.draw.circle(backingSurf, (35, 110, 75, 220), (78, 78), 75, width=2)
            screen.blit(backingSurf, backingSurf.get_rect(center=logoCenter))
            screen.blit(self.logo, self.logo.get_rect(center=logoCenter))

        # Title Glow & Text: SYNTAX ERROR (68pt bold)
        titleText = "SYNTAX ERROR"
        textSurf = self.titleFont.render(titleText, True, (105, 255, 160))
        glowSurf = self.titleFont.render(titleText, True, (20, 110, 65))
        tRect = textSurf.get_rect(center=(self.screenW // 2, 195))

        # Backing pill for title readability against background bars
        titleBacking = pygame.Surface((tRect.width + 44, tRect.height + 12), pygame.SRCALPHA)
        titleBacking.fill((8, 14, 22, 210))
        pygame.draw.rect(titleBacking, (40, 130, 85, 180), titleBacking.get_rect(), width=1, border_radius=8)
        screen.blit(titleBacking, titleBacking.get_rect(center=tRect.center))

        screen.blit(glowSurf, tRect.move(3, 3))
        screen.blit(textSurf, tRect)

        # Subtitle: CODE TOWER DEFENSE (24pt bold)
        subText = "CODE TOWER DEFENSE // KNIGHT HACKS IX // PYTHON 3"
        subSurf = self.subFont.render(subText, True, (140, 225, 245))
        sRect = subSurf.get_rect(center=(self.screenW // 2, 246))

        # Subtitle backing
        subBacking = pygame.Surface((sRect.width + 30, sRect.height + 8), pygame.SRCALPHA)
        subBacking.fill((8, 14, 22, 195))
        pygame.draw.rect(subBacking, (30, 95, 70, 160), subBacking.get_rect(), width=1, border_radius=6)
        screen.blit(subBacking, subBacking.get_rect(center=sRect.center))

        screen.blit(subSurf, sRect)

        # Scaled up decorative bracket frame around buttons (460x300) with frosted cyber glass
        bracketW = 460
        bracketH = 300
        bx = (self.screenW - bracketW) // 2
        by = 280
        frameSurf = pygame.Surface((bracketW, bracketH), pygame.SRCALPHA)
        frameSurf.fill((10, 18, 26, 215))
        screen.blit(frameSurf, (bx, by))
        pygame.draw.rect(screen, (50, 150, 95), (bx, by, bracketW, bracketH), 2, border_radius=8)

        # Corner accent notches for cyberpunk aesthetic
        cornerLen = 14
        accCol = (80, 245, 140)
        pygame.draw.line(screen, accCol, (bx, by), (bx + cornerLen, by), 3)
        pygame.draw.line(screen, accCol, (bx, by), (bx, by + cornerLen), 3)
        pygame.draw.line(screen, accCol, (bx + bracketW, by), (bx + bracketW - cornerLen, by), 3)
        pygame.draw.line(screen, accCol, (bx + bracketW, by), (bx + bracketW, by + cornerLen), 3)
        pygame.draw.line(screen, accCol, (bx, by + bracketH), (bx + cornerLen, by + bracketH), 3)
        pygame.draw.line(screen, accCol, (bx, by + bracketH), (bx, by + bracketH - cornerLen), 3)
        pygame.draw.line(screen, accCol, (bx + bracketW, by + bracketH), (bx + bracketW - cornerLen, by + bracketH), 3)
        pygame.draw.line(screen, accCol, (bx + bracketW, by + bracketH), (bx + bracketW, by + bracketH - cornerLen), 3)

        # Buttons
        for b in self.mainButtons:
            b.draw(screen, self.btnFont)

    def _drawScoreboardView(self, screen):
        panelW, panelH = 920, 545
        px = (self.screenW - panelW) // 2
        py = 42

        # Draw frosted cyber glass container
        self._drawCyberFrame(screen, (px, py, panelW, panelH), fillAlpha=235)

        # Header Glow & Text: LOCAL SCOREBOARD
        titleText = "LOCAL SCOREBOARD"
        textSurf = self.modalTitleFont.render(titleText, True, (105, 255, 160))
        glowSurf = self.modalTitleFont.render(titleText, True, (20, 110, 65))
        tRect = textSurf.get_rect(center=(self.screenW // 2, py + 36))
        screen.blit(glowSurf, tRect.move(2, 2))
        screen.blit(textSurf, tRect)

        sub = self.modalSubFont.render("Persisted on-device: top hacking simulations survived", True, (140, 225, 245))
        screen.blit(sub, sub.get_rect(center=(self.screenW // 2, py + 72)))

        # Table Column Definitions: (label, xOffset, alignment)
        colY = py + 108
        headers = [
            ("RANK", px + 65, "center"),
            ("HANDLE", px + 150, "left"),
            ("WAVE REACHED", px + 440, "center"),
            ("BYTES", px + 640, "center"),
            ("BUGS KILLED", px + 800, "center"),
        ]
        for text, hx, align in headers:
            txt = self.headerFont.render(text, True, (85, 245, 155))
            if align == "center":
                rect = txt.get_rect(center=(hx, colY))
            else:
                rect = txt.get_rect(midleft=(hx, colY))
            screen.blit(txt, rect)

        # Matrix green divider line under column headers
        pygame.draw.line(screen, (45, 135, 88), (px + 30, colY + 18), (px + panelW - 30, colY + 18), 2)

        # Records
        scores = getScoreboard()
        rowY = colY + 32
        for i, s in enumerate(scores[:10]):
            if i % 2 == 0:
                stripeRect = pygame.Rect(px + 28, rowY - 4, panelW - 56, 28)
                stripeSurf = pygame.Surface((stripeRect.width, stripeRect.height), pygame.SRCALPHA)
                stripeSurf.fill((16, 30, 44, 180))
                screen.blit(stripeSurf, stripeRect)

            rankCol = (255, 215, 0) if i == 0 else ((210, 235, 250) if i < 3 else (145, 175, 195))
            rTxt = self.bodyFont.render(f"#{i+1}", True, rankCol)
            nTxt = self.bodyFont.render(str(s.get("name", "Unknown")), True, (235, 248, 255))
            wTxt = self.bodyFont.render(f"Wave {s.get('wave', 0)}", True, (85, 250, 145))
            bTxt = self.bodyFont.render(f"{s.get('bytes', 0)} B", True, (255, 200, 80))
            kTxt = self.bodyFont.render(str(s.get("kills", 0)), True, (255, 110, 110))

            screen.blit(rTxt, rTxt.get_rect(center=(px + 65, rowY + 10)))
            screen.blit(nTxt, nTxt.get_rect(midleft=(px + 150, rowY + 10)))
            screen.blit(wTxt, wTxt.get_rect(center=(px + 440, rowY + 10)))
            screen.blit(bTxt, bTxt.get_rect(center=(px + 640, rowY + 10)))
            screen.blit(kTxt, kTxt.get_rect(center=(px + 800, rowY + 10)))
            rowY += 32

        self.backBtn.draw(screen, self.btnFont)

    def _drawGuideView(self, screen):
        panelW, panelH = 960, 555
        px = (self.screenW - panelW) // 2
        py = 38

        # Draw frosted cyber glass container
        self._drawCyberFrame(screen, (px, py, panelW, panelH), fillAlpha=235)

        # Header Glow & Text: OPERATOR MANUAL & GUIDE
        titleText = "OPERATOR MANUAL & GUIDE"
        textSurf = self.modalTitleFont.render(titleText, True, (105, 255, 160))
        glowSurf = self.modalTitleFont.render(titleText, True, (20, 110, 65))
        tRect = textSurf.get_rect(center=(self.screenW // 2, py + 34))
        screen.blit(glowSurf, tRect.move(2, 2))
        screen.blit(textSurf, tRect)

        sub = self.modalSubFont.render("Tactical Protocol, Defensive Algorithms, and Swarm Specs", True, (140, 225, 245))
        screen.blit(sub, sub.get_rect(center=(self.screenW // 2, py + 62)))

        # Guide Sections
        sections = [
            ("GOAL & CORE LOOP", [
                "Protect your central CPU on the circuit board against 10 escalating bug waves.",
                "1. Build Phase: Deploy defense tools, customize Python scripts, and purchase upgrades.",
                "2. Wave Phase: Swarms execute adaptive Dijkstra flow fields and fear pheromones.",
            ]),
            ("CONTROLS & TACTICS", [
                "• Left Click: Deploy equipped defense tool on empty grid tile.",
                "• Right Click: Dismantle / sell existing tool (recovers 50% spent bytes).",
                "• [ENTER]: Launch incoming wave immediately.",
                "• [ESC]: Pause simulation / Return to Main Menu.",
            ]),
            ("PROGRAMMING DEFENSE TOOLS", [
                "Each programmable tower executes sandboxed Python in its tick() loop (~8x/sec):",
                "  targets = enemiesInRange()  # Read-only EnemyViews, sorted closest first",
                "  aim(targets[0]); fire()     # Aim projectile/laser and attack",
                "Watch your Cycle Budget! Unbounded loops will jam your tower hardware.",
            ]),
            ("ADAPTIVE ENEMY SWARM INTELLIGENCE", [
                "• Flow Fields: Bugs solve dynamic Dijkstra pathfinding around placed obstacles.",
                "• Fear Pheromones: Bugs leave death trails, actively routing around kill zones!",
                "• Zero-Days can teleport over firewalls; Injections corrupt tower Python scripts.",
            ]),
        ]

        curY = py + 84
        for heading, lines in sections:
            hSurf = self.headerFont.render(f"// {heading}", True, (85, 245, 155))
            screen.blit(hSurf, (px + 35, curY))
            curY += 25
            for line in lines:
                isCode = line.startswith("  ")
                lineCol = (140, 225, 245) if isCode else (215, 235, 245)
                lSurf = self.bodyFont.render(line, True, lineCol)
                screen.blit(lSurf, (px + 45, curY))
                curY += 21
            curY += 7

        self.backBtn.draw(screen, self.btnFont)

