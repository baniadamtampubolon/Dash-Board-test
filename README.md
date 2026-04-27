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
├── app.py                  # Aplikasi utama Dash (satu file)
├── requirements.txt        # Dependencies
├── Database/
│   ├── PUK-2018-2025-ver2.xlsx
│   ├── AK-2018-2025-ver2.xlsx
│   ├── PT-2018-2025-ver2.xlsx
│   └── PYB-2018-2025-ver3.xlsx
└── assets/                 # (opsional) file static
    └── kemnaker-logo.png
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

### 5 Halaman

1. **Ringkasan Ketenagakerjaan** — KPI 4 kartu, Funnel chart, Donut komposisi, Bar sektor, Multi-line trend
2. **Penduduk Usia Kerja (PUK)** — Piramida usia/gender, Status aktivitas, Treemap pendidikan, Trend
3. **Angkatan Kerja (AK)** — Bar usia per gender, Perbandingan gender, Pendidikan, Trend
4. **Pengangguran Terbuka (PT)** — Bar kategori, Sunburst, Area chart usia, Multi-line trend
5. **Penduduk Bekerja (PYB)** — Treemap sektor, Donut status, Bar jabatan, Bar jam kerja, Trend

### Variasi Chart

- Funnel chart (alur partisipasi)
- Treemap (sektor & pendidikan)
- Sunburst chart (kategori pengangguran)
- Piramida usia (population pyramid)
- Area chart
- Donut/Pie chart
- Grouped/stacked bar chart
- Multi-line trend chart

### Filter

- Tahun (dropdown)
- Tingkat Wilayah: Nasional / Provinsi / Kabupaten-Kota
- Auto-cascade: pilih provinsi → daftar kabkot otomatis update

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
