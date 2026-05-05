# Dashboard Ketenagakerjaan — Dash Rewrite

Rewrite dari Streamlit ke **Plotly Dash** untuk stabilitas, performa, dan tampilan yang lebih profesional.

## Keunggulan vs Streamlit

| Fitur             | Streamlit    | Dash                                   |
| ----------------- | ------------ | -------------------------------------- |
| Re-render         | Seluruh page | Hanya komponen yang berubah (callback) |
| Layout control    | Terbatas     | Full HTML/CSS                          |
| Interaktivitas    | Terbatas     | Rich callbacks + State                 |
| Production deploy | Sedang       | Mature (Gunicorn, Docker, dsb.)        |
| Chart variety     | Plotly       | Plotly native + lebih banyak opsi      |

## Struktur File

```
project/
├── app.py                  # Entry point Dash
├── design.py               # Palet warna, font, CSS kustom
├── data_loader.py          # Logika ETL data, filter wilayah, GeoJSON
├── components.py           # Pembuat UI Sidebar, Card KPI, Container
├── map_helper.py           # Modul utilitas khusus Peta Spasial
├── pages/                  # Seluruh modul dasbor per-halaman
│   ├── main.py             # Ringkasan Ketenagakerjaan
│   ├── ews.py              # Early Warning System (3 mode indikator)
│   ├── puk.py              # Dasbor Penduduk Usia Kerja
│   ├── ak.py               # Dasbor Angkatan Kerja
│   ├── pt.py               # Dasbor Pengangguran Terbuka
│   ├── pyb.py              # Dasbor Penduduk Bekerja
│   └── ratio.py            # Dasbor Rasio Indikator (TPAK, TPT, EPR)
├── requirements.txt        # Dependencies
├── Database/               # Folder dataset & spasial
│   ├── PUK-2018-2025-ver2.xlsx
│   ├── ...
│   └── indonesia-kabkot-simplified.geojson
└── assets/                 # File statis gambar dan CSS tambahan
```

## Instalasi

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
# Development
python app.py

# Production (Gunicorn)
gunicorn app:server -b 0.0.0.0:8050 --workers 2
```

Buka browser: http://localhost:8050


### Langkah 1 — Masuk ke folder project

> cd /Users/adamtampubolon/kemenaker/Project/Dash-Board-test



### Langkah 2 — Aktifkan Virtual Environment

> source venv/bin/activate
>
> python app.py



### Ringkasan cepat (copy-paste sekaligus):

> cd /Users/adamtampubolon/kemenaker/Project/Dash-Board-test
> source venv/bin/activate
> python app.py

## Fitur Dashboard

### 7 Modul Dasbor Utama

1. **Ringkasan Ketenagakerjaan** — Matriks Data Historis Penuh, Grid Alur Partisipasi (*Icicle Grid*), Donut komposisi, Trend Dinamika.
2. **Early Warning System (EWS)** — Sistem kewaspadaan berdasar top-indikator krusial. Mendukung tampilan Peta Resolusi Kabupaten, Treemap Proporsi, dan Ranking Bar Chart.
3. **Penduduk Usia Kerja (PUK)** — Peta Spasial, Komposisi Aktivitas, Piramida Usia/Gender, Ranking Wilayah.
4. **Angkatan Kerja (AK)** — Peta Spasial, Tren Historis, Proporsi Wilayah (Desa/Kota).
5. **Pengangguran Terbuka (PT)** — Sunburst Chart Kategori, Ranking Pengangguran, Peta Sebaran.
6. **Penduduk Bekerja (PYB)** — Analisis Sektor Formal vs Informal, Treemap Industri Eksekutif, Jam Kerja.
7. **Rasio (TPAK, TPT, EPR)** — Metrik turunan berbasis kalkulasi rasio antar kumpulan dataset.

### Variasi Visualisasi Komprehensif

- **Peta Spasial (Choropleth):** Peta cerdas yang mendukung tingkat zoom makro (Nasional) hingga mikro (Resolusi Kabupaten/Kota) dengan fitur *Auto Bounding-Box Zoom*.
- **Grid Hierarki Pekerjaan:** (*Icicle Layout*) Menggantikan bagan corong konvensional.
- **Treemap Skala Penuh:** Analisis proporsional interaktif untuk lapangan pekerjaan.
- **Radial Chart:** Sunburst & Donut (*Pie*) Chart tanpa *legend* menumpuk, mendistribusikan data langsung di atas irisan roda.
- **Peringkat Horizontal Bar:** Fitur pengurutan rangking 38 provinsi atau 500+ kabupaten berdasarkan metrik rasio maupun angka absolut.

### Filter Hierarki Navigasi

- Pemilihan Tahun interaktif.
- Analisis Tingkat Wilayah multi-lapis: Nasional ↔ Provinsi ↔ Kabupaten/Kota.
- Filter otomatis bersusun (*auto-cascade*): Pilihan provinsi langsung memperbarui mesin pemetaan resolusi geospasial Plotly secara *on-the-fly*.

## Deploy ke Server

```bash
# Menggunakan gunicorn + nginx
gunicorn app:server -b 127.0.0.1:8050

# Atau Docker
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8050"]


```
