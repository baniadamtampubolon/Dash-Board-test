# Project Dash Labor Board - Session Development Log
**Tanggal Terakhir Update:** 18 April 2026
**Status:** Stabil & Fitur Lengkap

---

## Sesi 17–18 April 2026 — Geo Map, Refactoring, EWS, & Estetika

### 1. Peta Sebaran (Choropleth Map) ✅
Menambahkan halaman **Peta Sebaran** untuk memvisualisasikan indikator ketenagakerjaan per provinsi.

- **GeoJSON:** Data 38 provinsi Indonesia di `Database/indonesia-provinces.geojson`
- **Name Mapping:** `_PROV_NAME_TO_GEO` untuk mencocokkan nama BPS ↔ GeoJSON
- **Fitur:** Dropdown 7 indikator, choropleth map, KPI Top/Bottom 3, ranking bar chart
- **Layout:** KPI cards → Peta → Ranking bar chart

### 2. Refactoring: Modularisasi app.py ✅
Memecah file `app.py` (1.712 baris) menjadi **12 file modular**:

| File | Isi |
|---|---|
| `app.py` (~165 baris) | Entry point: init, layout, callbacks |
| `design.py` (~325 baris) | PALETTE, SEQ, CHART, apply_chart(), CUSTOM_CSS |
| `data_loader.py` (~135 baris) | load_data(), fix_ratio(), filter_data(), load_geojson() |
| `components.py` (~164 baris) | make_sidebar(), kpi_card(), chart_card(), section(), fmt_compact() |
| `pages/main.py` | Ringkasan Eksekutif |
| `pages/geomap.py` | Peta Sebaran (choropleth + callback) |
| `pages/ews.py` | Early Warning System (3 mode chart + callback) |
| `pages/puk.py` | Penduduk Usia Kerja |
| `pages/ak.py` | Angkatan Kerja |
| `pages/pt.py` | Pengangguran Terbuka |
| `pages/pyb.py` | Penduduk Bekerja |
| `pages/ratio.py` | TPAK, TPT, EPR (shared builder) |

### 3. Logo Kemnaker & Sidebar ✅
- Logo `assets/kemnaker-logo.png` di sidebar (210×210px)
- Sidebar scroll fix: `max-height: 100vh` + `overflow-y: auto` di `custom.css`

### 4. Early Warning System (EWS) ✅
Halaman EWS menampilkan **10 indikator kunci** dengan **3 mode visualisasi** (toggle switch):

| Mode | Tampilan |
|---|---|
| Bar Chart | Top 10 daerah per indikator (horizontal bar) |
| Peta Sebaran | Choropleth map per indikator (nasional only) |
| Treemap | Proporsi daerah per indikator |

**10 Indikator EWS:**

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
| 9 | TPT | TPT | `TPT` |
| 10 | EPR | EPR | `EPR` |

- **Nasional:** Top 10 Provinsi per indikator
- **Provinsi:** Top 10 Kabupaten/Kota dalam provinsi terpilih
- **Callback:** `register_ews_callbacks(app)` untuk mode switching

### 5. Revisi Dashboard PUK, AK, PT, PYB ✅
Semua 4 halaman diperbarui secara konsisten:

| Perubahan | Detail |
|---|---|
| Piramida Usia (PUK) | Diganti → Donut chart gender (biru + pink) |
| Bar Gender (AK) | Diganti → Donut chart gender |
| Distribusi Usia per Gender (AK) | Dihapus |
| Donut Perkotaan vs Perdesaan | Ditambahkan di keempat halaman |
| Line Chart Kelompok Usia | Ditambahkan (satuan jumlah, bukan rasio) |
| Label Donut | Menggunakan jumlah dengan singkatan M/K (bukan persen) |
| Tren Historis | Full-width (md=12) dengan section sub-judul sendiri |

### 6. Overhaul Estetika — Font & Emoji ✅

**Font System Baru (Government Modern / Corporate Executive):**

| Layer | Sebelum | Sesudah |
|---|---|---|
| Judul & Header | Plus Jakarta Sans 800 | IBM Plex Sans 700 |
| Body & UI | Plus Jakarta Sans | Inter |
| Angka KPI | JetBrains Mono | JetBrains Mono (dipertahankan) |
| Chart | Plus Jakarta Sans | Inter |

**SVG Icons System (`dash-iconify`):**
Menggantikan emoji teks standar dan singkatan teks murni dengan icon SVG resolusi tinggi dari berbagai provider (Lucide, MDI, FontAwesome, Line Awesome) untuk membangun antarmuka yang sangat profesional.

| Area | Sebelum | Sesudah |
|---|---|---|
| Sidebar nav | 📊🗺️⚠️👥💼❌✅... / Teks Penuh | SVG Icon (`lucide`, `fa-solid`, `mdi`, `la`) berdampingan dengan Teks |
| KPI card icons | Singkatan Teks (PUK, AK, PT) | SVG Representatif (`fa-solid:users`, `la:industry-solid`, dll) |
| Page badge | Emoji 📍 📅 | Teks bersih tanpa icon |
| Geomap medals | Teks (1st, 2nd, 3rd, Terendah) | SVG (`fa-solid:trophy`, `fa-solid:medal`, `ph:warning-fill`, dll) |

**File yang Diubah:** `design.py`, `assets/custom.css`, `app.py`, `components.py`, `pages/main.py`, `pages/puk.py`, `pages/ak.py`, `pages/pt.py`, `pages/pyb.py`, `pages/ratio.py`, `pages/geomap.py`, `pages/ews.py`, `/notes.txt`

