#Syntax Error

#Gavin Heaver and Tadhg Hallahan
#KnightHacks_IX

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
from ai.flowField import buildField
from entities.enemy import Enemy
from ui.debugOverlay import drawFlowArrows

###DEBUG
from entities.tools import Turret
###DEBUG
from ui.menu import StartMenu

#setup
random.seed(config.DEMO_SEED)   # deterministic demo (use only `random` for randomness)
pygame.init()
screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
pygame.display.set_caption("Code Tower Defense")
clock = pygame.time.Clock()
uiManager = pygame_gui.UIManager((config.SCREEN_W, config.SCREEN_H))
running = True

board = Board()

###DEBUG
def bugCost(x, y):
    """TEMP: moves to ai/costLayers.py later. Tools are passable but expensive."""
    tool = board.toolAt(x, y)
    if tool:
        return 1 + tool.hp / config.BUG_DPS   # seconds to chew through = the wall cost
    return 1

dist = buildField(board, board.cpuTiles, bugCost)
###DEBUG

### Move to game/board.py
def onToolDestroyed(tool):
    board.remove(tool.x, tool.y)

events.subscribe("toolDestroyed", onToolDestroyed)
### Move to game/board.py

phase = config.PHASE_MENU
startMenu = StartMenu(config.SCREEN_W, config.SCREEN_H)
showOverlay = False
enemies = []                    # game.enemies: list[Enemy]
projectiles = []


def tileRect(x, y):
    return pygame.Rect(config.BOARD_X + x * config.TILE, config.BOARD_Y + y * config.TILE,
                       config.TILE, config.TILE)


def drawBoard():
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
        pygame.draw.rect(screen, config.COLOR_TOOL, tileRect(tool.x, tool.y).inflate(-4, -4))
    for e in enemies:
        px = config.BOARD_X + e.x * config.TILE
        py = config.BOARD_Y + e.y * config.TILE
        pygame.draw.circle(screen, config.COLOR_ENEMY, (int(px), int(py)), config.TILE // 3)

    for p in projectiles:
        px = config.BOARD_X + p.x * config.TILE
        py = config.BOARD_Y + p.y * config.TILE
        pygame.draw.circle(screen, (100, 220, 255), (int(px), int(py)), 3)


#main loop
while running:
    dt = clock.tick(config.FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if phase == config.PHASE_MENU:
            action = startMenu.handleEvent(event)
            if action == "play":
                phase = config.PHASE_BUILD
            elif action == "quit":
                running = False
        else:
            uiManager.process_events(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                phase = config.PHASE_MENU   # ESC returns to main menu

            ###DEBUG
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                edges = [(x, y) for x in range(board.width) for y in (0, board.height - 1)] + \
                    [(x, y) for y in range(board.height) for x in (0, board.width - 1)]
                x, y = random.choice([t for t in edges if board.isBuildable(*t)])
                enemies.append(Enemy("bug", x + 0.5, y + 0.5))
            ###DEBUG

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                showOverlay = not showOverlay

            ###DEBUG
            elif event.type == pygame.MOUSEBUTTONDOWN:
                tx = (event.pos[0] - config.BOARD_X) // config.TILE
                ty = (event.pos[1] - config.BOARD_Y) // config.TILE
                if event.button == 1:
                    board.place(Turret(tx, ty), tx, ty)
                elif event.button == 3:
                    board.remove(tx, ty)               # right click: remove it
            ###DEBUG

    if phase == config.PHASE_MENU:
        startMenu.draw(screen)
    else:
        uiManager.update(dt)

        # flow fields are rebuilt only when the board changes (see board.dirty)
        if board.dirty:
            dist = buildField(board, board.cpuTiles, bugCost)
            board.dirty = False

        for tool in board.allTools():
            if hasattr(tool, "update"):
                tool.update(dt, enemies, projectiles)

        for p in projectiles:
            p.update(dt, enemies, board)
        projectiles = [p for p in projectiles if p.alive]

        for e in enemies:
            e.update(dt, board, dist)
        enemies = [e for e in enemies if e.alive]

        screen.fill(config.COLOR_BG)
        drawBoard()
        if showOverlay:
            drawFlowArrows(screen, board, dist)
        uiManager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
