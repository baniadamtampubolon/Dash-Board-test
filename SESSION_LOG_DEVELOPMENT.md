# Project Dash Labor Board - Session Development Log
**Tanggal Terakhir Update:** 17 April 2026
**Status:** Stabil & Fitur Baru Aktif

---

## Sesi 17 April 2026 — Geo Map, Refactoring, & EWS

### 1. Peta Sebaran (Choropleth Map) ✅
Menambahkan halaman **Peta Sebaran** untuk memvisualisasikan indikator ketenagakerjaan per provinsi di seluruh Indonesia.

- **GeoJSON:** Mengunduh data 38 provinsi Indonesia ke `Database/indonesia-provinces.geojson`
- **Name Mapping:** Implementasi `_PROV_NAME_TO_GEO` untuk mencocokkan nama BPS ↔ GeoJSON (Bangka Belitung, D I Yogyakarta)
- **Fitur Halaman:**
  - Dropdown inline 7 indikator (PUK, AK, PYB, PT, TPAK, TPT, EPR)
  - Choropleth map Indonesia (Plotly `go.Choroplethmap`)
  - KPI cards Top 3 & Bottom 3 provinsi
  - Bar chart ranking 38 provinsi
- **Layout:** KPI cards → Peta → Ranking bar chart (atas ke bawah)

### 2. Refactoring: Modularisasi app.py ✅
Memecah file `app.py` (1.712 baris) menjadi **12 file modular** menggunakan mekanisme `sed` + copy-paste:

| File | Lines | Isi |
|---|---|---|
| `app.py` | ~165 | Entry point: app init, layout, callbacks (navigasi + filter + routing) |
| `design.py` | ~321 | PALETTE, SEQ, CHART, apply_chart(), CUSTOM_CSS |
| `data_loader.py` | ~135 | load_data(), fix_ratio(), filter_data(), load_geojson(), trend_filter() |
| `components.py` | ~162 | make_sidebar(), kpi_card(), chart_card(), section(), fmt_compact(), loc(), loc_name() |
| `pages/main.py` | ~160 | render_main() — Ringkasan Eksekutif |
| `pages/geomap.py` | ~205 | render_geomap() + register_geomap_callbacks() — Peta Sebaran |
| `pages/ews.py` | ~270 | render_ews() — Early Warning System |
| `pages/puk.py` | ~119 | render_puk() — Penduduk Usia Kerja |
| `pages/ak.py` | ~100 | render_ak() — Angkatan Kerja |
| `pages/pt.py` | ~114 | render_pt() — Pengangguran Terbuka |
| `pages/pyb.py` | ~132 | render_pyb() — Penduduk Bekerja |
| `pages/demo.py` | ~60 | render_demo_page() — Mock data |
| `pages/ratio.py` | ~218 | _build_ratio_page(), render_tpak/tpt_rasio/epr |

- **Backup:** `app_backup.py` (ditambah ke `.gitignore`)
- **Manfaat:** Setiap page bisa diedit independen, app.py hanya ~165 baris

### 3. Logo Kemnaker ✅
- Logo `assets/kemnaker-logo.png` ditampilkan di sidebar menggantikan emoji ⚙️
- Ukuran disesuaikan user menjadi **210×210px** dengan `borderRadius: 10px`

### 4. Sidebar Scroll Fix ✅
- Menambahkan `max-height: 100vh` dan `overflow-y: auto` di `assets/custom.css`
- Fix duplikasi CSS antara `custom.css` dan inline `CUSTOM_CSS` di `design.py`

### 5. Early Warning System (EWS) ✅
Halaman baru **Early Warning System** menampilkan **10 bar chart horizontal**, masing-masing memvisualisasikan **Top 10 daerah** untuk setiap indikator kunci:

| # | Indikator | Sumber | Kolom/Rumus |
|---|---|---|---|
| 1 | Penganggur Putus Asa | PT | `kat_pa` |
| 2 | Penganggur Pencari Kerja | PT | `kat_mp` |
| 3 | Pekerja Keluarga/Tak Dibayar | PYB | `sta_7` |
| 4 | Gender Gap TPAK | TPAK | `jk_lk - jk_pr` |
| 5 | Kualitas Pendidikan (SD) | PUK | `pd_sd / PUK × 100` |
| 6 | Pengangguran Terdidik | PT | `pd_univ / PT × 100` |
| 7 | Partisipasi Perempuan | TPAK | `jk_pr` |
| 8 | Partisipasi Pekerja Muda | TPAK | `ku_1519` |
| 9 | Tingkat Pengangguran Terbuka | TPT | `TPT` |
| 10 | Employment to Population Ratio | EPR | `EPR` |

- **Nasional:** Top 10 Provinsi per indikator
- **Provinsi:** Top 10 Kabupaten/Kota dalam provinsi terpilih
- **Layout:** 2 kolom × 5 baris (10 chart total)

---

## Sesi 16 April 2026 — Integrasi Dataset Rasio

### 1. Integrasi Dataset Rasio (TPAK, TPT, EPR)
Telah diintegrasikan tiga indikator rasio utama dengan dataset versi terbaru (`ver2.xlsx`):
- **TPAK:** Tingkat Partisipasi Angkatan Kerja (Rasio AK / PUK)
- **TPT:** Tingkat Pengangguran Terbuka (Rasio PT / AK)
- **EPR:** Employment to Population Ratio (Rasio PYB / PUK)

### 2. Fitur Data Engineering
- **Fix Ratio Logic:** Implementasi fungsi `fix_ratio(val)` untuk otomatis mendeteksi dan memperbaiki data Excel yang korup (terbaca sebagai `timedelta` atau `datetime`).
- **Standardisasi Filter:** Memastikan filtering tahun, level (Nasional/Provinsi/Kabupaten), dan wilayah sinkron di seluruh dashboard.

### 3. Desain UI & Visualisasi
Dashboard rasio kini menggunakan layout premium dengan variasi chart:
- **Line Chart (Age Groups):** Distribusi umur yang lebih halus.
- **Donut Charts (Gender & Wilayah):** Fokus pada perbandingan proporsi.
- **Full-Width Trend Section:** Tren historis 2018-2025 di bagian bawah.
- **Padding & Margin:** Penyesuaian `xaxis range` dan `margin` agar angka tidak terpotong.

---

## Info Teknis

### Akses & Testing
- **Server:** `host='0.0.0.0'` untuk akses dalam jaringan lokal (WiFi)
- **Port:** `8050` untuk dashboard utama (`app.py`)
- **Localtunnel:** `npx localtunnel --port 8050` untuk akses publik/remote

### Struktur File
```
├── app.py              ← Entry point (~165 baris)
├── design.py           ← Palet warna, CSS, chart config
├── data_loader.py      ← Load data, filter, GeoJSON
├── components.py       ← Sidebar, KPI card, chart card
├── pages/
│   ├── main.py         ← Ringkasan Eksekutif
│   ├── geomap.py       ← Peta Sebaran (choropleth)
│   ├── ews.py          ← Early Warning System
│   ├── puk.py          ← Penduduk Usia Kerja
│   ├── ak.py           ← Angkatan Kerja
│   ├── pt.py           ← Pengangguran Terbuka
│   ├── pyb.py          ← Penduduk Bekerja
│   ├── demo.py         ← Demo (mock data)
│   └── ratio.py        ← TPAK, TPT, EPR
├── Database/           ← File .xlsx & .geojson
├── assets/             ← CSS, logo, dan static files
└── app_backup.py       ← Backup pre-refactoring
```

---
*Log dikelola secara otomatis untuk menjaga kontinuitas pengembangan.*
