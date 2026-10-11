# ui/pauseMenu.py -- Pause overlay with confirmation dialogs.
import pygame
import config


from ui.volumeControls import VolumeModal
from game.audio import audioManager


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
            bg = (32, 85, 48) if self.isHovered else (18, 50, 30)
            border = (90, 240, 130) if self.isHovered else (50, 180, 85)
            txtCol = (240, 255, 245) if self.isHovered else (190, 240, 205)
        elif self.style == "red":
            bg = (95, 30, 36) if self.isHovered else (55, 20, 25)
            border = (255, 90, 100) if self.isHovered else (200, 55, 65)
            txtCol = (255, 240, 240) if self.isHovered else (245, 195, 195)
        else:
            bg = (42, 68, 98) if self.isHovered else (24, 38, 56)
            border = (90, 180, 255) if self.isHovered else (50, 105, 165)
            txtCol = (255, 255, 255) if self.isHovered else (200, 220, 240)

        pygame.draw.rect(screen, bg, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=6)

        txtSurf = font.render(self.text, True, txtCol)
        txtRect = txtSurf.get_rect(center=self.rect.center)
        screen.blit(txtSurf, txtRect)


class PauseMenu:
    def __init__(self, screenW=config.SCREEN_W, screenH=config.SCREEN_H):
        self.screenW = screenW
        self.screenH = screenH
        self.state = "menu"  # "menu", "confirm_restart", "confirm_menu", "volume"

        # Fonts
        self.titleFont = pygame.font.SysFont("consolas", 28, bold=True)
        self.subTitleFont = pygame.font.SysFont("consolas", 22, bold=True)
        self.btnFont = pygame.font.SysFont("consolas", 20, bold=True)
        self.bodyFont = pygame.font.SysFont("consolas", 16)
        self.hintFont = pygame.font.SysFont("consolas", 13)

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
        self.restartYesBtn = PauseButton((rx + 75, ry + 150, cBtnW, cBtnH), "YES", "confirm_restart_yes", style="green")
        self.restartNoBtn = PauseButton((rx + self.restartPanelW - 75 - cBtnW, ry + 150, cBtnW, cBtnH), "NO", "confirm_restart_no", style="red")

        # 3. Confirm Main Menu Dialog Box
        self.menuPanelW, self.menuPanelH = 580, 260
        mx = (self.screenW - self.menuPanelW) // 2
        my = (self.screenH - self.menuPanelH) // 2
        self.menuPanelRect = pygame.Rect(mx, my, self.menuPanelW, self.menuPanelH)

        self.menuYesBtn = PauseButton((mx + 95, my + 180, cBtnW, cBtnH), "YES", "confirm_menu_yes", style="green")
        self.menuNoBtn = PauseButton((mx + self.menuPanelW - 95 - cBtnW, my + 180, cBtnW, cBtnH), "NO", "confirm_menu_no", style="red")

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
                audioManager.sfx("back")
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
                        audioManager.sfx("select")
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
                    audioManager.sfx("select")
                    self.state = "menu"
                    return "restart"
                elif self.restartNoBtn.rect.collidepoint(mpos):
                    audioManager.sfx("back")
                    self.state = "menu"
                    return None

            elif self.state == "confirm_menu":
                if self.menuYesBtn.rect.collidepoint(mpos):
                    audioManager.sfx("select")
                    self.state = "menu"
                    return "main_menu"
                elif self.menuNoBtn.rect.collidepoint(mpos):
                    audioManager.sfx("back")
                    self.state = "menu"
                    return None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                audioManager.sfx("back")
                if self.state in ("confirm_restart", "confirm_menu", "volume"):
                    self.state = "menu"
                else:
                    return "resume"

            elif event.key == pygame.K_RETURN:
                if self.state == "menu":
                    audioManager.sfx("select")
                    return "resume"

        return None

    def draw(self, screen):
        # 1. Fullscreen semi-transparent backdrop
        shade = pygame.Surface((self.screenW, self.screenH), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
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
        pygame.draw.rect(screen, (18, 25, 36), rect, border_radius=8)
        pygame.draw.rect(screen, (50, 80, 120), rect, width=2, border_radius=8)

        # Header accent bar
        pygame.draw.rect(screen, (32, 48, 70), (rect.x + 2, rect.y + 2, rect.w - 4, 48),
                         border_top_left_radius=7, border_top_right_radius=7)
        pygame.draw.line(screen, (60, 100, 150), (rect.x, rect.y + 50), (rect.right, rect.y + 50), 2)

        # Title
        titleSurf = self.titleFont.render("PAUSED", True, (240, 245, 250))
        titleRect = titleSurf.get_rect(center=(rect.centerx, rect.y + 26))
        screen.blit(titleSurf, titleRect)

        # Buttons
        for b in self.mainButtons:
            b.draw(screen, self.btnFont)

        # Footer hint
        hintSurf = self.hintFont.render("[ESC] / [ENTER] Resume", True, (130, 155, 180))
        screen.blit(hintSurf, hintSurf.get_rect(center=(rect.centerx, rect.bottom - 16)))

    def _drawConfirmRestart(self, screen):
        rect = self.restartPanelRect
        pygame.draw.rect(screen, (18, 25, 36), rect, border_radius=8)
        pygame.draw.rect(screen, (220, 160, 60), rect, width=2, border_radius=8)

        # Header accent bar
        pygame.draw.rect(screen, (40, 32, 24), (rect.x + 2, rect.y + 2, rect.w - 4, 46),
                         border_top_left_radius=7, border_top_right_radius=7)
        pygame.draw.line(screen, (220, 160, 60), (rect.x, rect.y + 48), (rect.right, rect.y + 48), 2)

        # Title
        titleSurf = self.subTitleFont.render("RESTART MISSION?", True, (255, 210, 80))
        screen.blit(titleSurf, titleSurf.get_rect(center=(rect.centerx, rect.y + 25)))

        # Message
        msgSurf = self.bodyFont.render("Are you sure, you will lose all progress", True, (230, 240, 250))
        screen.blit(msgSurf, msgSurf.get_rect(center=(rect.centerx, rect.y + 95)))

        # Buttons
        self.restartYesBtn.draw(screen, self.btnFont)
        self.restartNoBtn.draw(screen, self.btnFont)

    def _drawConfirmMenu(self, screen):
        rect = self.menuPanelRect
        pygame.draw.rect(screen, (18, 25, 36), rect, border_radius=8)
        pygame.draw.rect(screen, (220, 160, 60), rect, width=2, border_radius=8)

        # Header accent bar
        pygame.draw.rect(screen, (40, 32, 24), (rect.x + 2, rect.y + 2, rect.w - 4, 46),
                         border_top_left_radius=7, border_top_right_radius=7)
        pygame.draw.line(screen, (220, 160, 60), (rect.x, rect.y + 48), (rect.right, rect.y + 48), 2)

        # Title
        titleSurf = self.subTitleFont.render("RETURN TO MAIN MENU?", True, (255, 210, 80))
        screen.blit(titleSurf, titleSurf.get_rect(center=(rect.centerx, rect.y + 25)))

        # Multi-line message
        line1 = self.bodyFont.render("This is an arcade style game.", True, (230, 240, 250))
        line2 = self.bodyFont.render("Going to the Main Menu will have you lose progress.", True, (230, 240, 250))
        line3 = self.bodyFont.render("Are you sure?", True, (255, 200, 80))

        screen.blit(line1, line1.get_rect(center=(rect.centerx, rect.y + 82)))
        screen.blit(line2, line2.get_rect(center=(rect.centerx, rect.y + 110)))
        screen.blit(line3, line3.get_rect(center=(rect.centerx, rect.y + 138)))

        # Buttons
        self.menuYesBtn.draw(screen, self.btnFont)
        self.menuNoBtn.draw(screen, self.btnFont)
