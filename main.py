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
from scripting.runner import towerScript

#setup
random.seed(config.DEMO_SEED)   # deterministic demo (use only `random` for randomness)
pygame.init()
screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
pygame.display.set_caption("Code Tower Defense")
clock = pygame.time.Clock()
uiManager = pygame_gui.UIManager((config.SCREEN_W, config.SCREEN_H))
running = True

board = Board()
phase = config.PHASE_BUILD
enemies = []                    # game.enemies: list[Enemy]


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


#main loop
while running:
    dt = clock.tick(config.FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        uiManager.process_events(event)

    uiManager.update(dt)

    # flow fields are rebuilt only when the board changes (see board.dirty)
    if board.dirty:
        board.dirty = False

    screen.fill(config.COLOR_BG)
    drawBoard()
    uiManager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
