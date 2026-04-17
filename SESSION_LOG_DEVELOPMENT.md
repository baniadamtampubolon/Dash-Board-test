# Project Dash Labor Board - Session Development Log
**Tanggal:** 16 April 2026
**Status:** Stabil & Integrasi Selesai

## 1. Integrasi Dataset Rasio (TPAK, TPT, EPR)
Telah diintegrasikan tiga indikator rasio utama dengan dataset versi terbaru (`ver2.xlsx`):
- **TPAK:** Tingkat Partisipasi Angkatan Kerja (Rasio AK / PUK)
- **TPT:** Tingkat Pengangguran Terbuka (Rasio PT / AK)
- **EPR:** Employment to Population Ratio (Rasio PYB / PUK)

## 2. Fitur Data Engineering
- **Fix Ratio Logic:** Implementasi fungsi `fix_ratio(val)` di `app.py` untuk otomatis mendeteksi dan memperbaiki data Excel yang korup (terbaca sebagai `timedelta` atau `datetime`).
- **Standardisasi Filter:** Memastikan filtering tahun, level (Nasional/Provinsi/Kabupaten), dan wilayah sinkron di seluruh dashboard.

## 3. Desain UI & Visualisasi (Update Terakhir)
Dashboard rasio kini menggunakan layout premium dengan variasi chart:
- **Line Chart (Age Groups):** Menggantikan bar chart untuk melihat distribusi umur yang lebih halus.
- **Donut Charts (Gender & Wilayah):** Memberikan variasi visual dan fokus pada perbandingan proporsi.
- **Full-Width Trend Section:** Tren historis 2018-2025 dipindahkan ke bagian bawah dengan area grafik yang luas agar mudah dibaca.
- **Padding & Margin:** Penyesuaian `xaxis range` dan `margin` pada Plotly agar angka di ujung grafik tidak terpotong.

## 4. Akses & Testing
- **Server:** Dikonfigurasi untuk `host='0.0.0.0'` agar bisa diakses dalam jaringan lokal (WiFi).
- **Port:** `8050` untuk dashboard utama (`app.py`) dan `8060` untuk testing area (`test.py`).
- **Localtunnel:** Panduan penggunaan `npx localtunnel --port 8050` disertakan dalam history chat untuk akses publik/remote.

## 5. File Penting
- `app.py`: Aplikasi utama.
- `test.py`: Playground testing.
- `Database/`: Folder penyimpanan file `.xlsx`.
- `assets/`: File CSS dan styling.

---
*Log dikelola secara otomatis untuk menjaga kontinuitas pengembangan.*
