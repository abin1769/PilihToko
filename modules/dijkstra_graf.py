import heapq

def dijkstra_graf(graf, start_node, end_node):
    """
    Menjalankan algoritma Dijkstra pada representasi graf (adjacency list)
    dan mengembalikan jarak terpendek, jalur, serta detail setiap iterasi.
    Inputnya adalah nama node dalam bentuk string (contoh: "Rumah1", "SimpangA").
    """
    # Antrian prioritas berisi: (jarak, node_sekarang)
    queue = [(0, start_node)]
    
    # Kamus untuk menyimpan jarak terpendek yang sudah ditemukan ke setiap node
    min_dist = {node: float('inf') for node in graf['nodes']}
    min_dist[start_node] = 0
    
    # Kamus untuk menyimpan predecessor (node sebelumnya di jalur terpendek)
    predecessors = {node: None for node in graf['nodes']}

    # Set untuk melacak node yang sudah dikunjungi (diambil dari priority queue)
    visited_nodes = set()

    # List untuk menyimpan semua langkah/iterasi algoritma
    dijkstra_steps = []
    
    # --- Inisialisasi Pertama (Iteration 0) ---
    initial_node_states = {}
    for node in graf['nodes']:
        current_dist = min_dist[node]
        current_prev = predecessors[node]
        initial_node_states[node] = {
            "dist": current_dist if current_dist != float('inf') else "∞", # Ubah Infinity jadi "∞"
            "prev": current_prev,
            "updated_at_iter": 0 if node == start_node else None
        }

    dijkstra_steps.append({
        "iteration_num": 0,
        "unvisited_q": sorted([node for node in min_dist if min_dist[node] != float('inf') and node not in visited_nodes]),
        "visited_s": sorted(list(visited_nodes)),
        "current_node": None, # Tidak ada current node di inisialisasi
        "node_states": initial_node_states
    })

    iteration_counter = 1 # Mulai iterasi dari 1

    while queue:
        dist, current_node = heapq.heappop(queue)

        # Jika node sudah pernah dikunjungi dengan rute yang lebih pendek, lewati
        if current_node in visited_nodes:
            continue
        
        visited_nodes.add(current_node) # Tandai sebagai dikunjungi

        # --- Rekam State Iterasi Saat Ini (sebelum eksplorasi tetangga) ---
        # Salin state node dari iterasi sebelumnya agar perubahan hanya berlaku untuk node yang diupdate
        current_node_states = {node: dict(dijkstra_steps[-1]["node_states"][node]) for node in graf['nodes']}
        # Pastikan state current_node itu sendiri adalah yang terbaru dari min_dist
        current_node_states[current_node] = {
            "dist": min_dist[current_node] if min_dist[current_node] != float('inf') else "∞",
            "prev": predecessors[current_node],
            "updated_at_iter": iteration_counter # Diupdate pada iterasi saat ini
        }

        # Eksplorasi semua tetangga dari node saat ini
        for neighbor, weight in graf['adjacency'].get(current_node, []):
            if neighbor in visited_nodes: # Jangan kunjungi node yang sudah final
                continue

            new_dist = min_dist[current_node] + weight
            
            # Jika ditemukan rute baru yang lebih pendek ke tetangga
            if new_dist < min_dist[neighbor]:
                min_dist[neighbor] = new_dist
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (new_dist, neighbor))

                # Update state node di current_node_states untuk tetangga yang baru di-update
                current_node_states[neighbor] = {
                    "dist": new_dist if new_dist != float('inf') else "∞",
                    "prev": current_node,
                    "updated_at_iter": iteration_counter # Tandai iterasi terakhir diupdate
                }
        
        # Simpan rekaman iterasi ini setelah semua tetangga dievaluasi
        dijkstra_steps.append({
            "iteration_num": iteration_counter,
            "unvisited_q": sorted([node for node in min_dist if node not in visited_nodes and min_dist[node] != float('inf')]),
            "visited_s": sorted(list(visited_nodes)),
            "current_node": current_node,
            "node_states": current_node_states # State nodes pada akhir iterasi ini
        })
        
        # Jika sudah sampai tujuan, kita bisa break, tapi kita perlu path-nya juga
        # Jika tujuan ditemukan, kita bisa langsung membangun path final
        if current_node == end_node:
            break # Keluar dari loop setelah tujuan ditemukan dan state-nya direkam

        iteration_counter += 1

    # Bangun path final setelah loop selesai (baik karena break atau queue kosong)
    final_path_nodes = []
    current_path_node = end_node
    # Hanya bangun path jika end_node benar-benar dapat dijangkau
    if min_dist[end_node] != float('inf'):
        while current_path_node is not None:
            final_path_nodes.insert(0, current_path_node)
            current_path_node = predecessors[current_path_node]
    
    # Validasi path final: pastikan dimulai dari start_node
    if not final_path_nodes or final_path_nodes[0] != start_node:
        return float('inf'), [], dijkstra_steps # Jika path tidak valid, kembalikan inf dan path kosong

    return min_dist[end_node], final_path_nodes, dijkstra_steps # Mengembalikan jarak, jalur, dan langkah-langkah