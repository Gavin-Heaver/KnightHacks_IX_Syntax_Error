import heapq
import math

INF = float('inf')
NEIGHBORS = [
             (1,0,1), (-1,0,1), (0,1,1), (0,-1,1), 
             (1,1,math.sqrt(2)), (-1,-1,math.sqrt(2)), 
             (1,-1,math.sqrt(2)), (-1,1,math.sqrt(2))
            ]

def buildField(board, goals, cost):
    width, height = board.width, board.height

    #tiles start as unvisited
    dist = [[INF] * width for _ in range(height)]

    #every goal tile starts at cost 0, and is added to the priority queue
    #search spreads from cpu all at once
    heap = []
    for gx, gy in goals:
        dist[gy][gx] = 0
        heap.append((0, gx, gy))
    #cheapest tile is always popped next
    heapq.heapify(heap)

    while heap:
        d, x, y = heapq.heappop(heap)
        #cheaper path to this tile has already been found
        if d > dist[y][x]:
            continue

        for dx, dy, step in NEIGHBORS:
            nx, ny = x + dx, y + dy

            if not board.inBounds(nx, ny):
                continue

            #checking to see if diagonal movement is blocked by a tool
            if dx and dy:
                if board.toolAt(x + dx, y) or board.toolAt(x, y + dy):
                    continue

            #calculating cost function for tile
            c = cost(nx, ny)
            if c is None:
                continue
            newDist = d + step * c

            #cheaper route found
            if newDist < dist[ny][nx]:
                dist[ny][nx] = newDist
                heapq.heappush(heap, (newDist, nx, ny))

    return dist

def nextStep(dist, board, x, y):
    best = None
    bestDist = dist[y][x]
    for dx, dy, _ in NEIGHBORS:
        nx, ny = x + dx, y + dy
        #bounds check
        if not board.inBounds(nx, ny):
            continue
        #checking validity of diagonal move
        if dx and dy:
            if board.toolAt(x + dx, y) or board.toolAt(x, y + dy):
                continue
            
        if dist[ny][nx] < bestDist:
            bestDist = dist[ny][nx]
            best = (dx, dy)
    #returning direction to move in
    return best