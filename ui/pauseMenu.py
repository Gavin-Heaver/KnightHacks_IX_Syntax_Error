# ui/pauseMenu.py -- Cyberpunk themed pause overlay with confirmation dialogs.
import pygame
import config
from ui.volumeControls import VolumeModal


class PauseButton:
    def __init__(self, rect, text, actionKey, style="default"):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.actionKey = actionKey
        self.style = style  # "default", "green", "red"
        self.isHovered = False

    def checkHover(self, mousePos):
        self.isHovered = self.rect.collidepoint(mousePos)
        return self.isHovered

    def draw(self, screen, font):
        if self.style == "green":
            # Confirmation YES: Matrix emerald
            bg = (28, 70, 45) if self.isHovered else (14, 38, 24)
            border = (85, 250, 145) if self.isHovered else (45, 160, 85)
            txtCol = (255, 255, 255) if self.isHovered else (195, 250, 215)
        elif self.style == "red":
            # Confirmation NO: Alert crimson
            bg = (75, 22, 28) if self.isHovered else (42, 14, 18)
            border = (255, 85, 95) if self.isHovered else (180, 45, 55)
            txtCol = (255, 240, 240) if self.isHovered else (245, 185, 190)
        else:
            # Default Pause Button: Cyberpunk Terminal (matches Main Menu)
            bg = (26, 62, 48) if self.isHovered else (14, 26, 36)
            border = (85, 250, 145) if self.isHovered else (45, 135, 88)
            txtCol = (255, 255, 255) if self.isHovered else (195, 248, 220)

        pygame.draw.rect(screen, bg, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=6)

        displayText = f"► {self.text}" if self.isHovered else self.text
        txtSurf = font.render(displayText, True, txtCol)
        txtRect = txtSurf.get_rect(center=self.rect.center)
        screen.blit(txtSurf, txtRect)


