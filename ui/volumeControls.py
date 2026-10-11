# ui/volumeControls.py -- Cyberpunk themed audio volume control widget for Main Menu & Pause Menu.
import pygame
from game.audio import audioManager


class VolumeSlider:
    def __init__(self, x, y, width, height, label, getValFunc, setValFunc):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.getVal = getValFunc
        self.setVal = setValFunc
        self.isDragging = False

        # Stepper buttons [-] and [+]
        btnSize = 34
        self.minusRect = pygame.Rect(x, y + 26, btnSize, btnSize)
        self.plusRect = pygame.Rect(x + width - btnSize, y + 26, btnSize, btnSize)

        # Track rect sits between [-] and [+]
        trackX = x + btnSize + 14
        trackW = width - (btnSize * 2) - 28
        trackH = 20
        trackY = y + 26 + (btnSize - trackH) // 2
        self.trackRect = pygame.Rect(trackX, trackY, trackW, trackH)

        self.minusHovered = False
        self.plusHovered = False
        self.trackHovered = False

    def handleEvent(self, event):
        """Processes mouse clicks and dragging for volume slider."""
        if event.type == pygame.MOUSEMOTION:
            mpos = event.pos
            self.minusHovered = self.minusRect.collidepoint(mpos)
            self.plusHovered = self.plusRect.collidepoint(mpos)
            self.trackHovered = self.trackRect.collidepoint(mpos)

            if self.isDragging:
                self._updateFromMouseX(mpos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mpos = event.pos
            if self.minusRect.collidepoint(mpos):
                cur = self.getVal()
                self.setVal(round(max(0.0, cur - 0.1), 2))
                audioManager.sfx("select")
                return True
            elif self.plusRect.collidepoint(mpos):
                cur = self.getVal()
                self.setVal(round(min(1.0, cur + 0.1), 2))
                audioManager.sfx("select")
                return True
            elif self.trackRect.collidepoint(mpos):
                self.isDragging = True
                self._updateFromMouseX(mpos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.isDragging:
                self.isDragging = False
                audioManager.sfx("select")   # preview the new level once the drag ends
                return True

        return False

    def _updateFromMouseX(self, mouseX):
        ratio = (mouseX - self.trackRect.x) / float(self.trackRect.width)
        ratio = max(0.0, min(1.0, ratio))
        self.setVal(round(ratio, 2))

    def draw(self, screen, labelFont, valFont, btnFont):
        val = self.getVal()
        pct = int(round(val * 100))

        # 1. Label and percentage badge
        lblSurf = labelFont.render(self.label, True, (140, 225, 245))
        screen.blit(lblSurf, (self.x, self.y))

        pctColor = (85, 250, 145) if not audioManager.isMuted else (150, 150, 150)
        pctText = f"{pct}%" if not audioManager.isMuted else f"{pct}% (MUTED)"
        pctSurf = valFont.render(pctText, True, pctColor)
        pctRect = pctSurf.get_rect(topright=(self.x + self.width, self.y))
        screen.blit(pctSurf, pctRect)

        # 2. Stepper Buttons: [-]
        mBg = (26, 62, 48) if self.minusHovered else (14, 26, 36)
        mBdr = (85, 250, 145) if self.minusHovered else (45, 135, 88)
        pygame.draw.rect(screen, mBg, self.minusRect, border_radius=5)
        pygame.draw.rect(screen, mBdr, self.minusRect, width=2, border_radius=5)
        mTxt = btnFont.render("-", True, (240, 255, 245))
        screen.blit(mTxt, mTxt.get_rect(center=self.minusRect.center))

        # 3. Stepper Buttons: [+]
        pBg = (26, 62, 48) if self.plusHovered else (14, 26, 36)
        pBdr = (85, 250, 145) if self.plusHovered else (45, 135, 88)
        pygame.draw.rect(screen, pBg, self.plusRect, border_radius=5)
        pygame.draw.rect(screen, pBdr, self.plusRect, width=2, border_radius=5)
        pTxt = btnFont.render("+", True, (240, 255, 245))
        screen.blit(pTxt, pTxt.get_rect(center=self.plusRect.center))

        # 4. Slider Track (dark cyber groove)
        tRect = self.trackRect
        pygame.draw.rect(screen, (10, 18, 26), tRect, border_radius=6)
        pygame.draw.rect(screen, (40, 95, 70), tRect, width=1, border_radius=6)

        # 5. Filled portion (illuminated emerald bar)
        fillWidth = int(tRect.width * val)
        if fillWidth > 0:
            fillRect = pygame.Rect(tRect.x, tRect.y, fillWidth, tRect.height)
            barColor = (45, 180, 95) if not audioManager.isMuted else (60, 80, 75)
            pygame.draw.rect(screen, barColor, fillRect, border_radius=6)

            # High-tech glowing core line in filled bar
            if fillWidth > 8 and not audioManager.isMuted:
                coreY = tRect.centery
                pygame.draw.line(screen, (130, 255, 180), (tRect.x + 4, coreY), (tRect.x + fillWidth - 4, coreY), 2)

        # 6. Glowing Thumb indicator
        thumbX = tRect.x + fillWidth
        thumbW, thumbH = 14, tRect.height + 10
        thumbRect = pygame.Rect(thumbX - thumbW // 2, tRect.centery - thumbH // 2, thumbW, thumbH)
        thumbBg = (85, 250, 145) if (self.isDragging or self.trackHovered) else (40, 175, 95)
        if audioManager.isMuted:
            thumbBg = (90, 110, 100)
        pygame.draw.rect(screen, thumbBg, thumbRect, border_radius=4)
        pygame.draw.rect(screen, (240, 255, 245), thumbRect, width=1, border_radius=4)


class VolumeModal:
    """Cyberpunk modal dialog for adjusting Music and Sound Effects volume."""
    def __init__(self, centerX, centerY, width=640, height=450, backText="BACK TO MENU"):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(centerX - width // 2, centerY - height // 2, width, height)
        self.backText = backText

        # Fonts
        self.titleFont = pygame.font.SysFont("consolas", 34, bold=True)
        self.subFont = pygame.font.SysFont("consolas", 17)
        self.labelFont = pygame.font.SysFont("consolas", 20, bold=True)
        self.valFont = pygame.font.SysFont("consolas", 20, bold=True)
        self.btnFont = pygame.font.SysFont("consolas", 22, bold=True)
        self.smallBtnFont = pygame.font.SysFont("consolas", 18, bold=True)

        # Sliders positioning
        sliderW = width - 100
        sliderX = self.rect.x + 50
        musicY = self.rect.y + 115
        sfxY = self.rect.y + 205

        self.musicSlider = VolumeSlider(
            sliderX, musicY, sliderW, 70,
            "MUSIC VOLUME (BGM)",
            audioManager.getMusicVolume,
            audioManager.setMusicVolume
        )

        self.sfxSlider = VolumeSlider(
            sliderX, sfxY, sliderW, 70,
            "SOUND EFFECTS (SFX)",
            audioManager.getSfxVolume,
            audioManager.setSfxVolume
        )

        # Mute toggle button
        muteBtnW, muteBtnH = 220, 38
        self.muteBtnRect = pygame.Rect(centerX - muteBtnW // 2, self.rect.y + 298, muteBtnW, muteBtnH)
        self.muteHovered = False

        # Back button
        backBtnW, backBtnH = 280, 46
        self.backBtnRect = pygame.Rect(centerX - backBtnW // 2, self.rect.bottom - 66, backBtnW, backBtnH)
        self.backHovered = False

    def handleEvent(self, event):
        """
        Handles volume slider drags, stepper clicks, mute toggle, and back button.
        Returns:
            "back" -> user wants to exit volume screen
            None   -> stays in volume screen
        """
        if event.type == pygame.MOUSEMOTION:
            mpos = event.pos
            self.muteHovered = self.muteBtnRect.collidepoint(mpos)
            self.backHovered = self.backBtnRect.collidepoint(mpos)
            self.musicSlider.handleEvent(event)
            self.sfxSlider.handleEvent(event)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mpos = event.pos
            if self.muteBtnRect.collidepoint(mpos):
                audioManager.toggleMute()
                audioManager.sfx("select")   # silent when muting, audible when unmuting
                return None
            elif self.backBtnRect.collidepoint(mpos):
                return "back"

            self.musicSlider.handleEvent(event)
            self.sfxSlider.handleEvent(event)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.musicSlider.handleEvent(event)
            self.sfxSlider.handleEvent(event)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

        return None

    def draw(self, screen):
        px, py, pw, ph = self.rect.x, self.rect.y, self.rect.w, self.rect.h

        # Frosted cyber glass background panel
        panelSurf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panelSurf.fill((10, 18, 26, 240))
        screen.blit(panelSurf, (px, py))
        pygame.draw.rect(screen, (50, 150, 95), (px, py, pw, ph), 2, border_radius=8)

        # High-voltage neon corner accents
        cLen = 18
        accCol = (80, 245, 140)
        pygame.draw.line(screen, accCol, (px, py), (px + cLen, py), 3)
        pygame.draw.line(screen, accCol, (px, py), (px, py + cLen), 3)
        pygame.draw.line(screen, accCol, (px + pw, py), (px + pw - cLen, py), 3)
        pygame.draw.line(screen, accCol, (px + pw, py), (px + pw, py + cLen), 3)
        pygame.draw.line(screen, accCol, (px, py + ph), (px + cLen, py + ph), 3)
        pygame.draw.line(screen, accCol, (px, py + ph), (px, py + ph - cLen), 3)
        pygame.draw.line(screen, accCol, (px + pw, py + ph), (px + pw - cLen, py + ph), 3)
        pygame.draw.line(screen, accCol, (px + pw, py + ph), (px + pw, py + ph - cLen), 3)

        # Title Glow & Text
        titleText = "AUDIO CONFIGURATION"
        tSurf = self.titleFont.render(titleText, True, (105, 255, 160))
        gSurf = self.titleFont.render(titleText, True, (20, 110, 65))
        tRect = tSurf.get_rect(center=(self.rect.centerx, py + 38))
        screen.blit(gSurf, tRect.move(2, 2))
        screen.blit(tSurf, tRect)

        subSurf = self.subFont.render("// MASTER AUDIO SUBSYSTEM & SOUND LEVELS", True, (140, 225, 245))
        screen.blit(subSurf, subSurf.get_rect(center=(self.rect.centerx, py + 68)))

        # Header horizontal divider line
        pygame.draw.line(screen, (40, 115, 80), (px + 30, py + 86), (px + pw - 30, py + 86), 1)

        # Sliders
        self.musicSlider.draw(screen, self.labelFont, self.valFont, self.btnFont)
        self.sfxSlider.draw(screen, self.labelFont, self.valFont, self.btnFont)

        # Mute toggle button
        mBg = (40, 22, 28) if audioManager.isMuted else ((26, 62, 48) if self.muteHovered else (14, 26, 36))
        mBdr = (240, 80, 95) if audioManager.isMuted else ((85, 250, 145) if self.muteHovered else (45, 135, 88))
        mTxtCol = (255, 140, 150) if audioManager.isMuted else ((255, 255, 255) if self.muteHovered else (195, 248, 220))
        mText = "MUTE: ACTIVE (OFF)" if audioManager.isMuted else "MUTE: DISABLED (ON)"

        pygame.draw.rect(screen, mBg, self.muteBtnRect, border_radius=6)
        pygame.draw.rect(screen, mBdr, self.muteBtnRect, width=2, border_radius=6)
        muteTextSurf = self.smallBtnFont.render(mText, True, mTxtCol)
        screen.blit(muteTextSurf, muteTextSurf.get_rect(center=self.muteBtnRect.center))

        # Back button
        bBg = (26, 62, 48) if self.backHovered else (14, 26, 36)
        bBdr = (85, 250, 145) if self.backHovered else (45, 135, 88)
        bTxtCol = (255, 255, 255) if self.backHovered else (195, 248, 220)
        bText = f"► {self.backText}" if self.backHovered else self.backText

        pygame.draw.rect(screen, bBg, self.backBtnRect, border_radius=6)
        pygame.draw.rect(screen, bBdr, self.backBtnRect, width=2, border_radius=6)
        bSurf = self.btnFont.render(bText, True, bTxtCol)
        screen.blit(bSurf, bSurf.get_rect(center=self.backBtnRect.center))

