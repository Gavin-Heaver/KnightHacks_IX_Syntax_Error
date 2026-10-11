# ui/hud.py -- Cyberpunk telemetry HUD with dynamic enemy tracking and tactical CPU health bar.
import config
import pygame
from game import gameState

class HUD:

    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 18, bold=True)
        self.smallFont = pygame.font.SysFont("consolas", 14, bold=True)
        self.enemyFont = pygame.font.SysFont("consolas", 13, bold=True)
        self.badgeFont = pygame.font.SysFont("consolas", 16, bold=True)

        self.enemySpecs = {
            "bug": {
                "name": "Bug",
                "color": (255, 85, 85),
                "shape": "circle",
            },
            "injection": {
                "name": "Injection",
                "color": (255, 75, 210),
                "shape": "diamond",
            },
            "memoryLeak": {
                "name": "Memory Leak",
                "color": (70, 235, 170),
                "shape": "amoeba",
            },
            "zeroDay": {
                "name": "Zero Day",
                "color": (255, 220, 70),
                "shape": "ring",
            },
        }

    def _drawSymbol(self, screen, shape, color, cx, cy):
        """Draws the enemy's in-game tactical symbol at (cx, cy)."""
        if shape == "circle":
            # Bug: classic red circle with darker core
            pygame.draw.circle(screen, color, (cx, cy), 6)
            pygame.draw.circle(screen, (130, 25, 25), (cx, cy), 2)
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
            pygame.draw.circle(screen, (20, 95, 65), (cx, cy), 3)
        elif shape == "ring":
            # Zero Day: cloaked gold wireframe ring with center point
            pygame.draw.circle(screen, color, (cx, cy), 6, width=1)
            pygame.draw.circle(screen, color, (cx, cy), 1)

    def draw(self, screen, gameState, enemies=None):
        barHeight = 44

        # 1. Deep cipher obsidian banner background
        pygame.draw.rect(screen, (10, 16, 24), (0, 0, config.SCREEN_W, barHeight))

        # Cyber border divider line with neon bottom highlight
        pygame.draw.line(screen, (40, 115, 80), (0, barHeight - 1), (config.SCREEN_W, barHeight - 1), 1)
        pygame.draw.line(screen, (65, 205, 145), (0, barHeight), (config.SCREEN_W, barHeight), 1)

        # 2. Byte Tracking (Cyber Gold Badge)
        bytePill = pygame.Rect(16, 8, 195, 28)
        pygame.draw.rect(screen, (14, 24, 34), bytePill, border_radius=5)
        pygame.draw.rect(screen, (45, 120, 85), bytePill, width=1, border_radius=5)

        bytesText = f"BYTES: {gameState.bytes} B"
        bytesSurf = self.badgeFont.render(bytesText, True, (255, 205, 75))
        screen.blit(bytesSurf, bytesSurf.get_rect(center=bytePill.center))

        # 3. CPU Health Bar (Cyber Housing from x=225 to x=695)
        barW, barH = 470, 22
        barX = 225
        barY = 11

        # Housing base & border with cyber bevels
        pygame.draw.rect(screen, (12, 18, 25), (barX, barY, barW, barH), border_radius=4)
        pygame.draw.rect(screen, (45, 125, 85), (barX, barY, barW, barH), width=1, border_radius=4)

        # Dynamic Health Bar Fill
        hpPct = max(0.0, gameState.cpuHp / gameState.cpuMaxHp)
        if hpPct > 0.5:
            hpColor = (65, 225, 125)    # Matrix green
            coreColor = (160, 255, 195)
        elif hpPct > 0.25:
            hpColor = (245, 190, 50)   # Caution gold
            coreColor = (255, 235, 140)
        else:
            hpColor = (255, 65, 75)    # Alert crimson
            coreColor = (255, 160, 170)

        fillW = int(barW * hpPct)
        if fillW > 0:
            pygame.draw.rect(screen, hpColor, (barX, barY, fillW, barH), border_radius=4)
            # Glowing high-energy core line inside the health bar
            if fillW > 8:
                midY = barY + barH // 2
                pygame.draw.line(screen, coreColor, (barX + 3, midY), (barX + fillW - 3, midY), 2)

        # Health Bar Centered Label with Soft Contrast Backing Pill
        hpStr = f"CPU CORE: {int(gameState.cpuHp)}/{int(gameState.cpuMaxHp)}"
        hpLabel = self.smallFont.render(hpStr, True, (240, 250, 255))
        labelCenter = (barX + barW // 2, barY + barH // 2)
        lRect = hpLabel.get_rect(center=labelCenter)

        labelBacking = pygame.Surface((lRect.width + 14, lRect.height + 4), pygame.SRCALPHA)
        labelBacking.fill((8, 14, 20, 190))
        screen.blit(labelBacking, labelBacking.get_rect(center=labelCenter))
        screen.blit(hpLabel, lRect)

        # 4. Wave Counter (Cyber Cyan Badge at top right)
        waveX = config.SCREEN_W - 145
        wavePill = pygame.Rect(waveX, 8, 130, 28)
        pygame.draw.rect(screen, (14, 24, 34), wavePill, border_radius=5)
        pygame.draw.rect(screen, (40, 130, 165), wavePill, width=1, border_radius=5)

        waveText = f"// WAVE {gameState.wave}"
        waveSurf = self.badgeFont.render(waveText, True, (115, 225, 255))
        screen.blit(waveSurf, waveSurf.get_rect(center=wavePill.center))

        # 5. Enemy List (Between CPU bar and Wave badge)
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

        order = ["bug", "injection", "memoryLeak", "zeroDay"]
        activeEnemies = [t for t in order if t in gameState.encounteredEnemies and t in self.enemySpecs]

        zoneLeft = barX + barW + 16
        zoneRight = waveX - 16
        zoneW = zoneRight - zoneLeft

        renderedItems = []
        totalW = 0
        gap = 10
        for t in activeEnemies:
            spec = self.enemySpecs[t]
            textSurf = self.enemyFont.render(f": {spec['name']}", True, (215, 235, 245))
            # pill width = left padding(6) + symbol(14) + space(2) + text + right padding(6)
            pillW = 6 + 14 + 2 + textSurf.get_width() + 6
            pillH = 26
            renderedItems.append((spec, textSurf, pillW, pillH))
            totalW += pillW

        if renderedItems:
            totalW += gap * (len(renderedItems) - 1)
            curX = zoneLeft + max(0, (zoneW - totalW) // 2)
            centerY = barHeight // 2

            for spec, textSurf, pillW, pillH in renderedItems:
                badgeRect = pygame.Rect(curX, centerY - pillH // 2, pillW, pillH)
                pygame.draw.rect(screen, (14, 22, 32), badgeRect, border_radius=4)
                pygame.draw.rect(screen, (38, 85, 65), badgeRect, width=1, border_radius=4)

                symCx = curX + 13
                symCy = centerY
                self._drawSymbol(screen, spec["shape"], spec["color"], symCx, symCy)
                textRect = textSurf.get_rect(midleft=(curX + 22, centerY))
                screen.blit(textSurf, textRect)
                curX += pillW + gap