#Syntax Error

#Gavin Heaver and Tadhg Hallahan
#KnightHacks_IX

#YOU WILL BE REWARDED FOR YOU PATIENCE AND UNDERSTANDING~ THANK YOU PANDA EXPRESS
#YOU ARE ADMIRED FOR YOUR ADVENTUROUS SPIRIT~ THANK YOU PANDA EXPRESS x2

#imports
import os
import sys

# Project directory
projectDir = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(projectDir):
    os.chdir(projectDir)
    if projectDir not in sys.path:
        sys.path.insert(0, projectDir)

import pygame
import pygame_gui
import ast                     # script checks (unlocks, blocked imports)
import heapq                   # Dijkstra
import math, random, time      # math, random, timing
from collections import deque  # BFS helpers, event queues
from dataclasses import dataclass, field
from enum import Enum, auto    # game phases, enemy types
import json                    # wave definition, (optional)

import config
from game.board import Board
from game import events
from entities.enemy import Enemy
from ui.debugOverlay import DebugOverlay
from game.gameState import GameState
from game.waves import WaveSpawner
from ai.costLayers import buildFields, buildOneField
from ai.pheromone import PheromoneMap

###DEBUG
from entities.tools import Debugger, Firewall, Antivirus, Turret
###DEBUG

from ui.shop import ShopPanel
from ui.menu import StartMenu, recordNewScore
from ui.hud import HUD
from ui.editor import CodeEditor
from ui.gameOver import GameOverTerminal
from ui.pauseMenu import PauseMenu
from game.audio import audioManager

#setup
try:
    import ctypes
    # Tells Windows this process has its own identity so the taskbar displays our custom icon instead of python.exe
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("knighthacks.syntaxerror.towerdefense.1.0")
except Exception:
    pass

random.seed(config.DEMO_SEED)   # deterministic demo (use only `random` for randomness)
pygame.init()

# Set window and taskbar icon
iconPath = os.path.join(projectDir, "assets", "pixil-frame-0-trans.png")
if not os.path.exists(iconPath):
    iconPath = os.path.join(projectDir, "assets", "pixil-frame-0.png")
if os.path.exists(iconPath):
    try:
        gameIcon = pygame.image.load(iconPath)
        pygame.display.set_icon(gameIcon)
    except Exception as e:
        print("Failed to set window icon:", e)

screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H), pygame.SCALED)
pygame.display.set_caption("Syntax Error: Code Tower Defense")

# Re-apply after set_mode to guarantee persistence across all SDL window managers
if 'gameIcon' in locals():
    pygame.display.set_icon(gameIcon)

def toggleFullscreen():
    """Toggles fullscreen mode smoothly while maintaining the 1280x720 scaled aspect ratio."""
    success = pygame.display.toggle_fullscreen()
    if not success:
        curr = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
        newFlags = pygame.SCALED if curr else (pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H), newFlags)

clock = pygame.time.Clock()
audioManager.startMusic()       # background soundtrack loops for the whole session
uiManager = pygame_gui.UIManager((config.SCREEN_W, config.SCREEN_H))
consolasPath = pygame.font.match_font("consolas")
if consolasPath:
    try:
        uiManager.add_font_paths("consolas", consolasPath)
        uiManager.preload_fonts([
            {"name": "consolas", "point_size": 14, "style": "bold"},
            {"name": "consolas", "point_size": 14, "style": "regular"},
            {"name": "consolas", "point_size": 14, "style": "italic"},
            {"name": "consolas", "point_size": 13, "style": "bold"},
            {"name": "consolas", "point_size": 13, "style": "regular"},
            {"name": "consolas", "point_size": 12, "style": "regular"},
        ])
    except Exception:
        pass
themePath = os.path.join(projectDir, "theme.json")
if os.path.exists(themePath):
    uiManager.get_theme().load_theme(themePath)
running = True

board = Board()

### Move to game/board.py
def onToolDestroyed(tool):
    board.remove(tool.x, tool.y)

events.subscribe("toolDestroyed", onToolDestroyed)
### Move to game/board.py

