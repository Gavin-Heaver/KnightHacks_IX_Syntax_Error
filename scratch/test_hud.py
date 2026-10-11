import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import config

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))

from game.gameState import GameState
from ui.hud import HUD
from entities.enemy import Enemy

def test_hud_enemy_list():
    hud = HUD()
    gs = GameState()
    
    # Wave 1
    gs.wave = 1
    hud.draw(screen, gs, [])
    assert "bug" in gs.encounteredEnemies
    assert "zeroDay" not in gs.encounteredEnemies
    print("Wave 1 HUD OK! Enemies:", gs.encounteredEnemies)
    
    # Wave 3
    gs.wave = 3
    hud.draw(screen, gs, [])
    assert "injection" in gs.encounteredEnemies
    assert "memoryLeak" in gs.encounteredEnemies
    assert "zeroDay" not in gs.encounteredEnemies
    print("Wave 3 HUD OK! Enemies:", gs.encounteredEnemies)
    
    # Wave 4
    gs.wave = 4
    hud.draw(screen, gs, [])
    assert "zeroDay" in gs.encounteredEnemies
    print("Wave 4 HUD OK! Enemies:", gs.encounteredEnemies)
    
    # Dynamic enemy appearance
    gs2 = GameState()
    gs2.wave = 1
    customEnemy = Enemy("zeroDay", 0, 0)
    hud.draw(screen, gs2, [customEnemy])
    assert "zeroDay" in gs2.encounteredEnemies
    print("Dynamic enemy encounter OK! Enemies:", gs2.encounteredEnemies)
    print("ALL HUD TESTS PASSED!")

if __name__ == "__main__":
    test_hud_enemy_list()

