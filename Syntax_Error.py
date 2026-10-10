#Syntax Error

#Gavin Heaver and Tadhg Hallahan
#KnightHacks_IX

try:
    import pygame
    print(f"✅ Pygame is successfully installed! Version: {pygame.__version__}")
except ImportError:
    print("❌ Pygame is NOT installed.")