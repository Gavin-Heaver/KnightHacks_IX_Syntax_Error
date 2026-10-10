import config
import random

from entities.enemy import Enemy

MODIFIERS = ["normal", "swarm", "heavy", "rush", "flank"]

EDGES = ["top", "bottom", "left", "right"]
OPPOSITE_EDGE = {"top":"bottom", "bottom":"top", "left":"right", "right":"left"}
ADJACENT_EDGE = {"top":["left", "right"], "bottom":["left", "right"], "left":["top","bottom"], "right":["top", "bottom"]}

def generateWave(waveNumber, lastModifier=None):
  #wave modifier- only normal is wave 1 or 2
  if waveNumber < 3:
    modifier = "normal"
  else:
    options = [m for m in MODIFIERS if m == "normal" or m != lastModifier]
    modifier = random.choice(options)

  #calculating budget
  if modifier == "swarm":
    budget = (config.WAVE_BASE_BUDGET * config.WAVE_BUDGET_GROWTH ** (waveNumber - 1)) * 1.3
  else:
    budget = config.WAVE_BASE_BUDGET * config.WAVE_BUDGET_GROWTH ** (waveNumber - 1)

  #determining enemy types allowed
  if modifier == "swarm":
    allowedTypes = ["bug"]
  else:
    allowedTypes = ["bug"]
    if waveNumber >= 3:
      allowedTypes.extend(["injection", "memoryLeak"])
    if waveNumber >= 4:
      allowedTypes.append("zeroDay")

  #determining enemy weights
  weights = dict(config.ENEMY_WEIGHTS)
  if modifier == "heavy":
    weights["memoryLeak"] *= 4

  #initializing spawn queue
  queue = []

  cheapest = min(config.ENEMY_COSTS[t]for t in allowedTypes)
  while budget >= cheapest:
    affordable = [t for t in allowedTypes if config.ENEMY_COSTS[t] <= budget]
    t = random.choices(affordable, weights=[weights[a] for a in affordable])[0]
    queue.append(t)
    budget -= config.ENEMY_COSTS[t]

  interval = config.SPAWN_INTERVAL_BASE * config.SPAWN_INTERVAL_DECAY ** (waveNumber - 1)

  if modifier == "rush":
    interval *= 0.5
  elif modifier == "heavy":
    interval *= 1.3

  interval = max(config.SPAWN_INTERVAL_FLOOR, interval)

  edge = random.choice(EDGES)
  if modifier == "flank":
    edges = [edge, OPPOSITE_EDGE[edge]]
  else:
    edges = [edge, random.choice(ADJACENT_EDGE[edge])]

  return {"queue": queue, "interval": interval, "edges": edges, "modifier": modifier}

def randomEdgeTile(board, edges):
  """A random open tile on one of the given edges."""
  tiles = []
  if "top" in edges:
    tiles += [(x, 0) for x in range(board.width)]
  if "bottom" in edges:
    tiles += [(x, board.height - 1) for x in range(board.width)]
  if "left" in edges:
    tiles += [(0, y) for y in range(board.height)]
  if "right" in edges:
    tiles += [(board.width - 1, y) for y in range(board.height)]

  openTiles = [t for t in tiles if board.isBuildable(*t)]
  if not openTiles:
      return randomEdgeTile(board, EDGES)
  return random.choice(openTiles)

class WaveSpawner:
    def __init__(self):
        self.queue = []            # enemy types still waiting to spawn
        self.interval = 1.0        # seconds between spawns
        self.timer = 0.0           # countdown to the next spawn
        self.edges = []            # this wave's main edges
        self.modifier = "normal"   # this wave's modifier (also used as "last" next wave)
        self.active = False        # True while a wave is running

    def start(self, waveNumber):
        wave = generateWave(waveNumber, self.modifier)
        self.queue = wave["queue"]
        self.interval = wave["interval"]
        self.edges = wave["edges"]
        self.modifier = wave["modifier"]
        self.timer = 0.0           # 0 = first enemy spawns immediately
        self.active = True

    def update(self, dt, board, enemies):
        if not self.active or not self.queue:
          return

        self.timer -= dt
        if self.timer > 0:
          return

        enemyType = self.queue.pop(0)
      
        if random.random() <= config.STRAGGLER_CHANCE:
          otherEdges = [e for e in EDGES if e not in self.edges]
          x, y = randomEdgeTile(board, otherEdges)
        else:
          x, y = randomEdgeTile(board, self.edges)

        jx = random.uniform(-0.2, 0.2)
        jy = random.uniform(-0.2, 0.2)

        enemies.append(Enemy(enemyType, x + 0.5 + jx, y + 0.5 + jy))

        self.timer = self.interval

    def isDone(self, enemies):
        # everything spawned, and nobody left alive
        return not self.queue and not any(e.alive for e in enemies)
