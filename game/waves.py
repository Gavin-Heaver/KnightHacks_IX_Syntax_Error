import config
import random

MODIFIERS = ["normal", "swarm", "heavy", "rush", "flank"]

def generateWave(waveNumber):
  #wave modifier- only normal is wave 1 or 2
  if waveNumber < 3:
    modifier = "normal"
  else:
    modifier = random.choice(MODIFIERS)

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

  EDGES = ["top", "bottom", "left", "right"]
  OPPOSITE_EDGE = {"top":"bottom", "bottom":"top", "left":"right", "right":"left"}
  ADJACENT_EDGE = {"top":["left", "right"], "bottom":["left", "right"], "left":["top","bottom"], "right":["top", "bottom"]}

  edge = random.choice(EDGES)
  if modifier == "flank":
    edges = [edge, OPPOSITE_EDGE[edge]]
  else:
    edges = [edge, random.choice(ADJACENT_EDGE[edge])]

  return {"queue": queue, "interval": interval, "edges": edges, "modifier": modifier}

# temporary, at the bottom of waves.py
if __name__ == "__main__":
    import random, config
    random.seed(config.DEMO_SEED)
    for n in range(1, 11):
        w = generateWave(n)
        counts = {t: w["queue"].count(t) for t in set(w["queue"])}
        print(n, w["modifier"], round(w["interval"], 2), w["edges"], counts)
