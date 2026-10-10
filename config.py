# config.py -- ALL tunable constants live here (UPPER_CASE).
# Shared file: add freely, but don't rename existing entries without telling the team.

# ---------------------------------------------------------------- display
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60

# ---------------------------------------------------------------- grid
TILE = 16            # pixels per tile
GRID_W = 60          # tiles
GRID_H = 40
BOARD_X = 16              # board's top-left pixel offset on screen
BOARD_Y = 16
BOARD_PX_W = GRID_W * TILE
BOARD_PX_H = GRID_H * TILE 
# Right-hand side panel (shop / editor) starts at x = BOARD_X + BOARD_PX_W + 16
# Bottom strip (console / HUD / graphs) starts at y = BOARD_Y + BOARD_PX_H + 16

# CPU occupies a small block on the right-middle of the board (top-left tile + size).
CPU_W = 2
CPU_H = 2
CPU_X = GRID_W // 2 - CPU_W // 2 
CPU_Y = GRID_H // 2 - CPU_H // 2 
CPU_MAX_HP = 100

# Bugs spawn on the left edge by default (director may use other edges).
SPAWN_EDGE = "all"

# ---------------------------------------------------------------- phases / timing
PHASE_MENU = "menu"
PHASE_BUILD = "build"
PHASE_WAVE = "wave"
PHASE_LAB = "lab"
PHASE_GAME_OVER = "gameOver"

SCRIPT_TICKS_PER_SECOND = 8      # how often tools run tick()
AI_TICK_SECONDS = 0.75           # pheromone / crowd update interval
DEMO_SEED = 1337
SEPARATION_RADIUS = 3
SEPARATION_WEIGHT = 5
SWARM_SEP_RADIUS = 1
SWARM_SEP_WEIGHT = 2

APPROACH_RANGE = 10.0
ATTACK_RANGE = .35

# ---------------------------------------------------------------- economy (bytes)
START_BYTES = 150
WAVE_CLEAR_BONUS = 25
SELL_REFUND = 0.5
REPAIR_COST_PER_HP = 0.5
FIX_CODE_COST = 15

# ---------------------------------------------------------------- tools
# cost, hp, range (tiles), dps
TOOL_STATS = {
    "turret":   {"cost": 50, "hp": 60,  "range": 5.0, "dps": 8.0},
    "firewall": {"cost": 30, "hp": 120, "range": 0.0, "dps": 0.0},
    "debugger": {"cost": 70, "hp": 40,  "range": 4.0, "dps": 0.0},
}
TURRET_TIERS = [
    # cycles per tick, damage per shot, range, shots per second
    {"cycles": 20, "damage": 4,  "range": 5.0, "fireRate": 2.0, "upgradeCost": 0},
    {"cycles": 40, "damage": 6,  "range": 5.5, "fireRate": 2.5, "upgradeCost": 60},
    {"cycles": 80, "damage": 9,  "range": 6.0, "fireRate": 3.0, "upgradeCost": 120},
]
PROJECTILE_SPEED = 12.0          # tiles per second
FIREWALL_MIN_LEN = 2
FIREWALL_MAX_LEN = 5

# ---------------------------------------------------------------- enemies
# hp, speed (tiles/sec), bytes reward, damage per second to tools/CPU
ENEMY_STATS = {
    "bug":        {"hp": 20,  "speed": 1.6, "reward": 5,  "dps": 4.0},
    "memoryLeak": {"hp": 120, "speed": 0.8, "reward": 20, "dps": 6.0},
    "zeroDay":    {"hp": 40,  "speed": 1.4, "reward": 15, "dps": 5.0},
    "injection":  {"hp": 10,  "speed": 2.8, "reward": 10, "dps": 0.0},
}
MEMORY_LEAK_SPLIT_COUNT = 3
BUG_DPS = ENEMY_STATS["bug"]["dps"]   # used by L_wall = tool.hp / BUG_DPS

# ---------------------------------------------------------------- AI: cost weights
# order of weights per enemy type: wall, fire, fear, crowd
AI_WEIGHTS = {
    "bug":        {"wall": 1.0, "fire": 0.2, "fear": 0.5, "crowd": 0.5},
    "memoryLeak": {"wall": 0.3, "fire": 0.0, "fear": 0.0, "crowd": 0.0},
    "zeroDay":    {"wall": 1.0, "fire": 1.0, "fear": 1.0, "crowd": 1.0},
    "injection":  {"wall": 0.0, "fire": 2.0, "fear": 2.0, "crowd": 1.5},
}
CROWD_CAP = 4.0
JUMP_COST = 3.0
PHEROMONE_DECAY = 0.97
PHEROMONE_CARRYOVER = 0.5        # fraction kept between waves
DIRECTOR_TEMPERATURE = 4.0
DIRECTOR_TEMP_MIN = 1.0
DIRECTOR_TEMP_MAX = 10.0
WAVEFRONT_SPEED = 0.6            # seconds for the wavefront replay
BENCH_ENEMY_COUNT = 50

# ---------------------------------------------------------------- scripting
CODE_UNLOCK_COSTS = {"if": 20, "for": 40, "while": 40, "memory": 30}

# ---------------------------------------------------------------- wave prefabs
WAVE_BASE_BUDGET = 20
WAVE_BUDGET_GROWTH = 1.25
ENEMY_COSTS   = {"bug": 2, "injection": 4, "zeroDay": 5, "memoryLeak": 8}
ENEMY_UNLOCK  = {"bug": 1, "injection": 3, "zeroDay": 4, "memoryLeak": 3}   # wave each is unlocked
ENEMY_WEIGHTS = {"bug": 6, "injection": 2, "zeroDay": 2, "memoryLeak": 1}   # how often each gets picked

SPAWN_INTERVAL_BASE = .8
SPAWN_INTERVAL_DECAY = .93
SPAWN_INTERVAL_FLOOR = .2

STRAGGLER_CHANCE = 0.1

# ---------------------------------------------------------------- colors
COLOR_BG = (14, 18, 24)
COLOR_GRID = (28, 36, 46)
COLOR_CPU = (70, 200, 120)
COLOR_TOOL = (90, 160, 255)
COLOR_ENEMY = (255, 90, 90)
COLOR_TEXT = (220, 230, 240)
COLOR_ERROR = (255, 70, 70)

