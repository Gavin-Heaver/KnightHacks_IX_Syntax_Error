#Syntax Error

#Gavin Heaver and Tadhg Hallahan
#KnightHacks_IX

#imports
import pygame
import pygame_gui

import sys                     # settrace (cycles budget)
import ast                     # script checks (unlocks, blocked imports)
import heapq                   # Dijkstra
import math, random, time, numpy  # math, random, noise
from collections import deque  # BFS helpers, event queues
from dataclasses import dataclass, field
from enum import Enum, auto    # game phases, enemy types
import json                    # wave definition, (optional)

from game.board import Board
from ai.flowField import buildField
from scripting.runner import towerScript

#setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True
