import math
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextBox
import config

class ShopPanel:
    def __init__(self, uiManager):
        self.uiManager = uiManager
        self.selectedToolType = "debugger"
        self.buildUI()

    def buildUI(self):
        self.panel = UIPanel(relative_rect=pygame.Rect((980, 56), (284, 648)), manager=self.uiManager)

        #Defensive Purchases
        self.paletteLabel = UILabel(
            relative_rect=pygame.Rect((10, 8), (264, 25)), text="DEFENSIVE BITS",manager=self.uiManager,container=self.panel
        )

        self.btnDebugger = UIButton(
            relative_rect=pygame.Rect((10, 36), (264, 32)),text="DEBUGGER (50 B)",manager=self.uiManager,container=self.panel
        )
        self.btnTurret = self.btnDebugger  # alias

        self.btnFirewall = UIButton(relative_rect=pygame.Rect((10, 72), (264, 32)), text="FIREWALL (30 B)", manager=self.uiManager, container=self.panel
        )

        self.btnAntivirus = UIButton(
            relative_rect=pygame.Rect((10, 108), (264, 32)), text="ANTIVIRUS (70 B)", manager=self.uiManager, container=self.panel
        )   


        #Tower Information
        self.inspectorLabel = UILabel(
            relative_rect=pygame.Rect((10, 148), (264, 25)), text="SELECTED TOWER",manager=self.uiManager,container=self.panel
        )

        self.infoLabel = UILabel(
            relative_rect=pygame.Rect((10, 173), (264, 25)), text="No Tower Selected", manager=self.uiManager, container=self.panel
        )

        self.btnUpgrade = UIButton(
            relative_rect=pygame.Rect((10, 203), (128, 32)), text="UPGRADE", manager=self.uiManager, container=self.panel
        )
        self.btnSell = UIButton(
            relative_rect=pygame.Rect((146, 203), (128, 32)), text="SELL", manager=self.uiManager, container=self.panel
        )
        self.btnRepair = UIButton(
            relative_rect=pygame.Rect((10, 239), (128, 32)), text="REPAIR", manager=self.uiManager, container=self.panel
        )
        self.btnCompiler = UIButton(
            relative_rect=pygame.Rect((146, 239), (128, 32)), text="COMPILER", manager=self.uiManager, container=self.panel
        )

        #coding Unlocks
        self.unlocksLabel = UILabel(
            relative_rect=pygame.Rect((10, 280), (264, 25)), text="PYTHON UNLOCKS", manager=self.uiManager, container=self.panel
        )

        self.btnUnlockFor = UIButton(
            relative_rect=pygame.Rect((10, 308), (264, 30)), text="for Loops (40 B)", manager=self.uiManager, container=self.panel
        )

        self.btnUnlockWhile = UIButton(
            relative_rect=pygame.Rect((10, 342), (264, 30)), text="while Loops (40 B)", manager=self.uiManager, container=self.panel
        )

        self.btnUnlockMemory = UIButton(
            relative_rect=pygame.Rect((10, 376), (264, 30)), text="memory Dict (30 B)", manager=self.uiManager, container=self.panel
        )

        #System / CPU Upgrades
        self.sysLabel = UILabel(
            relative_rect=pygame.Rect((10, 416), (264, 25)), text="SYSTEM UPGRADES", manager=self.uiManager, container=self.panel
        )

        self.btnExpandCPU = UIButton(
            relative_rect=pygame.Rect((10, 444), (264, 32)), text="EXPAND CPU (+25 HP | 50 B)", manager=self.uiManager, container=self.panel
        )

        #Status at bottom
        self.statusLabel = UILabel(
            relative_rect=pygame.Rect((10, 492), (264, 28)), text="Click an empty tile to build", manager=self.uiManager, container=self.panel
        )

    def update(self, gameState, selectedTool):
        #Update status text to show what tool you have equiped
        self.statusLabel.set_text(f"Equipped: {self.selectedToolType.upper()}")

        if selectedTool is not None:
            corruptStr = " [INFECTED!]" if getattr(selectedTool, "corrupted", False) else ""
            tierStr = f" (T{selectedTool.tier})" if hasattr(selectedTool, "tier") else ""
            self.infoLabel.set_text(f"{selectedTool.kind.upper()}{tierStr}{corruptStr}  HP:{int(selectedTool.hp)}/{selectedTool.maxHp}")
            # Check if an upgrade is available
            tiers = config.TOOL_TIERS.get(selectedTool.kind)
            if tiers and hasattr(selectedTool, "tier") and selectedTool.tier < len(tiers) - 1:
                cost = tiers[selectedTool.tier + 1]["upgradeCost"]
                self.btnUpgrade.set_text(f"UPGRADE ({cost} B)")
                if gameState.canAfford(cost):
                    self.btnUpgrade.enable()
                else:
                    self.btnUpgrade.disable()
            else:
                self.btnUpgrade.set_text("MAX TIER" if (tiers and hasattr(selectedTool, "tier")) else "NO UPGRADE")
                self.btnUpgrade.disable()

            # Show refund amount
            refundVal = int(selectedTool.spent * config.SELL_REFUND)
            self.btnSell.set_text(f"SELL (+{refundVal} B)")
            self.btnSell.enable()

            # Repair button
            missingHp = selectedTool.maxHp - selectedTool.hp
            if missingHp > 0.01:
                repairCost = max(1, int(math.ceil(missingHp * config.REPAIR_COST_PER_HP)))
                self.btnRepair.set_text(f"REPAIR ({repairCost} B)")
                if gameState.canAfford(repairCost):
                    self.btnRepair.enable()
                else:
                    self.btnRepair.disable()
            else:
                self.btnRepair.set_text("FULL HP")
                self.btnRepair.disable()

            # Dynamic compiler button
            if getattr(selectedTool, "programmable", False):
                if getattr(selectedTool, "corrupted", False):
                    self.btnCompiler.set_text("DEBUG/FIX!")
                else:
                    self.btnCompiler.set_text("COMPILER")
                self.btnCompiler.enable()
            else:
                self.btnCompiler.set_text("NO SCRIPT")
                self.btnCompiler.disable()

        else:
            self.infoLabel.set_text("No Tower Selected")
            self.btnUpgrade.set_text("UPGRADE")
            self.btnUpgrade.disable()
            self.btnSell.set_text("SELL")
            self.btnSell.disable()
            self.btnRepair.set_text("REPAIR")
            self.btnRepair.disable()
            self.btnCompiler.set_text("COMPILER")
            self.btnCompiler.disable()

        # Update Concept Unlock buttons state
        if "for" in gameState.unlockedConcepts:
            self.btnUnlockFor.set_text("[for] UNLOCKED")
            self.btnUnlockFor.disable()
        else:
            self.btnUnlockFor.set_text("for Loops (40 B)")
            self.btnUnlockFor.enable()

        if "while" in gameState.unlockedConcepts:
            self.btnUnlockWhile.set_text("[while] UNLOCKED")
            self.btnUnlockWhile.disable()
        else:
            self.btnUnlockWhile.set_text("while Loops (40 B)")
            self.btnUnlockWhile.enable()

        if "memory" in gameState.unlockedConcepts:
            self.btnUnlockMemory.set_text("[memory] UNLOCKED")
            self.btnUnlockMemory.disable()
        else:
            self.btnUnlockMemory.set_text("memory Dict (30 B)")
            self.btnUnlockMemory.enable()

        # Update CPU Expand button state
        if gameState.canAfford(50):
            self.btnExpandCPU.enable()
        else:
            self.btnExpandCPU.disable()

    def handleEvent(self, event, gameState, selectedTool, board):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Grid Placement
            if event.ui_element == self.btnDebugger:
                self.selectedToolType = "debugger"
            elif event.ui_element == self.btnFirewall:
                self.selectedToolType = "firewall"
            elif event.ui_element == self.btnAntivirus:
                self.selectedToolType = "antivirus"


            #Concept unlocks
            elif event.ui_element == self.btnUnlockFor:
                gameState.unlockConcept("for")
            elif event.ui_element == self.btnUnlockWhile:
                gameState.unlockConcept("while")
            elif event.ui_element == self.btnUnlockMemory:
                gameState.unlockConcept("memory")

            #upgrades
            elif event.ui_element == self.btnUpgrade and selectedTool is not None:
                tiers = config.TOOL_TIERS.get(selectedTool.kind)
                if tiers and hasattr(selectedTool, "tier") and selectedTool.tier < len(tiers) - 1:
                    cost = tiers[selectedTool.tier + 1]["upgradeCost"]
                    if gameState.spendBytes(cost):
                        selectedTool.upgrade()
                        board.dirty = True

            #repair
            elif event.ui_element == self.btnRepair and selectedTool is not None:
                missingHp = selectedTool.maxHp - selectedTool.hp
                if missingHp > 0.01:
                    repairCost = max(1, int(math.ceil(missingHp * config.REPAIR_COST_PER_HP)))
                    if gameState.spendBytes(repairCost):
                        selectedTool.hp = float(selectedTool.maxHp)

            #sell
            elif event.ui_element == self.btnSell and selectedTool is not None:
                board.remove(selectedTool.x, selectedTool.y)
                gameState.refundBytes(selectedTool.spent)
                return "deselected"

            #open compiler
            elif event.ui_element == self.btnCompiler and selectedTool is not None:
                if getattr(selectedTool, "programmable", False):
                    return "open_compiler"

            #expand CPU
            elif event.ui_element == self.btnExpandCPU:
                gameState.upgradeCpuMaxHp(25, 50)

        return None