"""
Data loading, filtering, and GeoJSON utilities.
"""

import pandas as pd
import numpy as np
import datetime
import re
import json

# ─── Data Loader ─────────────────────────────────────────────────────────────────
_cache = {}

def fix_ratio(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, pd.Timedelta):
        comps = val.components
        hours = comps.days * 24 + comps.hours
        return float(f"{hours}.{comps.minutes:02d}")
    if isinstance(val, datetime.time):
        return float(f"{val.hour}.{val.minute:02d}")
    
    val_str = str(val).strip()
    match_days = re.search(r'(\d+)\s*days?,?\s*(\d+):(\d+)(?::(\d+))?', val_str, re.IGNORECASE)
    if match_days:
        days = int(match_days.group(1))
        hours = int(match_days.group(2))
        mins = int(match_days.group(3))
        total_hours = days * 24 + hours
        return float(f"{total_hours}.{mins:02d}")
    
    match_time = re.search(r'^(\d+):(\d+)(?::(\d+))?$', val_str)
    if match_time:
        hours = int(match_time.group(1))
        mins = int(match_time.group(2))
        return float(f"{hours}.{mins:02d}")
        
    try:
        return float(val_str.replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0

def load_data(path: str) -> pd.DataFrame:
    if path in _cache:
        return _cache[path]
    df = pd.read_excel(path)
    df['thn'] = df['thn'].astype(int)
    df['lvl_wil'] = df['lvl_wil'].astype(str).str.lower()
    df['nm_prov']   = df['nm_prov'].fillna('NASIONAL')
    df['nm_kabkot'] = df['nm_kabkot'].fillna('-')
    text_cols = {'thn', 'lvl_wil', 'kd_prov', 'nm_prov', 'kd_kabkot', 'nm_kabkot'}
    
    is_ratio = any(x in path for x in ['TPAK', 'TPT', 'EPR'])
    
    for col in df.columns:
        if col not in text_cols:
            if is_ratio:
                df[col] = df[col].apply(fix_ratio)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    for tc in ['PUK', 'AK', 'PYB', 'PT', 'TPAK', 'TPT', 'EPR']:
        if tc in df.columns:
            df['total'] = df[tc]
            break
    if 'total' not in df.columns and 'jk_lk' in df.columns and 'jk_pr' in df.columns:
        df['total'] = df['jk_lk'] + df['jk_pr']
    _cache[path] = df
    return df


# ─── GeoJSON Loader ──────────────────────────────────────────────────────────────
_geojson_cache = None

# Mapping nama provinsi BPS → nama di GeoJSON (hanya yang beda)
_PROV_NAME_TO_GEO = {
    'Bangka Belitung': 'Kepulauan Bangka Belitung',
    'D I Yogyakarta': 'Daerah Istimewa Yogyakarta',
}

_PROV_NAME_TO_GEO_KABKOT = {
    'DKI Jakarta': 'Jakarta Raya',
    'D I Yogyakarta': 'Yogyakarta',
    'Papua Barat Daya': 'Papua Barat',
    'Papua Pegunungan': 'Papua',
    'Papua Selatan': 'Papua',
    'Papua Tengah': 'Papua'
}

def load_geojson():
    global _geojson_cache
    if _geojson_cache is not None:
        return _geojson_cache
    with open('Database/indonesia-provinces.geojson', 'r') as f:
        _geojson_cache = json.load(f)
    return _geojson_cache


_geojson_kabkot_cache = None

def load_geojson_kabkot():
    global _geojson_kabkot_cache
    if _geojson_kabkot_cache is not None:
        return _geojson_kabkot_cache
    with open('Database/indonesia-kabkot-simplified.geojson', 'r') as f:
        _geojson_kabkot_cache = json.load(f)
    return _geojson_kabkot_cache


def filter_data(df, year, level, prov=None, kabkot=None):
    d = df[df['thn'] == year]
    if level == 'nasional':
        return d[d['lvl_wil'] == 'nasional']
    elif level == 'provinsi':
        return d[(d['lvl_wil'] == 'provinsi') & (d['nm_prov'] == prov)]
    elif level == 'kabupaten':
        return d[(d['lvl_wil'].isin(['kabupaten', 'kota'])) & (d['nm_kabkot'] == kabkot)]
    return d


def fmt_compact(val):
    if val >= 1_000_000:
        v = val / 1_000_000
        return f"{v:.1f}M" if v % 1 else f"{int(v)}M"
    elif val >= 1_000:
        v = val / 1_000
        return f"{v:.1f}K" if v % 1 else f"{int(v)}K"
    return f"{val:,.0f}"



# ─── Static data for filters (always PUK as geo reference) ───────────────────────
try:
    _GEO = load_data("Database/PUK-2018-2025-ver2.xlsx")
    _YEARS = sorted(_GEO['thn'].unique(), reverse=True)
    _PROV_DF = (
        _GEO[_GEO['nm_prov'] != 'NASIONAL'][['kd_prov', 'nm_prov']]
        .drop_duplicates().sort_values('kd_prov')
    )
    _PROV_LIST = _PROV_DF['nm_prov'].tolist()
    DATA_AVAILABLE = True
except Exception:
    _YEARS = list(range(2018, 2026))
    _PROV_LIST = []
    DATA_AVAILABLE = False



def trend_filter(df, level, prov, kab):
    if level == "nasional":   return df[df['lvl_wil'] == 'nasional']
    if level == "provinsi":   return df[(df['lvl_wil'] == 'provinsi') & (df['nm_prov'] == prov)]
    if level == "kabupaten":  return df[(df['lvl_wil'].isin(['kabupaten','kota'])) & (df['nm_kabkot'] == kab)]
    return df
_KABKOT_NAME_TO_GEO = {
    'Labuhan Batu': 'Labuhanbatu',
    'Pakpak Bharat': 'Pakpak Barat',
    'Labuhan Batu Selatan': 'Labuhanbatu Selatan',
    'Labuhan Batu Utara': 'Labuhanbatu Utara',
    'Tanjung Balai': 'Kota Tanjungbalai',
    'Pematang Siantar': 'Pematangsiantar',
    'Tebing Tinggi': 'Tebingtinggi',
    'Medan': 'Kota Medan',
    'Binjai': 'Kota Binjai',
    'Sawah Lunto': 'Sawahlunto',
    'Kota Dumai': 'Dumai',
    'Pangkal Pinang': 'Pangkalpinang',
    'Kota Batam': 'Batam',
    'Tanjung Pinang': 'Tanjungpinang',
    'Kota Banjar': 'Banjar',
    'Yogyakarta': 'Kota Yogyakarta',
    'Karang Asem': 'Karangasem',
    'Baubau': 'Bau-Bau',
}

_PROV_BOUNDS = {
    'Aceh': {'west': 95.00970459, 'east': 98.28495789, 'south': 2.00810719, 'north': 6.07694054},
    'Bali': {'west': 114.43178558, 'east': 115.71130371, 'south': -8.84905338, 'north': -8.06179428},
    'Bangka Belitung': {'west': 105.10800171, 'east': 108.84799194, 'south': -3.4165349, 'north': -1.50188446},
    'Banten': {'west': 105.10054016, 'east': 106.77993774, 'south': -7.01511002, 'north': -5.80756569},
    'Bengkulu': {'west': 101.02232361, 'east': 103.76748657, 'south': -5.44246244, 'north': -2.27675128},
    'Gorontalo': {'west': 121.16124725, 'east': 123.55229187, 'south': 0.305967, 'north': 1.0410111},
    'Jakarta Raya': {'west': 106.38317871, 'east': 106.97189331, 'south': -6.37023163, 'north': -5.1844573},
    'Jambi': {'west': 101.12862396, 'east': 104.49739838, 'south': -2.77119875, 'north': -0.73329467},
    'Jawa Barat': {'west': 106.37055206, 'east': 108.83381653, 'south': -7.823071, 'north': -5.9142499},
    'Jawa Tengah': {'west': 108.55590057, 'east': 111.69140625, 'south': -8.21103859, 'north': -5.72572041},
    'Jawa Timur': {'west': 110.89974976, 'east': 116.27014923, 'south': -8.78030968, 'north': -5.04885721},
    'Kalimantan Barat': {'west': 108.67784119, 'east': 114.19824219, 'south': -3.06762958, 'north': 2.08096623},
    'Kalimantan Selatan': {'west': 114.34626007, 'east': 116.55476379, 'south': -4.74481297, 'north': -1.31503952},
    'Kalimantan Tengah': {'west': 110.73222351, 'east': 115.84696198, 'south': -3.54185033, 'north': 0.79313916},
    'Kalimantan Timur': {'west': 113.83665466, 'east': 118.98948669, 'south': -2.40868139, 'north': 2.6065557},
    'Kalimantan Utara': {'west': 114.56666565, 'east': 117.98799133, 'south': 1.04372931, 'north': 4.40296078},
    'Kepulauan Riau': {'west': 103.28524017, 'east': 109.16396332, 'south': -1.29836392, 'north': 4.7940135},
    'Lampung': {'west': 103.57125092, 'east': 106.21143341, 'south': -6.16855812, 'north': -3.72382259},
    'Maluku': {'west': 125.71851349, 'east': 134.90838623, 'south': -8.34106541, 'north': -1.38064957},
    'Maluku Utara': {'west': 124.28347778, 'east': 129.65371704, 'south': -2.47734118, 'north': 2.64397764},
    'Nusa Tenggara Barat': {'west': 115.82099152, 'east': 119.33580017, 'south': -9.1088829, 'north': -8.08005428},
    'Nusa Tenggara Timur': {'west': 118.92913055, 'east': 125.18756104, 'south': -11.00761509, 'north': -8.06335735},
    'Papua': {'west': 134.29566956, 'east': 141.01939392, 'south': -9.11892414, 'north': 0.93779665},
    'Papua Barat': {'west': 129.30770874, 'east': 135.25798035, 'south': -4.25427103, 'north': 0.58223522},
    'Riau': {'west': 100.02484894, 'east': 103.81461334, 'south': -1.12227285, 'north': 2.91912794},
    'Sulawesi Barat': {'west': 117.06947327, 'east': 119.87540436, 'south': -3.56903267, 'north': -0.84673607},
    'Sulawesi Selatan': {'west': 117.03848267, 'east': 121.8396759, 'south': -7.75840521, 'north': -1.8972863},
    'Sulawesi Tengah': {'west': 119.44742584, 'east': 124.18152618, 'south': -3.64074349, 'north': 1.3739239},
    'Sulawesi Tenggara': {'west': 120.86568451, 'east': 124.62190247, 'south': -6.21338749, 'north': -2.77940845},
    'Sulawesi Utara': {'west': 123.11084747, 'east': 127.16303253, 'south': 0.29155996, 'north': 5.56416416},
    'Sumatera Barat': {'west': 98.59764862, 'east': 101.89291382, 'south': -3.34996891, 'north': 0.90646428},
    'Sumatera Selatan': {'west': 102.06745148, 'east': 106.188797, 'south': -4.96004057, 'north': -1.62544119},
    'Sumatera Utara': {'west': 97.06072998, 'east': 100.42276764, 'south': -0.63876051, 'north': 4.30146551},
    'Yogyakarta': {'west': 110.0139389, 'east': 110.83421326, 'south': -8.20357704, 'north': -7.54184151},
}
