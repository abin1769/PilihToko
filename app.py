from flask import Flask, render_template, request, redirect, url_for
import os
import sys
sys.path.append('.')  # Biar bisa import dari folder modules

from modules.data_loader import load_data
from modules.dijkstra import dijkstra
from modules.fuzzy import hitung_kecocokan

app = Flask(__name__)

# Load data rumah & toko
rumah = load_data('data/rumah.json')
toko = load_data('data/toko.json')
barang_list = list(toko['Toko 1']['stok'].keys())

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

@app.route('/')
def home():
    return render_template('home.html', rumah_list=rumah.keys(), barang_list=toko.keys(), title="Rekomendasi Pasar")

@app.route('/rekomendasi', methods=['POST'])
def rekomendasi():
    barang_dicari = request.form.get('barang').lower()
    rumah_dipilih = request.form.get('rumah')

    if not rumah_dipilih or rumah_dipilih not in rumah:
        return render_template('home.html', rumah_list=rumah.keys(), error="Rumah tidak ditemukan.")

    asal = tuple(rumah[rumah_dipilih])
    skor_tiap_toko = {}

    for nama_toko, data in toko.items():
        lokasi = tuple(data["lokasi"])
        jarak, jalur = dijkstra(asal, lokasi, grid)
        rating = data.get("rating", 0)
        stok_total = data["stok"].get(barang_dicari, 0)

        skor, alasan = hitung_kecocokan(jarak, rating, stok_total)
        if stok_total == 0:
            continue  # Langsung skip toko ini

        skor_tiap_toko[nama_toko] = {
            "skor": skor,
            "jarak": jarak,
            "jalur": jalur,
            "alasan": alasan,
            "stok": stok_total,
            "rating": rating
        }

    rekomendasi = sorted(skor_tiap_toko.items(), key=lambda x: -x[1]["skor"])[:3]
    return render_template('rekomendasi.html',
                           rekomendasi=rekomendasi,
                           barang=barang_dicari,
                           rumah=rumah_dipilih,
                           title="Hasil Rekomendasi")

@app.route('/harga')
def harga_sembako():
    return render_template('harga.html', title="Harga Sembako")

@app.route('/how')
def how_it_works():
    return render_template('how_it_works.html', title="Cara Kerja")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

