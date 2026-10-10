import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextBox
import config

class ShopPanel:
    def __init__(self, uiManager):
        self.uiManager = uiManager
        self.selectedToolType = "turret"
        self.buildUI()

    def buildUI(self):
        self.panel = UIPanel(relative_rect=pygame.Rect((980, 56), (284, 648)), manager=self.uiManager)

        #Defensive Purchases
        self.paletteLabel = UILabel(
            relative_rect=pygame.Rect((10, 10), (264, 25)), text="DEFENSIVE BITS",manager=self.uiManager,container=self.panel
        )

        self.btnTurret = UIButton(
            relative_rect=pygame.Rect((10, 40), (264, 34)),text="TURRET (50 B)",manager=self.uiManager,container=self.panel
        )

        self.btnFirewall = UIButton(relative_rect=pygame.Rect((10, 80), (264, 34)), text="FIREWALL (30 B)", manager=self.uiManager, container=self.panel
        )

        self.btnDebugger = UIButton(
            relative_rect=pygame.Rect((10, 120), (264, 34)), text="DEBUGGER (70 B)", manager=self.uiManager, container=self.panel
        )   

        #Tower Information
        self.inspectorLabel = UILabel(
            relative_rect=pygame.Rect((10, 175), (264, 25)), text="SELECTED TOWER",manager=self.uiManager,container=self.panel
        )

        self.infoLabel = UILabel(
            relative_rect=pygame.Rect((10, 205), (264, 25)), text="No Tower Selected", manager=self.uiManager, container=self.panel
        )

        self.btnUpgrade = UIButton(
            relative_rect=pygame.Rect((10, 235), (264, 34)), text="UPGRADE TIER", manager=self.uiManager, container=self.panel
        )

        self.btnSell = UIButton(
            relative_rect=pygame.Rect((10, 275), (264, 34)), text="SELL (+50%)", manager=self.uiManager, container=self.panel
        )

        #coding Unlocks
        self.unlocksLabel = UILabel(
            relative_rect=pygame.Rect((10, 330), (264, 25)), text="PYTHON UNLOCKS", manager=self.uiManager, container=self.panel
        )

        self.btnUnlockFor = UIButton(
            relative_rect=pygame.Rect((10, 360), (264, 34)), text="for Loops (40 B)", manager=self.uiManager, container=self.panel
        )

        self.btnUnlockWhile = UIButton(
            relative_rect=pygame.Rect((10, 400), (264, 34)), text="while Loops (40 B)", manager=self.uiManager, container=self.panel
        )

        self.btnUnlockMemory = UIButton(
            relative_rect=pygame.Rect((10, 440), (264, 34)), text="memory Dict (30 B)", manager=self.uiManager, container=self.panel
        )

        #Status at bottom
        self.statusLabel = UILabel(
            relative_rect=pygame.Rect((10, 500), (264, 30)), text="Click an empty tile to build", manager=self.uiManager, container=self.panel
        )

    def update(self, gameState, selectedTool):
        #Update status text to show what tool you have equiped
        self.statusLabel.set_text(f"Equipped: {self.selectedToolType.upper()}")

        #Update Selected Tower
        if selectedTool is not None:
            self.infoLabel.set_text(f"{selectedTool.kind.upper()} (Tier {selectedTool.tier})")

            # Check if an upgrade is available
            if hasattr(selectedTool, "tier") and selectedTool.tier < len(config.TURRET_TIERS) - 1:
                cost = config.TURRET_TIERS[selectedTool.tier + 1]["upgradeCost"]
                self.btnUpgrade.set_text(f"UPGRADE ({cost} B)")

            else:
                self.btnUpgrade.set_text("MAX TIER")

            # Show refund amount
            refundVal = int(selectedTool.spent * config.SELL_REFUND)
            self.btnSell.set_text(f"SELL (+{refundVal} B)")

        else:
            self.infoLabel.set_text("No Tower Selected")
            self.btnUpgrade.set_text("UPGRADE TIER")
            self.btnSell.set_text("SELL (+50%)")

        # 3. Update Concept Unlock buttons if already purchased
        if "for" in gameState.unlockedConcepts:
            self.btnUnlockFor.set_text("[for] UNLOCKED")

        if "while" in gameState.unlockedConcepts:
            self.btnUnlockWhile.set_text("[while] UNLOCKED")

        if "memory" in gameState.unlockedConcepts:
            self.btnUnlockMemory.set_text("[memory] UNLOCKED")

    def handleEvent(self, event, gameState, selectedTool, board):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Grid Placement
            if event.ui_element == self.btnTurret:
                self.selectedToolType = "turret"
            elif event.ui_element == self.btnFirewall:
                self.selectedToolType = "firewall"
            elif event.ui_element == self.btnDebugger:
                self.selectedToolType = "debugger"

            #Concept unlocks
            elif event.ui_element == self.btnUnlockFor:
                gameState.unlockConcept("for")
            elif event.ui_element == self.btnUnlockWhile:
                gameState.unlockConcept("while")
            elif event.ui_element == self.btnUnlockMemory:
                gameState.unlockConcept("memory")

            #upgrades
            elif event.ui_element == self.btnUpgrade and selectedTool is not None:
                if hasattr(selectedTool, "tier") and selectedTool.tier < len(config.TURRET_TIERS) - 1:
                    cost = config.TURRET_TIERS[selectedTool.tier + 1]["upgradeCost"]
                    if gameState.spendBytes(cost):
                        selectedTool.upgrade()

            #sell
            elif event.ui_element == self.btnSell and selectedTool is not None:
                board.remove(selectedTool.x, selectedTool.y)
                gameState.refundBytes(selectedTool.spent)
                return "deselected"
        
        return None