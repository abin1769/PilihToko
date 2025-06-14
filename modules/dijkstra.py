import heapq

def get_neighbors(pos, grid):
    x, y = pos
    neighbors = []
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            if grid[ny][nx] in [1, 2, 3]:
                neighbors.append((nx, ny))
    return neighbors

def dijkstra(start, goal, grid):
    queue = [(0, start)]
    visited = set()
    dist = {start: 0}
    prev = {}

    while queue:
        cost, current = heapq.heappop(queue)

        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = prev[current]
            path.append(start)
            path.reverse()
            return cost, path

        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(current, grid):
            new_cost = cost + 1
            if neighbor not in dist or new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                prev[neighbor] = current
                heapq.heappush(queue, (new_cost, neighbor))

    return float('inf'), []
