# game/board.py -- grid, tiles, tool placement, `dirty` flag.
# Coordinates: tile (x, y), 0 <= x < GRID_W, 0 <= y < GRID_H, y grows downward.
# Entities (enemies, projectiles) use float tile units: tile (i, j) covers
# [i, i+1) x [j, j+1); its center is (i + 0.5, j + 0.5).

import config


class Board:
    def __init__(self, width=config.GRID_W, height=config.GRID_H):
        self.width = width
        self.height = height
        self.tools = [[None] * width for _ in range(height)]   # tools[y][x]
        self.cpuTiles = [
            (config.CPU_X + dx, config.CPU_Y + dy)
            for dy in range(config.CPU_H)
            for dx in range(config.CPU_W)
        ]
        self.dirty = True       # True after any change -> flow fields get rebuilt
        self.hpChanged = False  # True after a tool takes damage -> fields refreshed on the next AI tick

    # ------------------------------------------------------------ queries
    def inBounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def toolAt(self, x, y):
        if not self.inBounds(x, y):
            return None
        return self.tools[y][x]

    def isCpu(self, x, y):
        return (x, y) in self.cpuTiles

    def isBuildable(self, x, y):
        return self.inBounds(x, y) and not self.isCpu(x, y) and self.toolAt(x, y) is None

    def neighbors(self, x, y):
        """4-way neighbors that are inside the grid."""
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self.inBounds(nx, ny):
                yield nx, ny

    def allTools(self):
        """Unique tools on the board (a multi-tile tool is listed once per tile it owns)."""
        seen = []
        for row in self.tools:
            for tool in row:
                if tool is not None and tool not in seen:
                    seen.append(tool)
        return seen

    # ------------------------------------------------------------ changes
    def place(self, tool, x, y):
        """Put `tool` on (x, y). Returns True on success, False if blocked."""
        if not self.isBuildable(x, y):
            return False
        tool.x, tool.y = x, y
        self.tools[y][x] = tool
        self.dirty = True
        return True

    def remove(self, x, y):
        """Remove and return the tool at (x, y) (or None)."""
        tool = self.toolAt(x, y)
        if tool is not None:
            self.tools[y][x] = None
            self.dirty = True
        return tool

    # ------------------------------------------------------------ plasma walls
    def _calcPlasma(self):
        links = []
        tiles = set()
        damagingTiles = set()
        firewalls = [t for t in self.allTools() if getattr(t, "kind", "") == "firewall"]
        firewalls.sort(key=lambda f: (f.x, f.y))

        for i in range(len(firewalls)):
            f1 = firewalls[i]
            for j in range(i + 1, len(firewalls)):
                f2 = firewalls[j]
                maxAllowed = min(getattr(f1, "maxLen", 3), getattr(f2, "maxLen", 3))

                # Same X (vertical plasma wall)
                if f1.x == f2.x:
                    dy = abs(f1.y - f2.y)
                    if 1 < dy <= maxAllowed:
                        minY, maxY = min(f1.y, f2.y), max(f1.y, f2.y)
                        intermediate = [(f1.x, y) for y in range(minY + 1, maxY)]
                        if all(self.tools[y][f1.x] is None and not self.isCpu(f1.x, y) for _, y in intermediate):
                            isDamaging = getattr(f1, "isDamaging", False) or getattr(f2, "isDamaging", False)
                            links.append(((f1.x, f1.y), (f2.x, f2.y), isDamaging))
                            tiles.update(intermediate)
                            if isDamaging:
                                damagingTiles.update(intermediate)

                # Same Y (horizontal plasma wall)
                elif f1.y == f2.y:
                    dx = abs(f1.x - f2.x)
                    if 1 < dx <= maxAllowed:
                        minX, maxX = min(f1.x, f2.x), max(f1.x, f2.x)
                        intermediate = [(x, f1.y) for x in range(minX + 1, maxX)]
                        if all(self.tools[f1.y][x] is None and not self.isCpu(x, f1.y) for x, _ in intermediate):
                            isDamaging = getattr(f1, "isDamaging", False) or getattr(f2, "isDamaging", False)
                            links.append(((f1.x, f1.y), (f2.x, f2.y), isDamaging))
                            tiles.update(intermediate)
                            if isDamaging:
                                damagingTiles.update(intermediate)

        return links, tiles, damagingTiles

    def getPlasma(self):
        if self.dirty or not hasattr(self, "_cachedPlasmaLinks"):
            self._cachedPlasmaLinks, self._cachedPlasmaTiles, self._cachedDamagingTiles = self._calcPlasma()
        return self._cachedPlasmaLinks, self._cachedPlasmaTiles, self._cachedDamagingTiles

    def isPlaceable(self, x, y):
        m = config.BUILD_MARGIN
        return (m <= x < self.width - m and m <= y < self.height - m and self.isBuildable(x, y))

    @property
    def plasmaTiles(self):
        _, tiles, _ = self.getPlasma()
        return tiles

    @property
    def plasmaLinks(self):
        links, _, _ = self.getPlasma()
        return links

    @property
    def damagingPlasmaTiles(self):
        _, _, damTiles = self.getPlasma()
        return damTiles