class PauseMenu:
    def __init__(self, screenW=config.SCREEN_W, screenH=config.SCREEN_H):
        self.screenW = screenW
        self.screenH = screenH
        self.state = "menu"  # "menu", "confirm_restart", "confirm_menu", "volume"

        # Fonts
        self.titleFont = pygame.font.SysFont("consolas", 30, bold=True)
        self.subTitleFont = pygame.font.SysFont("consolas", 22, bold=True)
        self.btnFont = pygame.font.SysFont("consolas", 20, bold=True)
        self.bodyFont = pygame.font.SysFont("consolas", 16)
        self.hintFont = pygame.font.SysFont("consolas", 14)

        # Volume Controls Modal
        self.volumeModal = VolumeModal(screenW // 2, screenH // 2, width=600, height=440, backText="BACK TO PAUSE")

        # Setup Buttons
        self._buildButtons()

    def _buildButtons(self):
        # 1. Main Pause Menu Box
        self.mainPanelW, self.mainPanelH = 380, 328
        px = (self.screenW - self.mainPanelW) // 2
        py = (self.screenH - self.mainPanelH) // 2
        self.mainPanelRect = pygame.Rect(px, py, self.mainPanelW, self.mainPanelH)

        btnW, btnH = 260, 42
        bx = px + (self.mainPanelW - btnW) // 2
        gap = 52
        self.mainButtons = [
            PauseButton((bx, py + 66, btnW, btnH), "RESUME", "resume"),
            PauseButton((bx, py + 66 + gap, btnW, btnH), "VOLUME CONTROLS", "volume"),
            PauseButton((bx, py + 66 + gap * 2, btnW, btnH), "RESTART", "restart"),
            PauseButton((bx, py + 66 + gap * 3, btnW, btnH), "MAIN MENU", "main_menu"),
        ]

        # 2. Confirm Restart Dialog Box
        self.restartPanelW, self.restartPanelH = 520, 230
        rx = (self.screenW - self.restartPanelW) // 2
        ry = (self.screenH - self.restartPanelH) // 2
        self.restartPanelRect = pygame.Rect(rx, ry, self.restartPanelW, self.restartPanelH)

        cBtnW, cBtnH = 140, 44
        self.restartYesBtn = PauseButton((rx + 75, ry + 152, cBtnW, cBtnH), "YES", "confirm_restart_yes", style="green")
        self.restartNoBtn = PauseButton((rx + self.restartPanelW - 75 - cBtnW, ry + 152, cBtnW, cBtnH), "NO", "confirm_restart_no", style="red")

        # 3. Confirm Main Menu Dialog Box
        self.menuPanelW, self.menuPanelH = 580, 260
        mx = (self.screenW - self.menuPanelW) // 2
        my = (self.screenH - self.menuPanelH) // 2
        self.menuPanelRect = pygame.Rect(mx, my, self.menuPanelW, self.menuPanelH)

        self.menuYesBtn = PauseButton((mx + 95, my + 182, cBtnW, cBtnH), "YES", "confirm_menu_yes", style="green")
        self.menuNoBtn = PauseButton((mx + self.menuPanelW - 95 - cBtnW, my + 182, cBtnW, cBtnH), "NO", "confirm_menu_no", style="red")

    def open(self):
        """Opens pause menu at base menu state."""
        self.state = "menu"

    def handleEvent(self, event):
        """
        Processes events while game is paused.
        Returns:
            "resume"    -> unpause game
            "restart"   -> reset and restart wave 1
            "main_menu" -> reset and return to title screen
            None        -> stay in pause menu
        """
        if self.state == "volume":
            action = self.volumeModal.handleEvent(event)
            if action == "back":
                self.state = "menu"
            return None

        if event.type == pygame.MOUSEMOTION:
            mpos = event.pos
            if self.state == "menu":
                for b in self.mainButtons:
                    b.checkHover(mpos)
            elif self.state == "confirm_restart":
                self.restartYesBtn.checkHover(mpos)
                self.restartNoBtn.checkHover(mpos)
            elif self.state == "confirm_menu":
                self.menuYesBtn.checkHover(mpos)
                self.menuNoBtn.checkHover(mpos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mpos = event.pos
            if self.state == "menu":
                for b in self.mainButtons:
                    if b.rect.collidepoint(mpos):
                        if b.actionKey == "resume":
                            return "resume"
                        elif b.actionKey == "volume":
                            self.state = "volume"
                        elif b.actionKey == "restart":
                            self.state = "confirm_restart"
                        elif b.actionKey == "main_menu":
                            self.state = "confirm_menu"
                        return None

            elif self.state == "confirm_restart":
                if self.restartYesBtn.rect.collidepoint(mpos):
                    self.state = "menu"
                    return "restart"
                elif self.restartNoBtn.rect.collidepoint(mpos):
                    self.state = "menu"
                    return None

            elif self.state == "confirm_menu":
                if self.menuYesBtn.rect.collidepoint(mpos):
                    self.state = "menu"
                    return "main_menu"
                elif self.menuNoBtn.rect.collidepoint(mpos):
                    self.state = "menu"
                    return None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state in ("confirm_restart", "confirm_menu", "volume"):
                    self.state = "menu"
                else:
                    return "resume"

            elif event.key == pygame.K_RETURN:
                if self.state == "menu":
                    return "resume"

        return None

    def _drawCyberFrame(self, screen, rect, fillAlpha=245, borderCol=(50, 150, 95), accCol=(80, 245, 140)):
        """Draws frosted cyber glass container with glowing border and neon corner brackets."""
        px, py, pw, ph = rect.x, rect.y, rect.w, rect.h
        panelSurf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panelSurf.fill((10, 18, 26, fillAlpha))
        screen.blit(panelSurf, (px, py))
        pygame.draw.rect(screen, borderCol, (px, py, pw, ph), 2, border_radius=8)

        # High-voltage neon corner accents
        cLen = 16
        pygame.draw.line(screen, accCol, (px, py), (px + cLen, py), 3)
        pygame.draw.line(screen, accCol, (px, py), (px, py + cLen), 3)
        pygame.draw.line(screen, accCol, (px + pw, py), (px + pw - cLen, py), 3)
        pygame.draw.line(screen, accCol, (px + pw, py), (px + pw, py + cLen), 3)
        pygame.draw.line(screen, accCol, (px, py + ph), (px + cLen, py + ph), 3)
        pygame.draw.line(screen, accCol, (px, py + ph), (px, py + ph - cLen), 3)
        pygame.draw.line(screen, accCol, (px + pw, py + ph), (px + pw - cLen, py + ph), 3)
        pygame.draw.line(screen, accCol, (px + pw, py + ph), (px + pw, py + ph - cLen), 3)

    def draw(self, screen):
        # 1. Darkened backdrop scrim with cyber scanline feel
        shade = pygame.Surface((self.screenW, self.screenH), pygame.SRCALPHA)
        shade.fill((5, 10, 16, 175))
        screen.blit(shade, (0, 0))

        # 2. Render state modal
        if self.state == "menu":
            self._drawMainMenu(screen)
        elif self.state == "confirm_restart":
            self._drawConfirmRestart(screen)
        elif self.state == "confirm_menu":
            self._drawConfirmMenu(screen)
        elif self.state == "volume":
            self.volumeModal.draw(screen)

    def _drawMainMenu(self, screen):
        rect = self.mainPanelRect
        self._drawCyberFrame(screen, rect, fillAlpha=245, borderCol=(50, 150, 95), accCol=(80, 245, 140))

        # Header Glow & Text: PAUSED
        titleText = "PAUSED"
        tSurf = self.titleFont.render(titleText, True, (105, 255, 160))
        gSurf = self.titleFont.render(titleText, True, (20, 110, 65))
        tRect = tSurf.get_rect(center=(rect.centerx, rect.y + 24))
        screen.blit(gSurf, tRect.move(2, 2))
        screen.blit(tSurf, tRect)

        subSurf = self.hintFont.render("// SIMULATION SUSPENDED", True, (140, 225, 245))
        screen.blit(subSurf, subSurf.get_rect(center=(rect.centerx, rect.y + 44)))

        # Header horizontal divider line
        pygame.draw.line(screen, (40, 115, 80), (rect.x + 25, rect.y + 56), (rect.right - 25, rect.y + 56), 1)

        # Buttons
        for b in self.mainButtons:
            b.draw(screen, self.btnFont)

        # Footer hint
        hintSurf = self.hintFont.render("[ESC] / [ENTER] Resume", True, (120, 175, 195))
        screen.blit(hintSurf, hintSurf.get_rect(center=(rect.centerx, rect.bottom - 16)))

    def _drawConfirmRestart(self, screen):
        rect = self.restartPanelRect
        self._drawCyberFrame(screen, rect, fillAlpha=245, borderCol=(220, 150, 50), accCol=(255, 210, 70))

        # Header Glow & Text: RESTART MISSION?
        titleText = "// RESTART MISSION?"
        tSurf = self.subTitleFont.render(titleText, True, (255, 210, 80))
        gSurf = self.subTitleFont.render(titleText, True, (100, 70, 20))
        tRect = tSurf.get_rect(center=(rect.centerx, rect.y + 28))
        screen.blit(gSurf, tRect.move(2, 2))
        screen.blit(tSurf, tRect)

        # Header horizontal divider line
        pygame.draw.line(screen, (160, 105, 35), (rect.x + 30, rect.y + 52), (rect.right - 30, rect.y + 52), 1)

        # Message
        msgSurf = self.bodyFont.render("Current wave progress will be completely erased.", True, (220, 235, 245))
        screen.blit(msgSurf, msgSurf.get_rect(center=(rect.centerx, rect.y + 82)))

        subMsg = self.bodyFont.render("All active defense towers will be dismantled.", True, (255, 130, 100))
        screen.blit(subMsg, subMsg.get_rect(center=(rect.centerx, rect.y + 110)))

        # Buttons
        self.restartYesBtn.draw(screen, self.btnFont)
        self.restartNoBtn.draw(screen, self.btnFont)

    def _drawConfirmMenu(self, screen):
        rect = self.menuPanelRect
        self._drawCyberFrame(screen, rect, fillAlpha=245, borderCol=(220, 150, 50), accCol=(255, 210, 70))

        # Header Glow & Text: RETURN TO MAIN MENU?
        titleText = "// RETURN TO MAIN MENU?"
        tSurf = self.subTitleFont.render(titleText, True, (255, 210, 80))
        gSurf = self.subTitleFont.render(titleText, True, (100, 70, 20))
        tRect = tSurf.get_rect(center=(rect.centerx, rect.y + 28))
        screen.blit(gSurf, tRect.move(2, 2))
        screen.blit(tSurf, tRect)

        # Header horizontal divider line
        pygame.draw.line(screen, (160, 105, 35), (rect.x + 30, rect.y + 52), (rect.right - 30, rect.y + 52), 1)

        # Multi-line message
        line1 = self.bodyFont.render("Arcade session active: Unfinished simulation data will be lost.", True, (220, 235, 245))
        line2 = self.bodyFont.render("Only completed games are recorded to the Local Scoreboard.", True, (140, 225, 245))
        line3 = self.bodyFont.render("Confirm abort protocol and return to title screen?", True, (255, 180, 70))

        screen.blit(line1, line1.get_rect(center=(rect.centerx, rect.y + 84)))
        screen.blit(line2, line2.get_rect(center=(rect.centerx, rect.y + 112)))
        screen.blit(line3, line3.get_rect(center=(rect.centerx, rect.y + 140)))

        # Buttons
        self.menuYesBtn.draw(screen, self.btnFont)
        self.menuNoBtn.draw(screen, self.btnFont)