### 7. Standarisasi Format & Layout Chart Visual ✅
Menyempurnakan dan menseragamkan tata letak visual berbagai grafik metrik agar tidak saling bertumpuk (bebas dari error *clipping*):
- **Tema Visual Kemenaker:** Warna *sidebar* disesuaikan persis dengan spektrum biru maskapai resmi Kementerian (`#1353A0`) bergradasi menuju dominasi gelap angkatan laut dengan selektor *active* margin putih-kebiruan.
- **Konversi Treemap ke Bar Chart:** Grafik "Tingkat Pendidikan" (PUK) diubah formatnya menjadi diagram mendatar demi pembandingan proporsi yang lebih linier. 
- **Konversi Donut ke Bar Chart:** Seluruh grafik donat pada halaman rasio (Gender dan Kota vs Desa untuk dasbor TPAK, TPT, EPR) diubah bentuknya menjadi *horizontal bar chart*.
- **Restrukturisasi Eksternal Label Donut Chart:** Merapikan metrik-metrik profil gabungan yang sempit (Proporsi Kategori PT, Status Pekerjaan PYB, dan Status Aktivitas PUK) murni ke ekstensi `go.Pie` — memindah keterangan *legend* menjadi tulisan tegak melayang yang menempel di luar roda, memberikan teks keterangan *center-hole*, dipadu palet pewarnaan serasi (Teal, Oranye, Biru).
- **Perbaikan Margin Padding:** Menambahkan injeksi nilai _margin right_ hingga `70px` dan membatalkan parameter _no_legend=False_ demi mengatasi terpotongnya deretan teks angka persen ganda di sisi kanan _container_ tabel.

### 8. Restrukturisasi Navigasi Sidebar & Highlighting EWS ✅
- **Pemindahan EWS:** Menu "Early Warning System" dipisahkan dari daftar Menu Utama dan dinaikkan letaknya menjadi sub-judul kategori mandiri bernama **"Peringatan Dini"** (tepat di bawah kendali _Filter Wilayah_). Susunan UX (*User Experience*) diperbaiki menjadi urutan [Filter Wilayah -> Peringatan Dini -> Menu Utama -> Indikator Rasio].
- **EWS Alert Highlighting:** Menambahkan kelas pemformatan khusus (`.nav-ews-btn`) sehingga menu peringatan menyala kontras menggunakan paduan kuning pijar (*Amber/Gold* `#FBBF24`) dengan gradien bayangan saat _hover_ dan _active_.
- **Revisi Presisi Warna:** Penyesuaian akhir skema *background* sidebar dengan memasukkan referensi solid kode hex `#15406A` pada awal pilar (*0% gradien*) turun berangsur-angsur menjadi nuansa navy ultra-pekat (`#0B2136`) pada dasar (*100% gradien*).

---

## Sesi 16 April 2026 — Integrasi Dataset Rasio

### 1. Integrasi Dataset Rasio (TPAK, TPT, EPR)
Tiga indikator rasio utama dengan dataset versi terbaru (`ver2.xlsx`):
- **TPAK:** Tingkat Partisipasi Angkatan Kerja (Rasio AK / PUK)
- **TPT:** Tingkat Pengangguran Terbuka (Rasio PT / AK)
- **EPR:** Employment to Population Ratio (Rasio PYB / PUK)

### 2. Fitur Data Engineering
- **Fix Ratio Logic:** Fungsi `fix_ratio(val)` untuk memperbaiki data Excel korup
- **Standardisasi Filter:** Filtering tahun, level, wilayah sinkron di seluruh dashboard

### 3. Desain UI & Visualisasi
- Line Chart (Age Groups), Donut Charts (Gender & Wilayah)
- Full-Width Trend Section, penyesuaian padding & margin

---

## Info Teknis

### Akses & Testing
- **Server:** `host='0.0.0.0'` untuk akses jaringan lokal
- **Port:** `8050` untuk dashboard utama
- **Localtunnel:** `npx localtunnel --port 8050` untuk akses publik

### Font Stack
```
Header:  'IBM Plex Sans', 'Inter', sans-serif
Body:    'Inter', 'Roboto', sans-serif
Mono:    'JetBrains Mono', 'IBM Plex Mono', monospace
```

### Struktur File
```
├── app.py              ← Entry point (~165 baris)
├── design.py           ← Palet warna, font, CSS, chart config
├── data_loader.py      ← Load data, filter, GeoJSON
├── components.py       ← Sidebar, KPI card, chart card
├── pages/
│   ├── main.py         ← Ringkasan Eksekutif
│   ├── geomap.py       ← Peta Sebaran (choropleth + callback)
│   ├── ews.py          ← Early Warning System (3 mode + callback)
│   ├── puk.py          ← Penduduk Usia Kerja
│   ├── ak.py           ← Angkatan Kerja
│   ├── pt.py           ← Pengangguran Terbuka
│   ├── pyb.py          ← Penduduk Bekerja
│   ├── demo.py         ← Demo (mock data)
│   └── ratio.py        ← TPAK, TPT, EPR (shared builder)
├── Database/           ← File .xlsx & .geojson
├── assets/             ← CSS, logo, dan static files
└── app_backup.py       ← Backup pre-refactoring
```

---
*Log dikelola secara otomatis untuk menjaga kontinuitas pengembangan.*
