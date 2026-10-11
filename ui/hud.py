import config
import pygame
from game import gameState

class HUD:

    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.smallFont = pygame.font.SysFont("consolas", 15, bold=True)
        self.enemyFont = pygame.font.SysFont("consolas", 14, bold=True)

        self.enemySpecs = {
            "bug": {
                "name": "Bug",
                "color": (255, 80, 80),
                "shape": "circle",
            },
            "injection": {
                "name": "Injection",
                "color": (255, 60, 200),
                "shape": "diamond",
            },
            "memoryLeak": {
                "name": "Memory Leak",
                "color": (60, 220, 160),
                "shape": "amoeba",
            },
            "zeroDay": {
                "name": "Zero Day",
                "color": (255, 215, 60),
                "shape": "ring",
            },
        }

    def _drawSymbol(self, screen, shape, color, cx, cy):
        """Draws the enemy's in-game tactical symbol at (cx, cy)."""
        if shape == "circle":
            # Bug: classic red circle with darker core
            pygame.draw.circle(screen, color, (cx, cy), 6)
            pygame.draw.circle(screen, (140, 30, 30), (cx, cy), 2)
        elif shape == "diamond":
            # Injection: sharp neon pink diamond
            pts = [
                (cx, cy - 7),
                (cx + 6, cy),
                (cx, cy + 7),
                (cx - 6, cy),
            ]
            pygame.draw.polygon(screen, color, pts)
        elif shape == "amoeba":
            # Memory Leak: amoeba circle with dark cellular nucleus
            pygame.draw.circle(screen, color, (cx, cy), 6)
            pygame.draw.circle(screen, (25, 110, 75), (cx, cy), 3)
        elif shape == "ring":
            # Zero Day: cloaked gold wireframe ring with center point
            pygame.draw.circle(screen, color, (cx, cy), 6, width=1)
            pygame.draw.circle(screen, color, (cx, cy), 1)

    def draw(self, screen, gameState, enemies=None):
        # Banner
        barHeight = 44
        pygame.draw.rect(screen, (16, 24, 34), (0, 0, config.SCREEN_W, barHeight))
        pygame.draw.line(screen, (40, 60, 85), (0, barHeight), (config.SCREEN_W, barHeight), 2)

        # Byte Tracking (leaves room for up to 6 digits, e.g. 999999)
        bytesText = f"BYTES (B): {gameState.bytes}"
        bytesSurf = self.font.render(bytesText, True, (255, 200, 80))
        screen.blit(bytesSurf, (20, 12))

        # CPU Health bar (470px long, barX=225, ends at x=695)
        barW, barH = 470, 22
        barX = 225
        barY = 11

        pygame.draw.rect(screen, (40, 20, 25), (barX, barY, barW, barH), border_radius=4)

        # Dynamic Health bar
        hpPct = max(0.0, gameState.cpuHp / gameState.cpuMaxHp)
        if hpPct > 0.5:
            hpColor = (70, 200, 120)    # Good Health: Green
        elif hpPct > 0.25:
            hpColor = (240, 190, 60)   # Caution Health: Yellow
        else:
            hpColor = (255, 70, 70)    # Danger Health: Red

        if hpPct > 0:
            pygame.draw.rect(screen, hpColor, (barX, barY, int(barW * hpPct), barH), border_radius=4)

        # Health Bar border and centered text
        pygame.draw.rect(screen, (60, 80, 105), (barX, barY, barW, barH), width=1, border_radius=4)
        hpLabel = self.smallFont.render(f"CPU: {int(gameState.cpuHp)}/{int(gameState.cpuMaxHp)}", True, (240, 245, 250))
        labelRect = hpLabel.get_rect(center=(barX + barW // 2, barY + barH // 2))
        screen.blit(hpLabel, labelRect)

        # Wave Count Display at top right
        waveText = f"WAVE {gameState.wave}"
        waveSurf = self.font.render(waveText, True, (90, 160, 225))
        waveX = config.SCREEN_W - 130
        screen.blit(waveSurf, (waveX, 12))

        # Update encountered enemies: unlocks at wave thresholds or when spawned
        if not hasattr(gameState, "encounteredEnemies"):
            gameState.encounteredEnemies = {"bug"}
        if gameState.wave >= 1:
            gameState.encounteredEnemies.add("bug")
        if gameState.wave >= 3:
            gameState.encounteredEnemies.add("injection")
            gameState.encounteredEnemies.add("memoryLeak")
        if gameState.wave >= 4:
            gameState.encounteredEnemies.add("zeroDay")

        if enemies:
            for e in enemies:
                if getattr(e, "alive", True) and e.type in self.enemySpecs:
                    gameState.encounteredEnemies.add(e.type)

        # Filter in tactical progression order
        order = ["bug", "injection", "memoryLeak", "zeroDay"]
        activeEnemies = [t for t in order if t in gameState.encounteredEnemies and t in self.enemySpecs]

        # Render Enemy List between CPU bar right edge and Wave counter
        zoneLeft = barX + barW + 16
        zoneRight = waveX - 16
        zoneW = zoneRight - zoneLeft

        renderedItems = []
        totalW = 0
        gap = 14
        for t in activeEnemies:
            spec = self.enemySpecs[t]
            textSurf = self.enemyFont.render(f": {spec['name']}", True, (215, 230, 245))
            # item width = symbol width (14) + spacing (3) + text width
            itemW = 14 + 3 + textSurf.get_width()
            renderedItems.append((spec, textSurf, itemW))
            totalW += itemW

        if renderedItems:
            totalW += gap * (len(renderedItems) - 1)
            # Center the list horizontally in the available gap
            curX = zoneLeft + max(0, (zoneW - totalW) // 2)
            centerY = barHeight // 2

            for spec, textSurf, itemW in renderedItems:
                symCx = curX + 7
                symCy = centerY
                self._drawSymbol(screen, spec["shape"], spec["color"], symCx, symCy)
                textRect = textSurf.get_rect(midleft=(curX + 17, centerY))
                screen.blit(textSurf, textRect)
                curX += itemW + gap