#Syntax Error

#Gavin Heaver and Tadhg Hallahan
#KnightHacks_IX

#YOU WILL BE REWARDED FOR YOU PATIENCE AND UNDERSTANDING~ THANK YOU PANDA EXPRESS
#YOU ARE ADMIRED FOR YOUR ADVENTUROUS SPIRIT~ THANK YOU PANDA EXPRESS x2

#imports
import pygame
import pygame_gui

import sys                     # settrace (cycles budget)
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
from ui.debugOverlay import drawFlowArrows, drawHeatmap
from game.gameState import GameState
from game.waves import WaveSpawner
from ai.costLayers import buildFields
from ai.pheromone import PheromoneMap

###DEBUG
from entities.tools import Turret, Firewall, Debugger
###DEBUG
from ui.shop import ShopPanel
from ui.menu import StartMenu, recordNewScore
from ui.hud import HUD
from ui.editor import CodeEditor
from ui.gameOver import GameOverTerminal

#setup
random.seed(config.DEMO_SEED)   # deterministic demo (use only `random` for randomness)
pygame.init()
screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
pygame.display.set_caption("Code Tower Defense")
clock = pygame.time.Clock()
uiManager = pygame_gui.UIManager((config.SCREEN_W, config.SCREEN_H))
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
overlayMode = 0                 # F1 cycles: 0 = off, 1 = flow arrows, 2 = fear heatmap
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


def beginWave():
    global phase
    waveSpawner.start(gameState.wave)
    phase = config.PHASE_WAVE


