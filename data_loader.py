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
