import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import config

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))

from game.audio import audioManager, AudioManager
from ui.menu import StartMenu
from ui.pauseMenu import PauseMenu

def test_audio_manager():
    print("Testing AudioManager...")
    audioManager.setMusicVolume(0.5)
    assert abs(audioManager.getMusicVolume() - 0.5) < 0.01, f"Expected 0.5, got {audioManager.getMusicVolume()}"
    
    audioManager.setSfxVolume(0.9)
    assert abs(audioManager.getSfxVolume() - 0.9) < 0.01, f"Expected 0.9, got {audioManager.getSfxVolume()}"
    
    # Clamping tests
    audioManager.setMusicVolume(1.5)
    assert audioManager.getMusicVolume() == 1.0, f"Expected 1.0, got {audioManager.getMusicVolume()}"
    
    audioManager.setMusicVolume(-0.5)
    assert audioManager.getMusicVolume() == 0.0, f"Expected 0.0, got {audioManager.getMusicVolume()}"
    
    # Mute test
    wasMuted = audioManager.isMuted
    audioManager.toggleMute()
    assert audioManager.isMuted != wasMuted
    audioManager.toggleMute()
    assert audioManager.isMuted == wasMuted
    print("AudioManager passed!")

def test_start_menu_volume():
    print("Testing StartMenu volume flow...")
    menu = StartMenu(config.SCREEN_W, config.SCREEN_H)
    assert menu.state == "main"
    
    # Find volume button
    volBtn = next((b for b in menu.mainButtons if b.actionKey == "volume"), None)
    assert volBtn is not None, "VOLUME CONTROLS button not found in main menu!"
    
    # Simulate clicking Volume button
    clickEvt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": volBtn.rect.center})
    res = menu.handleEvent(clickEvt)
    assert res is None
    assert menu.state == "volume", f"Expected state 'volume', got {menu.state}"
    
    # Test drawing volume screen
    surf = pygame.Surface((config.SCREEN_W, config.SCREEN_H))
    menu.draw(surf)
    print("StartMenu volume draw succeeded!")
    
    # Simulate clicking Back button inside VolumeModal
    backPos = menu.volumeModal.backBtnRect.center
    backClickEvt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": backPos})
    res = menu.handleEvent(backClickEvt)
    assert menu.state == "main", f"Expected state 'main' after back, got {menu.state}"
    
    # Re-enter volume state and test ESC
    menu.handleEvent(clickEvt)
    assert menu.state == "volume"
    escEvt = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    menu.handleEvent(escEvt)
    assert menu.state == "main", f"Expected state 'main' after ESC, got {menu.state}"
    print("StartMenu volume flow passed!")

def test_pause_menu_volume():
    print("Testing PauseMenu volume flow...")
    pause = PauseMenu(config.SCREEN_W, config.SCREEN_H)
    assert pause.state == "menu"
    
    # Find volume button in pause menu
    volBtn = next((b for b in pause.mainButtons if b.actionKey == "volume"), None)
    assert volBtn is not None, "VOLUME CONTROLS button not found in pause menu!"
    
    # Click volume button
    clickEvt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": volBtn.rect.center})
    res = pause.handleEvent(clickEvt)
    assert res is None
    assert pause.state == "volume", f"Expected state 'volume', got {pause.state}"
    
    # Test drawing volume in pause menu
    surf = pygame.Surface((config.SCREEN_W, config.SCREEN_H))
    pause.draw(surf)
    print("PauseMenu volume draw succeeded!")
    
    # Test Back button in volume modal
    backPos = pause.volumeModal.backBtnRect.center
    backClickEvt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": backPos})
    pause.handleEvent(backClickEvt)
    assert pause.state == "menu", f"Expected state 'menu' after back, got {pause.state}"
    
    # Re-enter and test ESC
    pause.handleEvent(clickEvt)
    assert pause.state == "volume"
    escEvt = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    pause.handleEvent(escEvt)
    assert pause.state == "menu", f"Expected state 'menu' after ESC, got {pause.state}"
    print("PauseMenu volume flow passed!")

if __name__ == "__main__":
    test_audio_manager()
    test_start_menu_volume()
    test_pause_menu_volume()
    print("ALL TESTS PASSED SUCCESSFULLY!")
