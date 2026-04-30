# Project Dash Labor Board - Session Development Log
**Tanggal Terakhir Update:** 29 April 2026
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
| `pages/main.py` | Ringkasan Ketenagakerjaan |
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

### 9. Perombakan UI Ringkasan Ketenagakerjaan & Tabel Matriks Historis ✅
- **Kustomisasi Bagan Alur Partisipasi (Icicle Grid):** Mengganti komponen bawaan `go.Funnel` yang statis menjadi susunan HTML/CSS Grid kustom yang membentuk tata letak blok (*Icicle Layout*) berdimensi lebar penuh (*full-width*). Bagan baru ini berhasil memunculkan secara eksplisit rincian metrik BAK (Sekolah, MRT, Lainnya) dengan desain sudut *rounded* yang sangat modern, teks di tengah, dan ruang pembatas grid putih tebal.
- **Restrukturisasi Formasi Dasbor:** Merapikan formasi letak baris (*row*) Ringkasan Ketenagakerjaan agar menyesuaikan hierarki pembacaan: Baris 1 ditempati Peta Alur Ketenagakerjaan Penuh, Baris 2 memuat Top Sektor & Donut AK secara bersisian, dan Baris 3 difokuskan khusus untuk kurva Dinamika & Tren.
- **Standardisasi Donut AK:** Konversi gaya diagram lingkaran ke tipe `go.Pie` berekstensi label luar, melenyapkan tab *legend* agar selaras dengan dasbor rasio.
- **Injeksi Tabel Data Historis (2018-2025):** Menyematkan tabel matriks transparan super responsif pada baris pamungkas. Tabel ini disetel agar mendemonstrasikan angka asli dengan *comma-separated* yang merangkum detail data historis PUK, AK, BAK beserta komponen sub-kegiatannya dari agregat seluruh 8 tahun data secara *real-time* berbasis _filter_ wilayah.

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

## Sesi 27 April 2026 — Modularisasi GeoMap & Restrukturisasi UI

### 1. Modularisasi GeoMap
- **Penghapusan Peta Standalone:** Menghapus halaman mandiri `geomap.py` beserta tab navigasi "Peta Sebaran" di *sidebar*.
- **Pembuatan `map_helper.py`:** Memindahkan logika rendering peta Spasial ke utilitas baru yang memecah visualisasi menjadi tiga bagian independen: Peta Choropleth Utama, Kartu KPI Top/Bottom, dan Grafik Ranking.
- **Injeksi Indikator:** Menyuntikkan ketiga komponen peta tersebut langsung ke dalam halaman setiap indikator (`puk.py`, `ak.py`, `pt.py`, `pyb.py`, `ratio.py`) dengan urutan hierarki yang dioptimalkan (Peta diletakkan setelah *Ban Chart*, dan Grafik Ranking dipaku di bagian paling bawah).

### 2. Peningkatan Ringkasan Ketenagakerjaan (`main.py`)
- **Highlight Struktur Ketenagakerjaan:** Menerapkan prinsip *Gestalt* dan psikologi warna pada grafik Alur Partisipasi (*Icicle Chart*). Angkatan Kerja (Bekerja & Pengangguran) dikelompokkan secara visual dalam kontainer biru, sementara Bukan Angkatan Kerja (Sekolah, MRT, Lainnya) dikelompokkan dalam kontainer abu-abu netral.
- **Kompaktifikasi Ban Chart:** Menyatukan 4 metrik absolut utama dan 3 metrik rasio (TPAK, TPT, EPR) ke dalam satu baris horizontal memanjang yang elegan (`kpi-row-compact`).
- **Re-ordering Layout:** Menukar tata letak agar tabel matriks "Rekapitulasi Data Historis" tampil lebih dulu sebelum grafik "Dinamika & Tren".

---

## Sesi 29 April 2026 — Pemetaan Resolusi Kabupaten & Arsitektur EWS ✅

### 1. Perombakan Arsitektur EWS
- **Transisi Layout:** Merombak tampilan indikator EWS dari kotak-kotak kecil *grid* multi-indikator menjadi **Satu Dasbor Penuh (Single View)**. Pilihan indikator kini disembunyikan dalam menu tarik-turun (*Dropdown*).
- **Concurrent 3-Chart View:** Seluruh 3 *chart* (Peta, Bar Chart, dan Treemap) ditampilkan secara bersamaan tanpa *toggle switch*, untuk analisis metrik mendalam.
- **Indikator Informal:** Menambahkan indikator baru EWS yaitu **"Proporsi Pekerja Informal"** dengan kalkulasi rasio otomatis berbasis data total Penduduk Bekerja (PYB).

