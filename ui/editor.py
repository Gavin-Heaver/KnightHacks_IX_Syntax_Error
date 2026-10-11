import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UITextEntryBox, UIButton, UITextBox, UILabel
import config
from game.audio import audioManager

class CodeEditor:
    def __init__(self, uiManager):
        self.uiManager = uiManager
        self.currentTool = None
        self.isOpen = False
        self.buildUI()
        self.panel.hide()

    def buildUI(self):
        self.panel = UIPanel (
            relative_rect=pygame.Rect((980, config.BOARD_Y), (284, config.BOARD_PX_H)), manager=self.uiManager
        )

        self.titleLabel = UILabel(
            relative_rect=pygame.Rect((10, 10), (264, 30)), text="TOWER COMPILER", manager=self.uiManager, container=self.panel
        )

        self.codeBox = UITextEntryBox(
            relative_rect=pygame.Rect((10, 50), (264, 340)), initial_text = "", manager=self.uiManager, container=self.panel
            )

        self.closeBtn = UIButton(
            relative_rect=pygame.Rect((180, 400), (94, 40)), text="CLOSE", manager=self.uiManager, container=self.panel
        )

        self.compileBtn = UIButton(
                    relative_rect=pygame.Rect((10, 400), (160, 40)), text="COMPILE & RUN", manager=self.uiManager, container=self.panel
        )

        self.consoleBox = UITextBox(
            html_text="Console ready...", relative_rect=pygame.Rect((10, 450), (264, 180)), manager=self.uiManager, container=self.panel
        )

    def open(self, tool):
        self.currentTool = tool
        self.isOpen = True

        self.codeBox.set_text(tool.script.sourceCode)

        if getattr(tool, "corrupted", False):
            self.titleLabel.set_text(f"{tool.kind.upper()} COMPILER [INFECTED!]")
            errorMsg = tool.script.error or "Injected malware detected."
            self.consoleBox.set_text(f"<font color='#FF4646'><b>MALWARE INFECTION DETECTED:</b></font><br>{errorMsg}")
        else:
            self.titleLabel.set_text(f"{tool.kind.upper()} COMPILER (Tier: {tool.tier})")
            self.consoleBox.set_text("Console ready...")

        self.panel.show()
        
    def close(self):
        self.isOpen = False
        self.currentTool = None
        self.panel.hide()

    def compileCode(self, unlockedConcepts=None, board=None):
        if self.currentTool is None:
            return
        
        self.currentTool.script.sourceCode = self.codeBox.get_text()
        # Pass player's unlocked concepts to the AST validator
        success = self.currentTool.script.compile(unlockedConcepts=unlockedConcepts)

        if success:
            audioManager.sfx("upgrade")
            if getattr(self.currentTool, "corrupted", False):
                self.currentTool.corrupted = False
                if board is not None:
                    board.dirty = True
                self.titleLabel.set_text(f"{self.currentTool.kind.upper()} COMPILER (Tier: {self.currentTool.tier})")
                self.consoleBox.set_text("<font color='#46C878'><b>Malware Purged!</b></font><br>Tower restored to friendly operation.")
            else:
                self.consoleBox.set_text("<font color='#46C878'><b>Compile Successful!</b></font><br>Tower logic updated.")
        
        else:
            audioManager.sfx("corrupt")
            errorMsg = self.currentTool.script.error
            self.consoleBox.set_text(f"<font color='#FF4646'><b>Compile Error:</b></font><br>{errorMsg}")

    def handleEvent(self, event, unlockedConcepts=None, board=None):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.compileBtn:
                self.compileCode(unlockedConcepts=unlockedConcepts, board=board)
                
            elif event.ui_element == self.closeBtn:
                audioManager.sfx("back")
                self.close()

        
