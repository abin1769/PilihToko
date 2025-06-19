def fuzzify_jarak(jarak):
    dekat = sedang = jauh = 0

    # Dekat: maksimal 0-7 (1), turun cepat sampai 10
    if jarak <= 7:
        dekat = 1
    elif 7 < jarak <= 10:
        dekat = (10 - jarak) / 3

    # Sedang: naik dari 8-15, puncak 15, turun sampai 20 (lebih sempit)
    if 8 < jarak < 15:
        sedang = (jarak - 8) / 7
    elif 15 <= jarak <= 20:
        sedang = (20 - jarak) / 5

    # Jauh: mulai 18 ke atas, naik cepat, max dari 22 ke atas
    if 18 < jarak <= 22:
        jauh = (jarak - 18) / 4
    elif jarak > 22:
        jauh = 1

    return {"dekat": round(dekat, 3), "sedang": round(sedang, 3), "jauh": round(jauh, 3)}

def fuzzify_rating(rating):
    if rating <= 2.5:
        return {"rendah": 1, "sedang": 0, "tinggi": 0}
    elif 2.5 < rating <= 3.5:
        rendah = (3.5 - rating) / 1
        sedang = (rating - 2.5) / 1
        return {"rendah": round(rendah,3), "sedang": round(sedang,3), "tinggi": 0}
    elif 3.5 < rating <= 4.5:
        sedang = (4.5 - rating) / 1
        tinggi = (rating - 3.5) / 1
        return {"rendah": 0, "sedang": round(sedang,3), "tinggi": round(tinggi,3)}
    else:
        return {"rendah": 0, "sedang": 0, "tinggi": 1}

def fuzzify_stok(stok_total):
    sedikit = sedang = banyak = 0
    # Sedikit (trapesium kiri)
    if stok_total <= 5:
        sedikit = 1
    elif 5 < stok_total <= 10:
        sedikit = (10 - stok_total) / 5
    else:
        sedikit = 0

    # Sedang (segitiga tengah)
    if 10 < stok_total <= 12.5:
        sedang = (stok_total - 10) / 2.5
    elif 12.5 < stok_total <= 15:
        sedang = (15 - stok_total) / 2.5
    else:
        sedang = 0

    # Banyak (trapesium kanan)
    if 15 < stok_total <= 20:
        banyak = (stok_total - 15) / 5
    elif stok_total > 20:
        banyak = 1
    else:
        banyak = 0

    return {"sedikit": round(sedikit,3), "sedang": round(sedang,3), "banyak": round(banyak,3)}

def hitung_kecocokan(jarak, rating, stok_total):
    jarak_fz = fuzzify_jarak(jarak)
    rating_fz = fuzzify_rating(rating)
    stok_fz = fuzzify_stok(stok_total)

    rules = [
        # === PRIORITAS 1: Jarak DEKAT (Bobot 0.8 - 1.0) ===
        # Toko ideal, jarak dekat, rating tinggi, stok banyak. Skor tertinggi.
        (min(jarak_fz["dekat"], rating_fz["tinggi"], stok_fz["banyak"]), 1.0, "Jarak dekat, rating tinggi, stok banyak"),
        # Jarak dekat, tapi mungkin rating/stoknya sedang. Tetap sangat direkomendasikan.
        (min(jarak_fz["dekat"], rating_fz["sedang"], stok_fz["sedang"]), 0.9, "Jarak dekat, rating sedang, stok sedang"),
        # Jarak dekat, walau rating/stoknya sedikit. Bobotnya kita naikkan dari 0.3 jadi 0.8 biar tetap jadi pilihan utama.
        (min(jarak_fz["dekat"], rating_fz["rendah"], stok_fz["sedikit"]), 0.8, "Jarak dekat, walau rating/stok kurang"),

        # === PRIORITAS 2: Jarak SEDANG (Bobot 0.5 - 0.7) ===
        # Jarak sedang hanya akan direkomendasikan jika rating dan stoknya bagus.
        (min(jarak_fz["sedang"], rating_fz["tinggi"], stok_fz["banyak"]), 0.7, "Jarak sedang, rating & stok bagus"),
        (min(jarak_fz["sedang"], rating_fz["sedang"], stok_fz["sedang"]), 0.5, "Jarak sedang, rating & stok cukup"),

        # === PRIORITAS 3: Jarak JAUH (Bobot < 0.3, kita penalti) ===
        # Toko jauh hanya akan muncul jika SEMPURNA dan tidak ada pilihan lain yang lebih baik.
        (min(jarak_fz["jauh"], rating_fz["tinggi"], stok_fz["banyak"]), 0.2, "Jarak jauh, tapi rating & stok sempurna"),
        # Aturan lain untuk jarak jauh kita beri skor sangat rendah atau nol.
        (min(jarak_fz["jauh"], rating_fz["sedang"], stok_fz["banyak"]), 0.1, "Jarak jauh, rating sedang, stok banyak"),
        (min(jarak_fz["jauh"], rating_fz["rendah"], stok_fz["sedikit"]), 0.0, "Jarak jauh, rating & stok kurang"),
    ]


    skor_tertinggi, bobot, alasan = max(rules, key=lambda x: x[0]*x[1])

    final_score = round(skor_tertinggi * bobot, 3)
    return final_score, alasan if final_score > 0 else "Tidak ada rule yang terpenuhi"