### 2. Ekspansi Peta Resolusi Kabupaten/Kota (Geospatial Engineering)
- **Kompresi GeoJSON:** Menyusutkan *file* batas spasial masif `indonesia-kota-kabupaten.json` (92MB) menjadi versi *simplified* berukuran ringan (~3MB) memakai pustaka `geopandas` untuk menghindari *browser memory crash*.
- **Algoritma Fuzzy Matching:** Menyusun algoritma pencocokan kemiripan teks (*fuzzy matching string*) untuk menjembatani ribuan anomali nama wilayah (contoh: *Medan* vs *Kota Medan*, *Labuhan Batu* vs *Labuhanbatu*) antara data Excel Kemnaker dan poligon GeoJSON, yang kemudian dibekukan menjadi *dictionary* `_KABKOT_NAME_TO_GEO` di `data_loader.py`.
- **Dynamic Bounding Box:** Menyelesaikan eror kompatibilitas Plotly `fitbounds` dengan cara mengekstraksi koordinat absolut (*west, east, south, north*) dari ke-38 provinsi secara sistematis, dan menginjeksinya langsung ke mesin Plotly. Hasilnya, peta kini dapat secara mulus dan instan melakukan *zoom-in* langsung menukik ke pulau yang dipilih pengguna.
- **Ekspansi Dasbor Utama:** Mengintegrasikan mesin peta dinamis (Provinsi ↔ Kabupaten) ini ke 5 tab utama (PUK, AK, PYB, PT, Rasio) dengan merevisi modul `map_helper.py` beserta fitur pengurutan rangking *Top & Bottom* Kabupaten-nya.

### 3. Kendali Navigasi Peta (Modebar)
- Mengaktifkan ulang panel kontrol navigasi peta bawaan Plotly dengan konfigurasi `displayModeBar: "hover"`. Fitur ini menambahkan kendali presisi seperti perbesaran layar (`+`/`-`), pergeseran kanvas (*pan*), dan *Reset View*, tanpa mengorbankan kebersihan antarmuka (*UI*) karena hanya akan muncul saat diletakkan kursor (*hover*).

---

## Sesi 28 April 2026 — Penyempurnaan EWS & Analisis Formal/Informal

### 1. Finalisasi Estetika EWS & Map Helper
- **Pembersihan EWS:** Menghapus emoji konvensional dari judul indikator EWS untuk kesan eksekutif. Mengaplikasikan ukuran *font* judul 15px dan warna gradasi dinamis (dari `#F8FAFC` ke *solid*) pada grafik mendatar (*Bar Chart*).
- **Ranking Visual:** Menambahkan penanda peringkat dinamis (`#1`, `#2`, `#3`) berdampingan langsung dengan ikon Medali/Piala (menggunakan *Inline-Flexbox* yang elastis) di kartu *Top & Bottom* Provinsi.

### 2. Fitur Interaktif EWS (Urutan & Satuan)
- **Toggle Urutan (Tertinggi vs Terendah):** Menambahkan kontrol interaktif untuk menukar arah pengurutan data *Top 10* pada mode *Bar Chart*, menimpa konfigurasi orientasi dasar indikator.
- **Toggle Satuan (Angka vs Persen):** Menambahkan konversi canggih yang merubah hitungan absolut menjadi rasio persentase riil. Algoritma ini mencari kolom total aktual (misal `PT` atau `PYB`) lalu membagi populasi metrik di suatu wilayah dengan total populasinya sendiri, menghasilkan *insight* prioritas wilayah baru yang berbasis keparahan rasio. Fitur ini cerdas mengabaikan metrik yang secara bawaan sudah berformat rasio.

### 3. Analisis Formal vs Informal (PYB)
- **Kalkulasi Lanjutan:** Mengonstruksi logika pembagian sektor riil menjadi Formal (menggabungkan Buruh Tetap + Karyawan/Pegawai) dan Informal (Berusaha sendiri, Bebas, dll).
- **Visualisasi Dual-Donut:** Menyandingkan grafik *Donut* Status Pekerjaan BPS lawas (7 klasifikasi) dengan *Donut Chart* Formal vs Informal yang menggunakan kontras warna kementerian (Teal dan Gold).
- **Ekspansi Treemap:** Merentangkan grafik balok bersarang (*Treemap*) untuk "Lapangan Usaha" menjadi seluas bentang layar penuh (`md=12`).

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
├── map_helper.py       ← Helper module untuk GeoMap & Ranking
├── pages/
│   ├── main.py         ← Ringkasan Ketenagakerjaan
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