def onEnemyKilled(enemy):
    if enemy.type != "memoryLeak":
        return
    else:
        count = math.ceil(config.MEMORY_LEAK_SPLIT_COUNT + random.uniform(-config.ML_SPLIT_VARIANCE, config.ML_SPLIT_VARIANCE))

        for _ in range(count):
            x = enemy.x + random.uniform(-2, 2)
            y = enemy.y + random.uniform(-2, 2)
            if not Enemy._walkable(board, x, y):
                x, y = enemy.x, enemy.y
            enemies.append(Enemy("bug", x, y))

events.subscribe("enemyKilled", onEnemyKilled)


phase = config.PHASE_MENU
shopPanel = ShopPanel(uiManager)
startMenu = StartMenu(config.SCREEN_W, config.SCREEN_H)
gameState = GameState()
codeEditor = CodeEditor(uiManager)
hud = HUD()
gameOverTerminal = GameOverTerminal(config.SCREEN_W, config.SCREEN_H)
pauseMenu = PauseMenu(config.SCREEN_W, config.SCREEN_H)
debugOverlay = DebugOverlay()
enemies = []                    # game.enemies: list[Enemy]
projectiles = []
selectedTool = None
waveSpawner = WaveSpawner()
waveCountdown = None            # seconds until the next wave auto-starts; None = waiting for Enter
paused = False
scoreRecorded = False
bannerFont = pygame.font.SysFont("consolas", 28, bold=True)
pauseFont = pygame.font.SysFont("consolas", 64, bold=True)
hintFont = pygame.font.SysFont("consolas", 20)

pheromones = PheromoneMap(board.width, board.height)   # fear left by dead enemies
aiTimer = 0.0                                          # counts up to AI_TICK_SECONDS
fields = buildFields(board, pheromones.grid)           # one flow field per enemy type
fieldJobs = []                                         # fields still to refresh after an AI tick (one per frame)


def beginWave():
    global phase
    waveSpawner.start(gameState.wave)
    phase = config.PHASE_WAVE


def resetGame():
    global board, gameState, enemies, projectiles, waveSpawner
    global waveCountdown, selectedTool, paused, phase, fields, fieldJobs, pheromones, aiTimer, scoreRecorded

    scoreRecorded = False

    # the old GameState / PheromoneMap are still subscribed to events -- clear them first
    events.clearAll()
    events.subscribe("toolDestroyed", onToolDestroyed)

    random.seed(config.DEMO_SEED)
    board = Board()
    gameState = GameState()                              # re-subscribes itself
    enemies = []
    projectiles = []
    waveSpawner = WaveSpawner()
    waveCountdown = None
    selectedTool = None
    codeEditor.close()
    pheromones = PheromoneMap(board.width, board.height)  # re-subscribes itself
    aiTimer = 0.0
    fields = buildFields(board, pheromones.grid)
    fieldJobs = []
    paused = False
    phase = config.PHASE_MENU
    events.subscribe("enemyKilled", onEnemyKilled)


def tileRect(x, y):
    return pygame.Rect(config.BOARD_X + x * config.TILE, config.BOARD_Y + y * config.TILE,
                       config.TILE, config.TILE)


