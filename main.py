import sys
sys.path.append('.')  # Tambahkan direktori root

from modules.data_loader import load_data
from modules.dijkstra import dijkstra, get_neighbors
from modules.fuzzy import hitung_kecocokan  # pastikan fungsi return skor, alasan

# Load data
rumah = load_data('data/rumah.json')
toko = load_data('data/toko.json')

# Grid jalan
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

# Cek data rumah dan toko
print(f"Grid size: {len(grid)}x{len(grid[0])}")
print("Cek posisi rumah:")
for k, v in rumah.items():
    print(k, v, "->", grid[v[1]][v[0]])

print("Cek data toko:")
for k, v in toko.items():
    x, y = v['lokasi']
    print(k, v, "->", grid[y][x])

# Masukkan input
barang_dicari = input("\nMasukkan nama barang yang dicari (misal: beras): ").lower()
rumah_dipilih = input("Masukkan nama rumah (contoh: Rumah 1): ")
asal = tuple(rumah[rumah_dipilih])

# Proses penilaian dan rekomendasi
skor_tiap_toko = {}
min_jarak = float('inf')
terdekat = None
rute_terdekat = []

for nama_toko, data in toko.items():
    lokasi = tuple(data["lokasi"])
    jarak, jalur = dijkstra(asal, lokasi, grid)
    rating = data.get("rating", 0)
    stok_total = data["stok"].get(barang_dicari, 0)

    skor, alasan = hitung_kecocokan(jarak, rating, stok_total)
    skor_tiap_toko[nama_toko] = {
        "skor": skor,
        "jarak": jarak,
        "jalur": jalur,
        "alasan": alasan,
        "stok": stok_total,
        "rating": rating
    }

    if jarak < min_jarak:
        min_jarak = jarak
        terdekat = nama_toko
        rute_terdekat = jalur

# Urutkan berdasarkan skor fuzzy tertinggi
rekomendasi = sorted(skor_tiap_toko.items(), key=lambda x: -x[1]["skor"])

# Tampilkan hasil rekomendasi
print("\n--- Rekomendasi Toko ---")
for i, (nama, info) in enumerate(rekomendasi[:3], start=1):
    print(f"{i}. {nama}")
    print(f"   Skor: {info['skor']:.2f}")
    print(f"   Jarak: {info['jarak']}")
    print(f"   Rating: {info['rating']}")
    print(f"   Stok '{barang_dicari}': {info['stok']}")
    print(f"   Jalur: {info['jalur']}")
    print(f"   Alasan: {info['alasan']}\n")

# Tampilkan toko terdekat (bukan berdasarkan skor, hanya jarak)
print(f"Toko terdekat: {terdekat}, jarak: {min_jarak}")
print("Jalurnya:", rute_terdekat)
