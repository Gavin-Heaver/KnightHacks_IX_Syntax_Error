import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import pygame_gui
import config

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))

# 1. Test theme.json parsing
print("Testing theme.json...")
themePath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "theme.json")
assert os.path.exists(themePath), "theme.json does not exist!"
with open(themePath, "r") as f:
    themeData = json.load(f)
assert "button" in themeData and "panel" in themeData
uiManager = pygame_gui.UIManager((config.SCREEN_W, config.SCREEN_H), themePath)
print("theme.json OK!")

# 2. Test HUD
print("Testing HUD with cyberpunk style...")
from ui.hud import HUD
from game.gameState import GameState
hud = HUD()
gs = GameState()
hud.draw(screen, gs, [])
print("HUD draw OK!")

# 3. Test PauseMenu
print("Testing PauseMenu with cyberpunk style...")
from ui.pauseMenu import PauseMenu
pause = PauseMenu(config.SCREEN_W, config.SCREEN_H)
pause.state = "menu"
pause.draw(screen)
pause.state = "confirm_restart"
pause.draw(screen)
pause.state = "confirm_menu"
pause.draw(screen)
pause.state = "volume"
pause.draw(screen)
print("PauseMenu draw OK across all states!")

# 4. Test GameOverTerminal
print("Testing GameOverTerminal...")
from ui.gameOver import GameOverTerminal
got = GameOverTerminal(config.SCREEN_W, config.SCREEN_H)
got.open(5, 500, 25)
got.draw(screen)
print("GameOverTerminal draw OK!")

print("ALL CYBER THEME INTEGRATION TESTS PASSED!")

