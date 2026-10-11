# game/audio.py -- Global audio management and volume controls for Music & SFX.
import os
import json
import pygame

SETTINGS_FILE = "audio_settings.json"

class AudioManager:
    """Manages audio playback, music volume, and sound effects volume."""
    def __init__(self):
        self.musicVolume = 0.7   # 0.0 to 1.0 (70%)
        self.sfxVolume = 0.8     # 0.0 to 1.0 (80%)
        self.isMuted = False
        self._soundCache = {}
        self.initialized = False

        self._initMixer()
        self.loadSettings()
        self.applyVolume()

    def _initMixer(self):
        """Safely initialize pygame mixer if not already initialized."""
        if not pygame.mixer.get_init():
            try:
                # 44.1kHz, 16-bit signed, 2 channels, 512 buffer for low latency
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.initialized = True
            except Exception as e:
                print("AudioManager: pygame.mixer.init failed or sound card unavailable:", e)
                self.initialized = False
        else:
            self.initialized = True

    def loadSettings(self):
        """Loads saved volume preferences if available."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.musicVolume = max(0.0, min(1.0, float(data.get("musicVolume", 0.7))))
                    self.sfxVolume = max(0.0, min(1.0, float(data.get("sfxVolume", 0.8))))
                    self.isMuted = bool(data.get("isMuted", False))
            except Exception as e:
                print("AudioManager: Failed to load audio settings:", e)

    def saveSettings(self):
        """Saves current volume settings to disk."""
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({
                    "musicVolume": round(self.musicVolume, 2),
                    "sfxVolume": round(self.sfxVolume, 2),
                    "isMuted": self.isMuted
                }, f, indent=2)
        except Exception as e:
            print("AudioManager: Failed to save audio settings:", e)

    def applyVolume(self):
        """Applies music volume to pygame mixer."""
        if self.initialized:
            try:
                effectiveMusic = 0.0 if self.isMuted else self.musicVolume
                pygame.mixer.music.set_volume(effectiveMusic)
            except Exception:
                pass

    def setMusicVolume(self, volume: float):
        """Sets music volume between 0.0 and 1.0."""
        self.musicVolume = max(0.0, min(1.0, volume))
        self.applyVolume()
        self.saveSettings()

    def setSfxVolume(self, volume: float):
        """Sets sound effects volume between 0.0 and 1.0."""
        self.sfxVolume = max(0.0, min(1.0, volume))
        # Update any cached sound volumes if present
        for sound in self._soundCache.values():
            try:
                eff = 0.0 if self.isMuted else self.sfxVolume
                sound.set_volume(eff)
            except Exception:
                pass
        self.saveSettings()

    def getMusicVolume(self) -> float:
        return self.musicVolume

    def getSfxVolume(self) -> float:
        return self.sfxVolume

    def toggleMute(self):
        self.isMuted = not self.isMuted
        self.applyVolume()
        self.saveSettings()
        return self.isMuted

    def playMusic(self, filePath: str, loop: bool = True):
        """Safely loads and plays background music."""
        if not self.initialized:
            return
        try:
            pygame.mixer.music.load(filePath)
            effectiveMusic = 0.0 if self.isMuted else self.musicVolume
            pygame.mixer.music.set_volume(effectiveMusic)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print(f"AudioManager: Could not play music '{filePath}':", e)

    def stopMusic(self):
        if self.initialized:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def playSfx(self, filePath: str):
        """Safely plays a sound effect at the configured SFX volume."""
        if not self.initialized or self.isMuted or self.sfxVolume <= 0.0:
            return
        try:
            if filePath not in self._soundCache:
                self._soundCache[filePath] = pygame.mixer.Sound(filePath)
            sound = self._soundCache[filePath]
            sound.set_volume(self.sfxVolume)
            sound.play()
        except Exception as e:
            print(f"AudioManager: Could not play SFX '{filePath}':", e)


# Global singleton instance
audioManager = AudioManager()

