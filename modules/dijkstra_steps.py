import heapq

def dijkstra_graf_detailed(graf, start_node, end_node):
    """
    Menjalankan algoritma Dijkstra dan mencatat setiap langkah iterasi.
    """
    # Inisialisasi
    queue = [(0, start_node)]  # (jarak, node)
    dist = {node: float('inf') for node in graf['nodes']}
    prev = {node: None for node in graf['nodes']}
    dist[start_node] = 0
    
    visited = set()
    steps = []
    iteration_count = 0

    # Inisialisasi tabel untuk langkah pertama
    initial_distances = {n: (d, p) for n, d, p in zip(dist.keys(), dist.values(), prev.values())}
    steps.append({
        "iteration": iteration_count,
        "unvisited": [item[1] for item in queue],
        "visited": [],
        "current": "Inisialisasi",
        "distances": initial_distances,
    })

    while queue:
        distance, current_node = heapq.heappop(queue)

        if current_node in visited:
            continue
        
        iteration_count += 1
        visited.add(current_node)

        # Eksplorasi tetangga
        for neighbor, weight in graf['adjacency'].get(current_node, []):
            if neighbor not in visited:
                new_dist = distance + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = current_node
                    heapq.heappush(queue, (new_dist, neighbor))
        
        # Catat keadaan setelah memproses node 'current_node'
        current_distances = {n: (d, p) for n, d, p in zip(dist.keys(), dist.values(), prev.values())}
        steps.append({
            "iteration": iteration_count,
            "unvisited": sorted([item[1] for item in queue]), # Urutkan agar rapi
            "visited": sorted(list(visited)),
            "current": current_node,
            "distances": current_distances
        })

        if current_node == end_node:
            break # Hentikan jika tujuan sudah ditemukan

    # Mengambil path final
    final_path = []
    curr = end_node
    while curr is not None:
        final_path.insert(0, curr)
        curr = prev[curr]

    if final_path[0] != start_node:
        return float('inf'), [], steps

    return dist[end_node], final_path, steps