import json
from collections import deque

def load_data(path):
    """Fungsi helper untuk memuat data dari file JSON."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di path: {path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Gagal mendekode JSON dari file: {path}")
        return None

def get_neighbors_from_grid(pos, grid):
    """Mendapatkan tetangga yang valid dari sebuah titik di grid."""
    x, y = pos
    neighbors = []
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != 0:
                neighbors.append((nx, ny))
    return neighbors

def is_intersection(pos, grid):
    """Mengecek apakah sebuah titik adalah persimpangan (lebih dari 2 jalan)."""
    return len(get_neighbors_from_grid(pos, grid)) > 2

def main():
    """Fungsi utama untuk membangun dan menyimpan graf."""
    print("Memulai proses pembuatan graf jalan otomatis...")

    # Memuat semua data yang dibutuhkan
    grid = load_data('data/map.json')
    rumah_data = load_data('data/rumah.json')
    toko_data = load_data('data/toko.json')

    if not all([grid, rumah_data, toko_data]):
        print("Proses dihentikan karena ada file data yang gagal dimuat.")
        return

    # --- LANGKAH 1: Identifikasi semua node penting (Key Nodes) ---
    print("1/3: Mengidentifikasi semua node penting (rumah, toko, simpang)...")
    key_nodes = {}      # Kamus untuk menyimpan nama_node -> (x, y)
    coord_to_name = {}  # Kamus untuk memetakan (x, y) -> nama_node

    # Tambahkan semua rumah sebagai node penting
    for nama, lokasi in rumah_data.items():
        coord = tuple(lokasi)
        key_nodes[nama] = coord
        coord_to_name[coord] = nama

    # Tambahkan semua toko sebagai node penting
    for nama, data in toko_data.items():
        coord = tuple(data['lokasi'])
        key_nodes[nama] = coord
        coord_to_name[coord] = nama
        
    # Cari dan tambahkan semua persimpangan jalan
    simpang_count = 1
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            pos = (x, y)
            if grid[y][x] != 0 and pos not in coord_to_name:
                if is_intersection(pos, grid):
                    nama_simpang = f"Simpang{simpang_count}"
                    key_nodes[nama_simpang] = pos
                    coord_to_name[pos] = nama_simpang
                    simpang_count += 1
                    
    print(f"   -> Ditemukan total {len(key_nodes)} node penting.")

    # --- LANGKAH 2: Bangun Adjacency List menggunakan BFS dari setiap node penting ---
    print("2/3: Menghitung jarak antar node (membangun adjacency list)...")
    adjacency = {name: [] for name in key_nodes}
    
    for start_node_name, start_coord in key_nodes.items():
        # Menjalankan Breadth-First Search (BFS) dari setiap node penting
        queue = deque([(start_coord, 0)]) # Antrian berisi (posisi_sekarang, jarak)
        visited = {start_coord}
        
        while queue:
            current_pos, distance = queue.popleft()
            
            # Jika posisi saat ini adalah node penting LAINNYA
            if current_pos in coord_to_name and current_pos != start_coord:
                neighbor_node_name = coord_to_name[current_pos]
                # Catat hubungan ketetanggaan dan jaraknya
                adjacency[start_node_name].append([neighbor_node_name, distance])
                # Hentikan pencarian di jalur ini karena sudah bertemu node penting
                continue

            # Jika bukan node penting, lanjutkan pencarian ke tetangga
            for neighbor_pos in get_neighbors_from_grid(current_pos, grid):
                if neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    queue.append((neighbor_pos, distance + 1))

    print("   -> Pembangunan adjacency list selesai.")

    # --- LANGKAH 3: Susun dan simpan graf ke file JSON ---
    print("3/3: Menyimpan graf ke file 'data/graf_jalan.json'...")
    final_graph = {
        "nodes": {name: list(coord) for name, coord in key_nodes.items()},
        "adjacency": adjacency
    }
    
    output_path = 'data/graf_jalan.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_graph, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Proses Selesai! Graf jalan berhasil dibuat dan disimpan di '{output_path}'.")

if __name__ == '__main__':
    main()