def drawBoard():
    mx, my = pygame.mouse.get_pos()
    hoverX = (mx - config.BOARD_X) // config.TILE
    hoverY = (my - config.BOARD_Y) // config.TILE

    if board.inBounds(hoverX, hoverY) and phase != config.PHASE_MENU:
        centerPixelX = config.BOARD_X + (hoverX + 0.5) * config.TILE
        centerPixelY = config.BOARD_Y + (hoverY + 0.5) * config.TILE

        prevRect = tileRect(hoverX, hoverY)
        prevSurf = pygame.Surface((prevRect.width, prevRect.height), pygame.SRCALPHA)

        if board.isBuildable(hoverX, hoverY):
            previewColor = (85, 250, 145)
            prevSurf.fill((65, 240, 135, 45))
            screen.blit(prevSurf, prevRect.topleft)
            pygame.draw.rect(screen, previewColor, prevRect, width=2)
            
            toolRange = config.TOOL_STATS[shopPanel.selectedToolType]["range"]
            if toolRange > 0:
                radius = int(toolRange * config.TILE)
                pygame.draw.circle(screen, previewColor, (int(centerPixelX), int(centerPixelY)), radius, width=1)
        else:
            previewColor = (255, 75, 85)
            prevSurf.fill((255, 55, 65, 45))
            screen.blit(prevSurf, prevRect.topleft)
            pygame.draw.rect(screen, previewColor, prevRect, width=2)

    # Board outer boundary frame with wireframe emerald border & neon corner brackets
    bx, by = config.BOARD_X, config.BOARD_Y
    bw, bh = config.BOARD_PX_W, config.BOARD_PX_H
    pygame.draw.rect(screen, (35, 110, 75), (bx - 1, by - 1, bw + 2, bh + 2), 2)

    cLen = 14
    accCol = (80, 245, 140)
    pygame.draw.line(screen, accCol, (bx - 1, by - 1), (bx - 1 + cLen, by - 1), 2)
    pygame.draw.line(screen, accCol, (bx - 1, by - 1), (bx - 1, by - 1 + cLen), 2)
    pygame.draw.line(screen, accCol, (bx + bw + 1, by - 1), (bx + bw + 1 - cLen, by - 1), 2)
    pygame.draw.line(screen, accCol, (bx + bw + 1, by - 1), (bx + bw + 1, by - 1 + cLen), 2)
    pygame.draw.line(screen, accCol, (bx - 1, by + bh + 1), (bx - 1 + cLen, by + bh + 1), 2)
    pygame.draw.line(screen, accCol, (bx - 1, by + bh + 1), (bx - 1, by + bh + 1 - cLen), 2)
    pygame.draw.line(screen, accCol, (bx + bw + 1, by + bh + 1), (bx + bw + 1 - cLen, by + bh + 1), 2)
    pygame.draw.line(screen, accCol, (bx + bw + 1, by + bh + 1), (bx + bw + 1, by + bh + 1 - cLen), 2)

    for y in range(board.height):
        for x in range(board.width):
            pygame.draw.rect(screen, config.COLOR_GRID, tileRect(x, y), 1)

    # Microprocessor CPU socket with silicon core and gold contact pins
    for (x, y) in board.cpuTiles:
        cRect = tileRect(x, y).inflate(-2, -2)
        pygame.draw.rect(screen, (16, 50, 32), cRect)
        pygame.draw.rect(screen, (65, 220, 125), cRect, 1)
        innerCore = cRect.inflate(-6, -6)
        pygame.draw.rect(screen, (30, 110, 68), innerCore)
        # Corner gold circuit contact pins
        pygame.draw.circle(screen, (245, 210, 80), (cRect.left + 3, cRect.top + 3), 1)
        pygame.draw.circle(screen, (245, 210, 80), (cRect.right - 3, cRect.top + 3), 1)
        pygame.draw.circle(screen, (245, 210, 80), (cRect.left + 3, cRect.bottom - 3), 1)
        pygame.draw.circle(screen, (245, 210, 80), (cRect.right - 3, cRect.bottom - 3), 1)

    # Firewall plasma links between aligned posts within range
    damTiles = board.damagingPlasmaTiles
    for link in board.plasmaLinks:
        (x1, y1), (x2, y2) = link[0], link[1]
        isDamaging = link[2] if len(link) > 2 else False
        p1 = (int(config.BOARD_X + (x1 + 0.5) * config.TILE), int(config.BOARD_Y + (y1 + 0.5) * config.TILE))
        p2 = (int(config.BOARD_X + (x2 + 0.5) * config.TILE), int(config.BOARD_Y + (y2 + 0.5) * config.TILE))
        if isDamaging:
            # Electric blue/violet high-voltage damaging plasma
            pygame.draw.line(screen, (80, 180, 255), p1, p2, 8)
            pygame.draw.line(screen, (220, 240, 255), p1, p2, 2)
        else:
            # Standard orange plasma laser
            pygame.draw.line(screen, (255, 120, 30), p1, p2, 6)
            pygame.draw.line(screen, (255, 230, 160), p1, p2, 2)

    # Plasma field nodes on intermediate tiles
    for (px, py) in board.plasmaTiles:
        cx = int(config.BOARD_X + (px + 0.5) * config.TILE)
        cy = int(config.BOARD_Y + (py + 0.5) * config.TILE)
        if (px, py) in damTiles:
            pygame.draw.circle(screen, (120, 220, 255), (cx, cy), 4)
        else:
            pygame.draw.circle(screen, (255, 180, 70), (cx, cy), 3)

    for tool in board.allTools():
        tRect = tileRect(tool.x, tool.y).inflate(-4, -4)
        isCorrupted = getattr(tool, "corrupted", False)

        if isCorrupted:
            pygame.draw.rect(screen, (55, 16, 22), tRect)
            pygame.draw.rect(screen, (255, 55, 65), tRect, width=2)
            m = 5
            pygame.draw.line(screen, (255, 75, 75), (tRect.left + m, tRect.top + m), (tRect.right - m, tRect.bottom - m), 2)
            pygame.draw.line(screen, (255, 75, 75), (tRect.left + m, tRect.bottom - m), (tRect.right - m, tRect.top + m), 2)
        else:
            if tool.kind in ("debugger", "turret"):
                pygame.draw.rect(screen, (18, 45, 75), tRect)
                pygame.draw.rect(screen, (75, 175, 255), tRect, width=2)
                core = tRect.inflate(-8, -8)
                pygame.draw.rect(screen, (160, 230, 255), core)
            elif tool.kind == "firewall":
                pygame.draw.rect(screen, (60, 28, 12), tRect)
                pygame.draw.rect(screen, (255, 130, 35), tRect, width=2)
                core = tRect.inflate(-8, -8)
                pygame.draw.rect(screen, (255, 215, 120), core)
            elif tool.kind == "antivirus":
                pygame.draw.rect(screen, (45, 20, 65), tRect)
                pygame.draw.rect(screen, (185, 100, 255), tRect, width=2)
                core = tRect.inflate(-8, -8)
                pygame.draw.rect(screen, (235, 185, 255), core)
            else:
                color = config.TOOL_COLORS.get(tool.kind, config.COLOR_TOOL)
                pygame.draw.rect(screen, color, tRect)

        # Tier 3 Debugger (formerly Turret) constant laser beam
        if tool.kind in ("debugger", "turret") and getattr(tool, "tier", 0) >= 2:
            lt = getattr(tool, "laserTarget", None)
            isLtAlive = getattr(lt, "alive", True) if hasattr(lt, "alive") else (getattr(lt, "hp", 1) > 0)
            if lt is not None and isLtAlive:
                tcx = int(config.BOARD_X + (tool.x + 0.5) * config.TILE)
                tcy = int(config.BOARD_Y + (tool.y + 0.5) * config.TILE)
                tx = int(config.BOARD_X + ((lt.x + 0.5) if hasattr(lt, "kind") else lt.x) * config.TILE)
                ty = int(config.BOARD_Y + ((lt.y + 0.5) if hasattr(lt, "kind") else lt.y) * config.TILE)
                if isCorrupted:
                    pygame.draw.line(screen, (255, 40, 40), (tcx, tcy), (tx, ty), 5)
                    pygame.draw.line(screen, (255, 200, 200), (tcx, tcy), (tx, ty), 2)
                    pygame.draw.circle(screen, (255, 220, 220), (tx, ty), 4)
                else:
                    pygame.draw.line(screen, (70, 170, 255), (tcx, tcy), (tx, ty), 5)
                    pygame.draw.line(screen, (220, 250, 255), (tcx, tcy), (tx, ty), 2)
                    pygame.draw.circle(screen, (255, 255, 255), (tx, ty), 4)

        # Antivirus (formerly Debugger) radar ring, rotating scan sweep, and cyber tether
        if tool.kind == "antivirus":
            dcx = int(config.BOARD_X + (tool.x + 0.5) * config.TILE)
            dcy = int(config.BOARD_Y + (tool.y + 0.5) * config.TILE)
            dr = int(tool.range * config.TILE)


            # Glowing transparent sphere of influence
            auraSurf = pygame.Surface((dr * 2, dr * 2), pygame.SRCALPHA)
            if isCorrupted:
                pygame.draw.circle(auraSurf, (220, 30, 30, 26), (dr, dr), dr)
                screen.blit(auraSurf, (dcx - dr, dcy - dr))
                pygame.draw.circle(screen, (240, 60, 60), (dcx, dcy), dr, width=1)
                angle = getattr(tool, "scanAngle", 0.0)
                swX = dcx + int(math.cos(angle) * dr)
                swY = dcy + int(math.sin(angle) * dr)
                pygame.draw.line(screen, (255, 90, 90), (dcx, dcy), (swX, swY), 1)

                # Active red tether beam to aimTarget
                target = getattr(tool, "aimTarget", None)
                if target is not None and getattr(target, "alive", True):
                    tx = int(config.BOARD_X + target.x * config.TILE)
                    ty = int(config.BOARD_Y + target.y * config.TILE)
                    pygame.draw.line(screen, (255, 70, 70), (dcx, dcy), (tx, ty), 2)
                    pygame.draw.circle(screen, (255, 180, 180), ((dcx + tx) // 2, (dcy + ty) // 2), 3)
            else:
                pygame.draw.circle(auraSurf, (150, 60, 220, 22), (dr, dr), dr)
                screen.blit(auraSurf, (dcx - dr, dcy - dr))
                pygame.draw.circle(screen, (160, 80, 240), (dcx, dcy), dr, width=1)
                angle = getattr(tool, "scanAngle", 0.0)
                swX = dcx + int(math.cos(angle) * dr)
                swY = dcy + int(math.sin(angle) * dr)
                pygame.draw.line(screen, (200, 120, 255), (dcx, dcy), (swX, swY), 1)

                # Active tether beam to aimTarget (if slow is unlocked)
                target = getattr(tool, "aimTarget", None)
                if target is not None and getattr(target, "alive", True) and getattr(tool, "slowFactor", 1.0) < 1.0:
                    tx = int(config.BOARD_X + target.x * config.TILE)
                    ty = int(config.BOARD_Y + target.y * config.TILE)
                    pygame.draw.line(screen, (220, 130, 255), (dcx, dcy), (tx, ty), 2)
                    pygame.draw.circle(screen, (255, 210, 255), ((dcx + tx) // 2, (dcy + ty) // 2), 3)


        # Floating mini-health bar on damaged tools/walls
        if hasattr(tool, "hp") and hasattr(tool, "maxHp") and tool.hp < tool.maxHp:
            tRect = tileRect(tool.x, tool.y)
            barW = config.TILE - 2
            barH = 2
            barX = tRect.x + 1
            barY = tRect.y - 3
            pygame.draw.rect(screen, (20, 24, 32), (barX, barY, barW, barH))
            hpPct = max(0.0, tool.hp / tool.maxHp)
            hpColor = (70, 220, 120) if hpPct > 0.5 else ((240, 200, 60) if hpPct > 0.25 else (255, 70, 70))
            pygame.draw.rect(screen, hpColor, (barX, barY, max(1, int(barW * hpPct)), barH))

    for e in enemies:
        px = config.BOARD_X + e.x * config.TILE
        py = config.BOARD_Y + e.y * config.TILE
        radius = max(2, int(e.size * config.TILE))
        color = config.ENEMY_COLORS.get(e.type, config.COLOR_ENEMY)

        # Cyber slow aura ring
        if getattr(e, "slowTimer", 0.0) > 0:
            slowR = radius + 3
            pygame.draw.circle(screen, (190, 120, 255), (int(px), int(py)), slowR, width=1)

        # Distinct enemy shapes per type
        if e.type == "injection":
            # Sharp neon diamond (injector needle)
            pts = [
                (int(px), int(py - radius - 1)),
                (int(px + radius), int(py)),
                (int(px), int(py + radius + 1)),
                (int(px - radius), int(py)),
            ]
            pygame.draw.polygon(screen, color, pts)

        elif e.type == "memoryLeak":
            # Big tank amoeba with darker cellular nucleus
            pygame.draw.circle(screen, color, (int(px), int(py)), radius)
            innerR = max(2, radius // 2)
            pygame.draw.circle(screen, (25, 110, 75), (int(px), int(py)), innerR)

        elif e.type == "zeroDay":
            if getattr(e, "revealed", False):
                pygame.draw.circle(screen, color, (int(px), int(py)), radius)
            else:
                # Cloaked wireframe glitch circle
                pygame.draw.circle(screen, color, (int(px), int(py)), radius, width=1)
                pygame.draw.circle(screen, color, (int(px), int(py)), 1)

        else:
            # Standard bug: solid red with darker core
            pygame.draw.circle(screen, color, (int(px), int(py)), radius)
            if radius > 3:
                pygame.draw.circle(screen, (160, 40, 40), (int(px), int(py)), radius - 2)

        # Floating health bar if damaged
        if e.hp < e.maxHp and e.maxHp > 0:
            barW = max(12, int(radius * 2.2))
            barH = 3
            barX = int(px - barW // 2)
            barY = int(py - radius - 5)

            pygame.draw.rect(screen, (20, 24, 32), (barX, barY, barW, barH))
            hpPct = max(0.0, e.hp / e.maxHp)
            if hpPct > 0.5:
                hpColor = (70, 220, 120)    # Green
            elif hpPct > 0.25:
                hpColor = (240, 200, 60)   # Yellow
            else:
                hpColor = (255, 70, 70)    # Red

            fillW = max(1, int(barW * hpPct))
            pygame.draw.rect(screen, hpColor, (barX, barY, fillW, barH))
            pygame.draw.rect(screen, (10, 14, 20), (barX, barY, barW, barH), 1)

    for p in projectiles:
        px = config.BOARD_X + p.x * config.TILE
        py = config.BOARD_Y + p.y * config.TILE
        if getattr(p, "targetTool", None) is not None:
            # Corrupted hostile projectile
            pygame.draw.circle(screen, (255, 60, 60), (int(px), int(py)), 4)
            pygame.draw.circle(screen, (255, 180, 180), (int(px), int(py)), 2)
        elif getattr(p, "homingTarget", None) is not None:
            # Gold/cyan glowing homing seeker projectile
            pygame.draw.circle(screen, (255, 215, 60), (int(px), int(py)), 4)
            pygame.draw.circle(screen, (255, 255, 220), (int(px), int(py)), 2)
        else:
            pygame.draw.circle(screen, (100, 220, 255), (int(px), int(py)), 3)

    if selectedTool is not None:
        selectRect = tileRect(selectedTool.x, selectedTool.y)
        pygame.draw.rect(screen, (255, 255, 120), selectRect, width=2)

        selCenterX = config.BOARD_X + (selectedTool.x + 0.5) * config.TILE
        selCenterY = config.BOARD_Y + (selectedTool.y + 0.5) * config.TILE
        selRadius = int(selectedTool.range * config.TILE)

        pygame.draw.circle(screen, (255, 255, 120), (int(selCenterX), int(selCenterY)), selRadius, width=1)


#main loop
while running:
    dt = clock.tick(config.FPS) / 1000.0

    # ================================================================ INPUT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            toggleFullscreen()

        # ---- main menu
        if phase == config.PHASE_MENU:
            action = startMenu.handleEvent(event)
            if action == "play":
                phase = config.PHASE_BUILD
            elif action == "fullscreen":
                toggleFullscreen()
            elif action == "quit":
                running = False
            continue

        if phase == config.PHASE_GAME_OVER:
            action = gameOverTerminal.handleEvent(event)
            if action == "submitted":
                recordNewScore(gameOverTerminal.playerName, gameState.wave, gameState.totalBytesEarned, gameState.bugsKilled)
                resetGame()
                startMenu.state = "scoreboard"   # Takes player directly to the scoreboard to see their rank!
                phase = config.PHASE_MENU
            elif action == "quit":
                resetGame()
                phase = config.PHASE_MENU
            continue

        # ---- paused
        if paused:
            action = pauseMenu.handleEvent(event)
            if action == "resume":
                paused = False
            elif action == "restart":
                paused = False
                resetGame()
                phase = config.PHASE_BUILD
            elif action == "main_menu":
                paused = False
                resetGame()
                startMenu.state = "main"
                phase = config.PHASE_MENU
            continue

        # ---- in game: UI first (Gavin's editor + shop)
        uiManager.process_events(event)
        codeEditor.handleEvent(event, gameState.unlockedConcepts, board=board)

        if not codeEditor.isOpen:
            shopPanel.panel.show()
        action = shopPanel.handleEvent(event, gameState, selectedTool, board)
        if action == "open_compiler" and selectedTool is not None:
            codeEditor.open(selectedTool)
            shopPanel.panel.hide()
        elif action == "deselected":
            selectedTool = None
            codeEditor.close()
        # Keyboard shortcuts (only active when NOT typing code in the editor)
        if not codeEditor.isOpen:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = True
                pauseMenu.open()
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
                  and gameState.wave == 1 and not waveSpawner.active
                  and waveCountdown is None):
                beginWave()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                debugOverlay.cycleMode()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                debugOverlay.cycleView()

        ###DEBUG
        if event.type == pygame.MOUSEBUTTONDOWN:
            tx = (event.pos[0] - config.BOARD_X) // config.TILE
            ty = (event.pos[1] - config.BOARD_Y) // config.TILE
            if event.button == 1:   # left click
                existing = board.toolAt(tx, ty)
                if existing is not None:
                    selectedTool = existing
                    audioManager.sfx("select")
                    codeEditor.close()
                    shopPanel.panel.show()
                elif board.isBuildable(tx, ty):
                    toolType = shopPanel.selectedToolType
                    cost = config.TOOL_STATS[toolType]["cost"]
                    if gameState.spendBytes(cost):
                        if toolType in ("debugger", "turret"):
                            board.place(Debugger(tx, ty), tx, ty)
                            audioManager.sfx("place")
                        elif toolType == "firewall":
                            board.place(Firewall(tx, ty), tx, ty)
                            audioManager.sfx("place")
                        elif toolType == "antivirus":
                            board.place(Antivirus(tx, ty), tx, ty)
                            audioManager.sfx("antivirus")

                    selectedTool = None
                    codeEditor.close()
                    shopPanel.panel.show()

            elif event.button == 3:   # right click
                removedTool = board.remove(tx, ty)
                if removedTool:
                    gameState.refundBytes(removedTool.spent)
                    audioManager.sfx("back")
                selectedTool = None
                codeEditor.close()
        ###DEBUG

    # ================================================================ UPDATE + DRAW
    if phase == config.PHASE_MENU:
        startMenu.draw(screen)

    else:
        # ---- update (skipped entirely while paused, so everything freezes)
        if not paused and phase != config.PHASE_GAME_OVER:
            # Check for Game Over when CPU HP hits 0
            if gameState.cpuHp <= 0:
                phase = config.PHASE_GAME_OVER
                gameState.phase = config.PHASE_GAME_OVER
                gameOverTerminal.open(gameState.wave, gameState.totalBytesEarned, gameState.bugsKilled)

            shopPanel.update(gameState, selectedTool)
            uiManager.update(dt)
            for tool in board.allTools():
                if hasattr(tool, "update"):
                    tool.update(dt, enemies, projectiles, gameState.unlockedConcepts, board=board)

            # AI tick: pheromones fade + spread every AI_TICK_SECONDS
            aiTimer += dt
            aiTick = aiTimer >= config.AI_TICK_SECONDS
            if aiTick:
                aiTimer = 0.0
                pheromones.tick()

            # board changed (place / remove / destroy) -> rebuild everything now so nobody walks into a new tool
            if board.dirty:
                fields = buildFields(board, pheromones.grid)
                board.dirty = False
                board.hpChanged = False
                fieldJobs = []
            # fear shifted or tools took damage -> queue every field, then refresh one per frame
            elif aiTick and (pheromones.isActive() or board.hpChanged) and not fieldJobs:
                fieldJobs = [(target, enemyType) for target in fields for enemyType in fields[target]]
                board.hpChanged = False

            if fieldJobs:
                target, enemyType = fieldJobs.pop()
                fields[target][enemyType] = buildOneField(board, pheromones.grid, target, enemyType)

            for p in projectiles:
                p.update(dt, enemies, board)
            projectiles = [p for p in projectiles if p.alive]

            waveSpawner.update(dt, board, enemies)

            for e in enemies:
                e.update(dt, board, fields[e.target][e.type], enemies)

            # Damaging plasma walls (Tier 3) zap enemies touching intermediate tiles
            damTiles = board.damagingPlasmaTiles
            if damTiles:
                for e in enemies:
                    if (int(e.x), int(e.y)) in damTiles:
                        e.takeDamage(config.PLASMA_WALL_DPS * dt)

            enemies = [e for e in enemies if e.alive]

            # wave cleared -> pay out, keep some fear for next wave, start the countdown
            if waveSpawner.active and waveSpawner.isDone(enemies):
                waveSpawner.active = False
                gameState.addBytes(config.WAVE_CLEAR_BONUS)
                gameState.regenerateCpuBetweenWaves(0.25)
                gameState.wave += 1
                phase = config.PHASE_BUILD
                waveCountdown = config.WAVE_BREAK_SECONDS
                pheromones.carryOver()

            # between waves -> count down, then start the next one automatically
            elif waveCountdown is not None:
                waveCountdown -= dt
                if waveCountdown <= 0:
                    waveCountdown = None
                    beginWave()

        # ---- draw (always, even while paused)
        screen.fill(config.COLOR_BG)
        drawBoard()

        debugOverlay.draw(screen, board, fields, pheromones.grid)

        hud.draw(screen, gameState, enemies)

        # wave banner: "PRESS ENTER TO BEGIN" before wave 1, countdown between waves
        if phase == config.PHASE_BUILD:
            msg = None
            if waveCountdown is not None:
                msg = f"► INCOMING SWARM // WAVE {gameState.wave} IN {math.ceil(waveCountdown)}s"
            elif gameState.wave == 1:
                msg = "► SYSTEM READY // PRESS [ENTER] TO COMMENCE WAVE 1"
            if msg:
                textSurf = bannerFont.render(msg, True, (105, 255, 160))
                glowSurf = bannerFont.render(msg, True, (20, 110, 65))
                bCenter = (config.BOARD_X + config.BOARD_PX_W // 2, config.BOARD_Y + 30)
                bRect = textSurf.get_rect(center=bCenter)

                # Frosted cyber glass banner pill
                bannerPill = bRect.inflate(36, 12)
                pillSurf = pygame.Surface((bannerPill.width, bannerPill.height), pygame.SRCALPHA)
                pillSurf.fill((10, 18, 26, 230))
                screen.blit(pillSurf, bannerPill.topleft)
                pygame.draw.rect(screen, (45, 135, 88), bannerPill, width=2, border_radius=6)

                # Corner accent ticks
                cLen = 8
                accCol = (80, 245, 140)
                pygame.draw.line(screen, accCol, bannerPill.topleft, (bannerPill.left + cLen, bannerPill.top), 2)
                pygame.draw.line(screen, accCol, bannerPill.topleft, (bannerPill.left, bannerPill.top + cLen), 2)
                pygame.draw.line(screen, accCol, bannerPill.topright, (bannerPill.right - cLen, bannerPill.top), 2)
                pygame.draw.line(screen, accCol, bannerPill.topright, (bannerPill.right, bannerPill.top + cLen), 2)
                pygame.draw.line(screen, accCol, bannerPill.bottomleft, (bannerPill.left + cLen, bannerPill.bottom), 2)
                pygame.draw.line(screen, accCol, bannerPill.bottomleft, (bannerPill.left, bannerPill.bottom - cLen), 2)
                pygame.draw.line(screen, accCol, bannerPill.bottomright, (bannerPill.right - cLen, bannerPill.bottom), 2)
                pygame.draw.line(screen, accCol, bannerPill.bottomright, (bannerPill.right, bannerPill.bottom - cLen), 2)

                screen.blit(glowSurf, bRect.move(2, 2))
                screen.blit(textSurf, bRect)

        uiManager.draw_ui(screen)

        # High-voltage neon corner accents on Shop / Editor panel dock
        spx, spy = 980, config.BOARD_Y
        spw, sph = 284, config.BOARD_PX_H
        cLen = 14
        accCol = (80, 245, 140)
        pygame.draw.line(screen, accCol, (spx, spy), (spx + cLen, spy), 2)
        pygame.draw.line(screen, accCol, (spx, spy), (spx, spy + cLen), 2)
        pygame.draw.line(screen, accCol, (spx + spw, spy), (spx + spw - cLen, spy), 2)
        pygame.draw.line(screen, accCol, (spx + spw, spy), (spx + spw, spy + cLen), 2)
        pygame.draw.line(screen, accCol, (spx, spy + sph), (spx + cLen, spy + sph), 2)
        pygame.draw.line(screen, accCol, (spx, spy + sph), (spx, spy + sph - cLen), 2)
        pygame.draw.line(screen, accCol, (spx + spw, spy + sph), (spx + spw - cLen, spy + sph), 2)
        pygame.draw.line(screen, accCol, (spx + spw, spy + sph), (spx + spw, spy + sph - cLen), 2)

        # pause overlay on top of everything (including the shop/editor panels)
        if paused:
            pauseMenu.draw(screen)

        # Game Over overlay
        if phase == config.PHASE_GAME_OVER:
            gameOverTerminal.draw(screen, dt)

    pygame.display.flip()

pygame.quit()
sys.exit()