def resetGame():
    global board, gameState, enemies, projectiles, waveSpawner
    global waveCountdown, selectedTool, paused, phase, fields, pheromones, aiTimer, scoreRecorded

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
    paused = False
    phase = config.PHASE_MENU
    events.subscribe("toolDestroyed", onToolDestroyed)
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

        if board.isBuildable(hoverX, hoverY):
            previewColor = (180, 255, 180)
            pygame.draw.rect(screen, previewColor, tileRect(hoverX, hoverY), width=2)
            
            toolRange = config.TOOL_STATS[shopPanel.selectedToolType]["range"]
            if toolRange > 0:
                radius = int(toolRange * config.TILE)
                pygame.draw.circle(screen, previewColor, (int(centerPixelX), int(centerPixelY)), radius, width=1)
        else:
            previewColor = (255, 70, 70)
            pygame.draw.rect(screen, previewColor, tileRect(hoverX, hoverY), width=2)

    # Board outer boundary frame
    boardOutline = pygame.Rect(config.BOARD_X - 1, config.BOARD_Y - 1,
                               config.BOARD_PX_W + 2, config.BOARD_PX_H + 2)
    pygame.draw.rect(screen, (40, 55, 75), boardOutline, 2)

    for y in range(board.height):
        for x in range(board.width):
            pygame.draw.rect(screen, config.COLOR_GRID, tileRect(x, y), 1)
    for (x, y) in board.cpuTiles:
        pygame.draw.rect(screen, config.COLOR_CPU, tileRect(x, y).inflate(-2, -2))
    for tool in board.allTools():
        color = config.TOOL_COLORS.get(tool.kind, config.COLOR_TOOL)
        pygame.draw.rect(screen, color, tileRect(tool.x, tool.y).inflate(-4, -4))
    for e in enemies:
        px = config.BOARD_X + e.x * config.TILE
        py = config.BOARD_Y + e.y * config.TILE
        radius = max(2, int(e.size * config.TILE))
        pygame.draw.circle(screen, config.COLOR_ENEMY, (int(px), int(py)), radius)

    for p in projectiles:
        px = config.BOARD_X + p.x * config.TILE
        py = config.BOARD_Y + p.y * config.TILE
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

        # ---- main menu
        if phase == config.PHASE_MENU:
            action = startMenu.handleEvent(event)
            if action == "play":
                phase = config.PHASE_BUILD
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

        # ---- paused: only ENTER (resume) and ESC (quit to menu) do anything
        if paused:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    paused = False
                elif event.key == pygame.K_ESCAPE:
                    resetGame()
            continue

        # ---- in game: UI first (Gavin's editor + shop)
        uiManager.process_events(event)
        codeEditor.handleEvent(event)
        if not codeEditor.isOpen:
            shopPanel.panel.show()
        action = shopPanel.handleEvent(event, gameState, selectedTool, board)
        if action == "open_compiler" and selectedTool is not None:
            codeEditor.open(selectedTool)
            shopPanel.panel.hide()
        elif action == "deselected":
            selectedTool = None
            codeEditor.close()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            paused = True

        # ENTER starts the first wave only (later waves start themselves after the countdown)
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
              and gameState.wave == 1 and not waveSpawner.active
              and waveCountdown is None and not codeEditor.isOpen):
            beginWave()

        ###DEBUG
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            edges = [(x, y) for x in range(board.width) for y in (0, board.height - 1)] + \
                    [(x, y) for y in range(board.height) for x in (0, board.width - 1)]
            x, y = random.choice([t for t in edges if board.isBuildable(*t)])
            enemies.append(Enemy("zeroDay", x + 0.5, y + 0.5))
        ###DEBUG

        # F1 cycles the AI overlay: off -> flow arrows -> fear heatmap -> off
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            overlayMode = (overlayMode + 1) % 3

        ###DEBUG
        elif event.type == pygame.MOUSEBUTTONDOWN:
            tx = (event.pos[0] - config.BOARD_X) // config.TILE
            ty = (event.pos[1] - config.BOARD_Y) // config.TILE
            if event.button == 1:   # left click
                existing = board.toolAt(tx, ty)
                if existing is not None:
                    selectedTool = existing
                    codeEditor.close()
                    shopPanel.panel.show()
                elif board.isBuildable(tx, ty):
                    toolType = shopPanel.selectedToolType
                if existing is None and board.isBuildable(tx, ty):
                    toolType = shopPanel.selectedToolType
                    cost = config.TOOL_STATS[toolType]["cost"]
                    if gameState.spendBytes(cost):
                        if toolType == "turret":
                            board.place(Turret(tx, ty), tx, ty)
                        elif toolType == "firewall":
                            board.place(Firewall(tx, ty), tx, ty)
                        elif toolType == "debugger":
                            board.place(Debugger(tx, ty), tx, ty)
                    selectedTool = None
                    codeEditor.close()
                    shopPanel.panel.show()

            elif event.button == 3:   # right click
                removedTool = board.remove(tx, ty)
                if removedTool:
                    gameState.refundBytes(removedTool.spent)
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

            # AI tick: pheromones fade + spread every AI_TICK_SECONDS
            aiTimer += dt
            aiTick = aiTimer >= config.AI_TICK_SECONDS
            if aiTick:
                aiTimer = 0.0
                pheromones.tick()

            # rebuild flow fields when the board changes, or when fear has shifted
            if board.dirty or (aiTick and pheromones.isActive()):
                fields = buildFields(board, pheromones.grid)
                board.dirty = False

            for tool in board.allTools():
                if hasattr(tool, "update"):
                    tool.update(dt, enemies, projectiles)

            for p in projectiles:
                p.update(dt, enemies, board)
            projectiles = [p for p in projectiles if p.alive]

            waveSpawner.update(dt, board, enemies)

            for e in enemies:
                e.update(dt, board, fields[e.type], enemies)
            enemies = [e for e in enemies if e.alive]

            # wave cleared -> pay out, keep some fear for next wave, start the countdown
            if waveSpawner.active and waveSpawner.isDone(enemies):
                waveSpawner.active = False
                gameState.addBytes(config.WAVE_CLEAR_BONUS)
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

        if overlayMode == 1:
            drawFlowArrows(screen, board, fields["bug"])
        elif overlayMode == 2:
            drawHeatmap(screen, pheromones.grid)

        hud.draw(screen, gameState)

        # wave banner: "PRESS ENTER TO BEGIN" before wave 1, countdown between waves
        if phase == config.PHASE_BUILD:
            msg = None
            if waveCountdown is not None:
                msg = f"WAVE {gameState.wave} IN {math.ceil(waveCountdown)}"
            elif gameState.wave == 1:
                msg = "PRESS ENTER TO BEGIN"
            if msg:
                text = bannerFont.render(msg, True, config.COLOR_TEXT)
                screen.blit(text, text.get_rect(center=(config.BOARD_X + config.BOARD_PX_W // 2,
                                                        config.BOARD_Y + 30)))

        uiManager.draw_ui(screen)

        # pause overlay on top of everything (including the shop/editor panels)
        if paused:
            shade = pygame.Surface((config.SCREEN_W, config.SCREEN_H), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 150))
            screen.blit(shade, (0, 0))
            cx, cy = config.SCREEN_W // 2, config.SCREEN_H // 2
            title = pauseFont.render("PAUSED", True, config.COLOR_TEXT)
            hint = hintFont.render("ENTER  resume     ESC  quit to menu", True, (150, 170, 190))
            screen.blit(title, title.get_rect(center=(cx, cy - 20)))
            screen.blit(hint, hint.get_rect(center=(cx, cy + 35)))

        # Game Over overlay
        if phase == config.PHASE_GAME_OVER:
            gameOverTerminal.draw(screen, dt)

    pygame.display.flip()

pygame.quit()
sys.exit()