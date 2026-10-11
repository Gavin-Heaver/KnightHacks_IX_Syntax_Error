import math
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextBox
import config
from game.audio import audioManager

class ShopPanel:
    def __init__(self, uiManager):
        self.uiManager = uiManager
        self.selectedToolType = "debugger"
        self._lastSpecsHtml = None
        self.buildUI()

    def buildUI(self):
        # Main shop container panel - aligned with game board grid Y and height
        self.panel = UIPanel(
            relative_rect=pygame.Rect((980, config.BOARD_Y), (284, config.BOARD_PX_H)),
            manager=self.uiManager
        )

        # ----------------------------------------------------------------
        # 1. DEFENSIVE ARSENAL (Placement Tools)
        # ----------------------------------------------------------------
        self.paletteLabel = UILabel(
            relative_rect=pygame.Rect((10, 12), (264, 22)),
            text="DEFENSIVE ARSENAL",
            manager=self.uiManager,
            container=self.panel
        )

        self.btnDebugger = UIButton(
            relative_rect=pygame.Rect((10, 38), (264, 32)),
            text="DEBUGGER (50 B)",
            manager=self.uiManager,
            container=self.panel
        )
        self.btnTurret = self.btnDebugger  # backward compatibility alias

        self.btnFirewall = UIButton(
            relative_rect=pygame.Rect((10, 76), (264, 32)),
            text="FIREWALL (30 B)",
            manager=self.uiManager,
            container=self.panel
        )

        self.btnAntivirus = UIButton(
            relative_rect=pygame.Rect((10, 114), (264, 32)),
            text="ANTIVIRUS (70 B)",
            manager=self.uiManager,
            container=self.panel
        )

        # ----------------------------------------------------------------
        # 2. TOWER INSPECTOR & TACTICAL SPECS
        # ----------------------------------------------------------------
        self.inspectorLabel = UILabel(
            relative_rect=pygame.Rect((10, 162), (264, 22)),
            text="TOWER INSPECTOR",
            manager=self.uiManager,
            container=self.panel
        )

        self.infoLabel = UILabel(
            relative_rect=pygame.Rect((10, 188), (264, 22)),
            text="No Tower Selected",
            manager=self.uiManager,
            container=self.panel
        )

        # Action Buttons (Row 1: Upgrade & Sell)
        self.btnUpgrade = UIButton(
            relative_rect=pygame.Rect((10, 218), (128, 32)),
            text="UPGRADE",
            manager=self.uiManager,
            container=self.panel
        )
        self.btnSell = UIButton(
            relative_rect=pygame.Rect((146, 218), (128, 32)),
            text="SELL",
            manager=self.uiManager,
            container=self.panel
        )

        # Action Buttons (Row 2: Repair & Compiler)
        self.btnRepair = UIButton(
            relative_rect=pygame.Rect((10, 256), (128, 32)),
            text="REPAIR",
            manager=self.uiManager,
            container=self.panel
        )
        self.btnCompiler = UIButton(
            relative_rect=pygame.Rect((146, 256), (128, 32)),
            text="COMPILER",
            manager=self.uiManager,
            container=self.panel
        )

        # Tactical Specs & Next Tier Preview Box
        self.specsBox = UITextBox(
            html_text="",
            relative_rect=pygame.Rect((10, 298), (264, 205)),
            manager=self.uiManager,
            container=self.panel
        )

        # ----------------------------------------------------------------
        # 3. SYSTEM CORE (CPU)
        # ----------------------------------------------------------------
        self.sysLabel = UILabel(
            relative_rect=pygame.Rect((10, 520), (264, 22)),
            text="SYSTEM CORE (CPU)",
            manager=self.uiManager,
            container=self.panel
        )

        self.cpuStatusLabel = UILabel(
            relative_rect=pygame.Rect((10, 546), (264, 22)),
            text="CPU: 100/100 HP",
            manager=self.uiManager,
            container=self.panel
        )

        self.btnExpandCPU = UIButton(
            relative_rect=pygame.Rect((10, 574), (264, 34)),
            text="EXPAND CPU (+25 HP | 50 B)",
            manager=self.uiManager,
            container=self.panel
        )

    def _buildSpecsHtml(self, selectedTool, gameState):
        """Builds formatted HTML stats for either the selected tower or the equipped tool."""
        if selectedTool is not None:
            kind = selectedTool.kind.lower()
            tierNum = getattr(selectedTool, "tier", 0) + 1
            hpInt = int(selectedTool.hp)
            maxHpInt = int(selectedTool.maxHp)
            hpPct = int((selectedTool.hp / selectedTool.maxHp) * 100) if selectedTool.maxHp > 0 else 0
            hpColor = "#44FF88" if hpPct > 50 else ("#FFAA33" if hpPct > 25 else "#FF4444")
            isCorrupted = getattr(selectedTool, "corrupted", False)

            lines = [
                f"<b><font color='#44DDFF'>{selectedTool.kind.upper()}</font></b> (Tier {tierNum})",
                f"<b>Health:</b> <font color='{hpColor}'>{hpInt}/{maxHpInt} HP ({hpPct}%)</font>"
            ]

            if isCorrupted:
                lines.append("<font color='#FF4444'><b>MALWARE ACTIVE!</b><br>Attacking allies. Open COMPILER to purge.</font>")
            else:
                lines.append("<font color='#44FF88'><b>ONLINE & OPERATIONAL</b></font>")

            if kind in ("debugger", "turret"):
                wType = getattr(selectedTool, "weapon", "bullet")
                weaponName = "Laser Beam" if wType == "laser" else ("Homing Bullets" if wType == "homing" else "Standard Bullets")
                fireRate = getattr(selectedTool, "fireRate", 2.0)
                dmg = getattr(selectedTool, "damage", 4.0)
                dps = round(dmg * fireRate, 1) if wType != "laser" else 18.0
                lines.append(f"<b>Weapon:</b> {weaponName}")
                lines.append(f"<b>Range:</b> {selectedTool.range} tiles | <b>Rate:</b> {fireRate}/s")
                lines.append(f"<b>Damage:</b> {dmg} ({dps} DPS)")
                lines.append(f"<b>Cycles:</b> {getattr(selectedTool, 'cycleBudget', 20)} / tick")

                tiers = config.TOOL_TIERS.get(kind, [])
                currTier = getattr(selectedTool, "tier", 0)
                if currTier < len(tiers) - 1:
                    nextCost = tiers[currTier + 1]["upgradeCost"]
                    if currTier == 0:
                        lines.append(f"<font color='#FFCC44'><b>Next (T2):</b> +50% dmg, 6.5 rng, homing ({nextCost} B)</font>")
                    elif currTier == 1:
                        lines.append(f"<font color='#FFCC44'><b>Next (T3):</b> Laser beam, 10.0 rng, 80 cyc ({nextCost} B)</font>")
                else:
                    lines.append("<font color='#88FFFF'><b>Max Tier Reached</b></font>")

            elif kind == "antivirus":
                dps = getattr(selectedTool, "dps", 4.0)
                currTier = getattr(selectedTool, "tier", 0)
                slowDesc = "No slow" if currTier == 0 else ("-50% focus / -20% AoE" if currTier == 1 else "-75% focus / -40% AoE")
                lines.append("<b>Aura:</b> Passive Damage & Slow Field")
                lines.append(f"<b>Range:</b> {selectedTool.range} tiles | <b>DPS:</b> {dps}")
                lines.append(f"<b>Slowdown:</b> {slowDesc}")
                lines.append(f"<b>Cycles:</b> {getattr(selectedTool, 'cycleBudget', 30)} / tick")

                tiers = config.TOOL_TIERS.get(kind, [])
                currTier = getattr(selectedTool, "tier", 0)
                if currTier < len(tiers) - 1:
                    nextCost = tiers[currTier + 1]["upgradeCost"]
                    if currTier == 0:
                        lines.append(f"<font color='#FFCC44'><b>Next (T2):</b> +25% DPS, 50% slow ({nextCost} B)</font>")
                    elif currTier == 1:
                        lines.append(f"<font color='#FFCC44'><b>Next (T3):</b> +50% DPS, 75% slow ({nextCost} B)</font>")
                else:
                    lines.append("<font color='#88FFFF'><b>Max Tier Reached</b></font>")

            elif kind == "firewall":
                currTier = getattr(selectedTool, "tier", 0)
                maxLen = getattr(selectedTool, "maxLen", 3)
                dps = getattr(selectedTool, "dps", 0.0)
                dmgDesc = f"Damaging ({dps} DPS)" if getattr(selectedTool, "isDamaging", False) else "Barrier only (0 DPS)"
                lines.append("<b>Type:</b> Plasma Barrier Grid")
                lines.append(f"<b>Beam Reach:</b> Up to {maxLen} tiles")
                lines.append(f"<b>Wall Damage:</b> {dmgDesc}")

                tiers = config.TOOL_TIERS.get(kind, [])
                if currTier < len(tiers) - 1:
                    nextCost = tiers[currTier + 1]["upgradeCost"]
                    if currTier == 0:
                        lines.append(f"<font color='#FFCC44'><b>Next (T2):</b> Plasma link up to 5 tiles ({nextCost} B)</font>")
                    elif currTier == 1:
                        lines.append(f"<font color='#FFCC44'><b>Next (T3):</b> 7-tile link + 15 DPS Wall ({nextCost} B)</font>")
                else:
                    lines.append("<font color='#88FFFF'><b>Max Tier Reached</b></font>")

            lines.append("<font color='#88A0B0'><i>Controls: Click empty tile to deselect.</i></font>")
            return "<br>".join(lines)

        else:
            eq = self.selectedToolType
            lines = []
            if eq in ("debugger", "turret"):
                lines = [
                    "<b><font color='#44DDFF'>DEBUGGER OVERVIEW</font></b>",
                    "<b>Deploy Cost:</b> 50 B | <b>HP:</b> 30",
                    "<b>Role:</b> Precision Attacker & Turret",
                    "&bull; <b>T1:</b> Bullets, 5.0 range, 4 dmg",
                    "&bull; <b>T2:</b> Homing, 6.5 range, 6 dmg",
                    "&bull; <b>T3:</b> Laser beam, 10.0 range",
                    "<br><font color='#99BBDD'><b>Controls & Deployment:</b></font>",
                    "&bull; Click any empty tile to deploy",
                    "&bull; Click deployed tower to upgrade/sell",
                    "&bull; Open Compiler to customize logic"
                ]
            elif eq == "firewall":
                lines = [
                    "<b><font color='#44DDFF'>FIREWALL OVERVIEW</font></b>",
                    "<b>Deploy Cost:</b> 30 B | <b>HP:</b> 120",
                    "<b>Role:</b> High-Durability Wall & Barrier",
                    "&bull; <b>T1:</b> 3-tile Plasma Link",
                    "&bull; <b>T2:</b> 5-tile Plasma Link",
                    "&bull; <b>T3:</b> 7-tile Link + 15 DPS Wall",
                    "<br><font color='#99BBDD'><b>Controls & Deployment:</b></font>",
                    "&bull; Click empty tile to deploy post",
                    "&bull; Connects plasma beams between posts",
                    "&bull; Click post to inspect or upgrade"
                ]
            elif eq == "antivirus":
                lines = [
                    "<b><font color='#44DDFF'>ANTIVIRUS OVERVIEW</font></b>",
                    "<b>Deploy Cost:</b> 70 B | <b>HP:</b> 40",
                    "<b>Role:</b> Scanner, Attack All & Slow Malware",
                    "&bull; <b>T1:</b> 4.0 Range, 4.0 AoE DPS",
                    "&bull; <b>T2:</b> 5.0 DPS, 50% bug slow",
                    "&bull; <b>T3:</b> 6.0 DPS, 75% heavy slow",
                    "<br><font color='#99BBDD'><b>Controls & Deployment:</b></font>",
                    "&bull; Click empty tile to deploy",
                    "&bull; Reveals hidden zero-day bugs",
                    "&bull; Click tower to inspect or upgrade"
                ]
            return "<br>".join(lines)

    def update(self, gameState, selectedTool):
        # Update palette buttons with equipped cursor indicator
        self.btnDebugger.set_text(f"{'► ' if self.selectedToolType == 'debugger' else ''}DEBUGGER (50 B)")
        self.btnFirewall.set_text(f"{'► ' if self.selectedToolType == 'firewall' else ''}FIREWALL (30 B)")
        self.btnAntivirus.set_text(f"{'► ' if self.selectedToolType == 'antivirus' else ''}ANTIVIRUS (70 B)")

        if selectedTool is not None:
            corruptStr = " [INFECTED!]" if getattr(selectedTool, "corrupted", False) else ""
            tierStr = f" (T{selectedTool.tier + 1})" if hasattr(selectedTool, "tier") else ""
            self.infoLabel.set_text(f"{selectedTool.kind.upper()}{tierStr}{corruptStr}")

            # Upgrade button
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

            # Sell button
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

        # Update rich tactical specs box
        specsHtml = self._buildSpecsHtml(selectedTool, gameState)
        if specsHtml != self._lastSpecsHtml:
            self.specsBox.set_text(specsHtml)
            self._lastSpecsHtml = specsHtml

        # Update CPU status
        pct = int((gameState.cpuHp / gameState.cpuMaxHp) * 100) if gameState.cpuMaxHp > 0 else 0
        self.cpuStatusLabel.set_text(f"CPU Health: {int(gameState.cpuHp)}/{int(gameState.cpuMaxHp)} ({pct}%)")

        # Update CPU Expand button state
        if gameState.canAfford(50):
            self.btnExpandCPU.enable()
        else:
            self.btnExpandCPU.disable()

    def handleEvent(self, event, gameState, selectedTool, board):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Grid Placement Selection
            if event.ui_element == self.btnDebugger:
                self.selectedToolType = "debugger"
                audioManager.sfx("select")
            elif event.ui_element == self.btnFirewall:
                self.selectedToolType = "firewall"
                audioManager.sfx("select")
            elif event.ui_element == self.btnAntivirus:
                self.selectedToolType = "antivirus"
                audioManager.sfx("select")

            # Upgrade
            elif event.ui_element == self.btnUpgrade and selectedTool is not None:
                tiers = config.TOOL_TIERS.get(selectedTool.kind)
                if tiers and hasattr(selectedTool, "tier") and selectedTool.tier < len(tiers) - 1:
                    cost = tiers[selectedTool.tier + 1]["upgradeCost"]
                    if gameState.spendBytes(cost):
                        selectedTool.upgrade()
                        board.dirty = True
                        audioManager.sfx("upgrade")

            # Repair
            elif event.ui_element == self.btnRepair and selectedTool is not None:
                missingHp = selectedTool.maxHp - selectedTool.hp
                if missingHp > 0.01:
                    repairCost = max(1, int(math.ceil(missingHp * config.REPAIR_COST_PER_HP)))
                    if gameState.spendBytes(repairCost):
                        selectedTool.hp = float(selectedTool.maxHp)
                        audioManager.sfx("upgrade")

            # Sell
            elif event.ui_element == self.btnSell and selectedTool is not None:
                board.remove(selectedTool.x, selectedTool.y)
                gameState.refundBytes(selectedTool.spent)
                audioManager.sfx("back")
                return "deselected"

            # Open compiler
            elif event.ui_element == self.btnCompiler and selectedTool is not None:
                if getattr(selectedTool, "programmable", False):
                    audioManager.sfx("select")
                    return "open_compiler"

            # Expand CPU
            elif event.ui_element == self.btnExpandCPU:
                if gameState.upgradeCpuMaxHp(25, 50):
                    audioManager.sfx("upgrade")

        return None