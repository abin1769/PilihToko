import heapq
import json

#  peta 
WIDTH = 40
HEIGHT = 20

grid = [
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,3,0,0,0],
    [0,0,0,0,0,3,0,1,0,0,0,0,0,0,0,0,0,0,2,0,0,3,0,0,1,0,0,0,0,3,0,0,0,0,0,1,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
    [0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,0,0,2,0,0,0,0,0,0,1,2,0,0,0],
    [0,1,0,1,0,0,0,0,0,1,0,0,0,0,3,1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
    [0,1,0,1,2,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,3,0,0,1,0,0,0,0],
    [0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,2,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0],
    [0,1,2,1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,3,1,0,0,0,0,1,0,0,0,0],
    [0,1,0,1,0,1,0,0,0,0,0,3,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0],
    [0,1,0,1,0,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0],
    [0,1,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,3,0,3,0,0],
    [0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,0,0,0,1,0,0,0,2,0,0,0,0,0,0,2,0,0,1,0,0,0,0,1,0,0,2,0,0,1,0,0,0,0,0,1,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,2,0,0],
    [0,0,2,0,0,1,0,0,0,0,0,3,0,0,1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,2,0,0,1,0,0,0],
    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
]


# Rumah dan toko
rumah = {
    "Rumah 1": (2, 9),
    "Rumah 2": (2, 17),
    "Rumah 3": (4, 6),
    "Rumah 4": (9, 15),
    "Rumah 5": (16, 15),
    "Rumah 6": (18, 2),
    "Rumah 7": (20, 7),
    "Rumah 8": (20, 14),
    "Rumah 9": (27, 15),
    "Rumah 10": (28, 4),
    "Rumah 11": (33, 18),
    "Rumah 12": (36, 4),
    "Rumah 13": (37, 16)
}

toko = {
    "Toko 1": (5, 2),
    "Toko 2": (11, 10),
    "Toko 3": (11, 17),
    "Toko 4": (14, 5),
    "Toko 5": (21, 2),
    "Toko 6": (29, 2),
    "Toko 7": (29, 9),
    "Toko 8": (32, 6),
    "Toko 9": (35, 13),
    "Toko 10": (36, 1),
    "Toko 11": (37, 13)
}



# Fungsi untuk mencari tetangga (atas, bawah, kiri, kanan)
def get_neighbors(pos,grid):
    x, y = pos
    neighbors = []
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
               if grid[ny][nx] in [1, 2, 3]:
                neighbors.append((nx, ny))
    return neighbors

# Algoritma Dijkstra
def dijkstra(start, goal):
    queue = [(0, start)]
    visited = set()
    dist = {start: 0}
    prev = {}  # <- pelacak jalur

    while queue:
        cost, current = heapq.heappop(queue)

        if current == goal:
            # Rekonstruksi jalur dari goal ke start
            path = []
            while current != start:
                path.append(current)
                current = prev[current]
            path.append(start)
            path.reverse()
            return cost, path  # Kembalikan jarak & jalur

        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(current, grid):
            new_cost = cost + 1
            if neighbor not in dist or new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                prev[neighbor] = current
                heapq.heappush(queue, (new_cost, neighbor))

    return float('inf'), []  # Gagal
# cari toko terdekat 
rumah_dipilih = input("Masukkan nama rumah (contoh: Rumah 1): ")
asal = rumah[rumah_dipilih]
min_jarak = float('inf')
rute_terdekat = []

for nama_toko, lokasi in toko.items():
    jarak, jalur = dijkstra(asal, lokasi)
    print(f"Jarak ke {nama_toko}: {jarak}")
    if jarak < min_jarak:
        min_jarak = jarak
        terdekat = nama_toko
        rute_terdekat = jalur

print(f"Toko terdekat: {terdekat}, jarak: {min_jarak}")
print("Jalurnya:", rute_terdekat)
