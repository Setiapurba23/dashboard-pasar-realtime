import yfinance as yf
import pandas as pd

def load_yfinance_data(ticker, period="1y", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval)
    df.reset_index(inplace=True)
    df.rename(columns={'Date': 'Tanggal', 'Close': 'Harga'}, inplace=True)
    return df[['Tanggal', 'Harga']]
