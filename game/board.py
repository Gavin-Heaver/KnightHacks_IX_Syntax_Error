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