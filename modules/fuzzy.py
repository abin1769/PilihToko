def fuzzify_jarak(jarak):
    if jarak <= 5:
        return {"dekat": 1, "sedang": 0, "jauh": 0}
    elif 5 < jarak <= 10:
        dekat = (10 - jarak) / 5
        sedang = (jarak - 5) / 5
        return {"dekat": dekat, "sedang": sedang, "jauh": 0}
    elif 10 < jarak <= 20:
        sedang = (20 - jarak) / 10
        jauh = (jarak - 10) / 10
        return {"dekat": 0, "sedang": sedang, "jauh": jauh}
    else:
        return {"dekat": 0, "sedang": 0, "jauh": 1}

def fuzzify_rating(rating):
    if rating <= 2.5:
        return {"rendah": 1, "sedang": 0, "tinggi": 0}
    elif 2.5 < rating <= 3.5:
        rendah = (3.5 - rating) / 1
        sedang = (rating - 2.5) / 1
        return {"rendah": rendah, "sedang": sedang, "tinggi": 0}
    elif 3.5 < rating <= 4.5:
        sedang = (4.5 - rating) / 1
        tinggi = (rating - 3.5) / 1
        return {"rendah": 0, "sedang": sedang, "tinggi": tinggi}
    else:
        return {"rendah": 0, "sedang": 0, "tinggi": 1}

def fuzzify_stok(stok_total):
    if stok_total <= 15:
        return {"sedikit": 1, "sedang": 0, "banyak": 0}
    elif 15 < stok_total <= 25:
        sedikit = (25 - stok_total) / 10
        sedang = (stok_total - 15) / 10
        return {"sedikit": sedikit, "sedang": sedang, "banyak": 0}
    elif 25 < stok_total <= 35:
        sedang = (35 - stok_total) / 10
        banyak = (stok_total - 25) / 10
        return {"sedikit": 0, "sedang": sedang, "banyak": banyak}
    else:
        return {"sedikit": 0, "sedang": 0, "banyak": 1}

def fuzzy_rules(jarak_fz, rating_fz, stok_fz):
    # Contoh aturan (bisa ditambah banyak nanti)
    rules = []

    # Rule 1: Jika jarak dekat DAN rating tinggi DAN stok banyak → sangat cocok (0.9)
    rules.append(min(jarak_fz["dekat"], rating_fz["tinggi"], stok_fz["banyak"]) * 0.9)

    # Rule 2: Jika jarak sedang DAN rating tinggi DAN stok banyak → cocok (0.75)
    rules.append(min(jarak_fz["sedang"], rating_fz["tinggi"], stok_fz["banyak"]) * 0.75)

    # Rule 3: Jika jarak jauh DAN rating tinggi DAN stok banyak → agak cocok (0.5)
    rules.append(min(jarak_fz["jauh"], rating_fz["tinggi"], stok_fz["banyak"]) * 0.5)

    # Rule 4: Jika jarak dekat DAN rating rendah DAN stok sedikit → kurang cocok (0.3)
    rules.append(min(jarak_fz["dekat"], rating_fz["rendah"], stok_fz["sedikit"]) * 0.3)

    return max(rules)  # ambil skor tertinggi dari semua rule

def hitung_kecocokan(jarak, rating, stok_total):
    # Fuzzify semua input
    jarak_fz = fuzzify_jarak(jarak)
    rating_fz = fuzzify_rating(rating)
    stok_fz = fuzzify_stok(stok_total)

    # Simpan alasan untuk setiap rule
    rules = [
        (min(jarak_fz["dekat"], rating_fz["tinggi"], stok_fz["banyak"]), "Jarak dekat, rating tinggi, stok banyak"),
        (min(jarak_fz["sedang"], rating_fz["tinggi"], stok_fz["banyak"]), "Jarak sedang, rating tinggi, stok banyak"),
        (min(jarak_fz["jauh"], rating_fz["tinggi"], stok_fz["banyak"]), "Jarak jauh, rating tinggi, stok banyak"),
        (min(jarak_fz["dekat"], rating_fz["rendah"], stok_fz["sedikit"]), "Jarak dekat, rating rendah, stok sedikit"),
        (min(jarak_fz["dekat"], rating_fz["sedang"], stok_fz["sedang"]) * 0.65, "Jarak dekat, rating sedang, stok sedang"),
        (min(jarak_fz["sedang"], rating_fz["sedang"], stok_fz["banyak"]) * 0.6, "Jarak sedang, rating sedang, stok banyak"),
        (min(jarak_fz["dekat"], rating_fz["sedang"], stok_fz["banyak"]) * 0.7, "Jarak dekat, rating sedang, stok banyak"),
        (min(jarak_fz["sedang"], rating_fz["tinggi"], stok_fz["sedang"]) * 0.6, "Jarak sedang, rating tinggi, stok sedang"),
        (min(jarak_fz["jauh"], rating_fz["tinggi"], stok_fz["sedang"]) * 0.4, "Jarak jauh, rating tinggi, stok sedang"),
        (min(jarak_fz["jauh"], rating_fz["sedang"], stok_fz["banyak"]) * 0.45, "Jarak jauh, rating sedang, stok banyak"),
        (min(jarak_fz["sedang"], rating_fz["sedang"], stok_fz["sedang"]) * 0.5, "Jarak sedang, rating sedang, stok sedang"),
        (min(jarak_fz["dekat"], rating_fz["rendah"], stok_fz["banyak"]) * 0.4, "Jarak dekat, rating rendah, stok banyak"),
        (min(jarak_fz["jauh"], rating_fz["rendah"], stok_fz["sedikit"]) * 0.1, "Jarak jauh, rating rendah, stok sedikit")
    ]

    # Nilai output yang diinginkan per rule (defuzzifikasi manual)
    skor_rules = [
        nilai * bobot for nilai, bobot in zip(
            [r[0] for r in rules],
            [0.9, 0.75, 0.5, 0.3]  # bobot disesuaikan urutan rules
        )
    ]

    if not skor_rules or max(skor_rules) == 0:
        return 0, "Tidak ada rule yang terpenuhi"

    # Ambil index skor terbaik untuk dapetin alasannya juga
    idx = skor_rules.index(max(skor_rules))
    return skor_rules[idx], rules[idx][1]
