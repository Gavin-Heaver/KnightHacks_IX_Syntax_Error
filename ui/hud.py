import config
import pygame
from game import gameState

class HUD:

    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.smallFont = pygame.font.SysFont("consolas", 15, bold=True)

    def draw(self, screen, gameState):
       #Banner
        barHeight = 44
        pygame.draw.rect(screen, (16, 24, 34), (0,0, config.SCREEN_W, barHeight))
        pygame.draw.line(screen, (40, 60, 85), (0, barHeight), (config.SCREEN_W, barHeight), 2)

        #Byte Tracking
        bytesText = f"BYTES: {gameState.bytes}"
        bytesSurf = self.font.render(bytesText, True, (255, 200, 80))
        screen.blit(bytesSurf, (24, 12))

        #Health bar location
        barW, barH = 160, 20
        barX = config.SCREEN_W // 2 - barW // 2
        barY = 12

        pygame.draw.rect(screen, (40, 20, 25), (barX, barY, barW, barH), border_radius=4)

        #Dynamic Health bar
        hpPct = max(0.0, gameState.cpuHp / gameState.cpuMaxHp)
        if hpPct > 0.5:
            hpColor = (70, 200, 120)    # Good Health: Green
        elif hpPct > 0.25:
            hpColor = (240, 190, 60)   # Caution Health: Yellow
        else:
            hpColor = (255, 70, 70)   # Danger Health: Red

        if hpPct > 0:
            pygame.draw.rect(screen, hpColor, (barX, barY, int(barW * hpPct), barH), border_radius=4)

        #Health Bar border
        pygame.draw.rect(screen, (60, 80, 105), (barX, barY, barW, barH), width=1, border_radius=4)
        hpLabel = self.smallFont.render(f"CPU: {int(gameState.cpuHp)}/{int(gameState.cpuMaxHp)}", True, (240, 245, 250))
        labelRect = hpLabel.get_rect(center=(barX + barW // 2, barY + barH // 2))
        screen.blit(hpLabel, labelRect)

        #Wave Count Display
        waveText = f"WAVE {gameState.wave}"
        waveSurf = self.font.render(waveText, True, (90, 160,225))
        screen.blit(waveSurf, (config.SCREEN_W - 320, 12))

        #Status based on current phase
        if gameState.phase == config.PHASE_BUILD:
            statusSurf = self.smallFont.render("[ENTER] Start Wave", True, (70, 200, 120))
        elif gameState.phase == config.PHASE_WAVE:
            statusSurf = self.smallFont.render("DEFENDING CPU...", True, (255, 120, 80))
        elif gameState.phase == config.PHASE_GAME_OVER:
            statusSurf = self.font.render("GAME OVER", True, (255, 70, 70))
        else:
            statusSurf = None

        if statusSurf:
            screen.blit(statusSurf, (config.SCREEN_W - 200, 14))