# utils/stats.py
import pandas as pd
import numpy as np

def hitung_statistik(df):
    df_tahun = df[df['Tanggal'] >= df['Tanggal'].max() - pd.Timedelta(days=365)]
    harga = df_tahun['Harga']

    statistik = {
        'Maksimum': harga.max(),
        'Minimum': harga.min(),
        'Rata-rata': harga.mean(),
        'Median': harga.median(),
        'Range': harga.max() - harga.min(),
        'Standar Deviasi': harga.std()
    }

    return statistik

def hitung_laju_perubahan(df):
    df = df.copy()
    df['Perubahan (%)'] = df['Harga'].pct_change() * 100
    return df
