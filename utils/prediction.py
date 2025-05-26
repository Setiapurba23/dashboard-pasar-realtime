# utils/prediction.py
import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.arima.model import ARIMA

def cari_order_arima_terbaik(series, p_range=range(0, 4), d_range=range(0, 2), q_range=range(0, 4)):
    best_aic = float('inf')
    best_order = None
    warnings.filterwarnings("ignore")  # Supress convergence warnings

    for p in p_range:
        for d in d_range:
            for q in q_range:
                try:
                    model = ARIMA(series, order=(p, d, q))
                    model_fit = model.fit()
                    aic = model_fit.aic
                    if aic < best_aic:
                        best_aic = aic
                        best_order = (p, d, q)
                except:
                    continue
    return best_order

def buat_prediksi_autoarima(series, langkah=30):
    series = series.dropna()

    # Cari parameter terbaik ARIMA
    best_order = cari_order_arima_terbaik(series)
    if best_order is None:
        raise ValueError("Tidak ditemukan model ARIMA yang valid untuk data ini.")

    model = ARIMA(series, order=best_order)
    model_fit = model.fit()

    # Prediksi in-sample (untuk evaluasi)
    d = best_order[1]
    in_sample_pred = model_fit.predict(start=d, end=len(series)-1, typ='levels')

    # Prediksi ke depan + interval
    forecast = model_fit.get_forecast(steps=langkah)
    pred_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()

    last_date = series.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=langkah, freq='B')

    pred_df = pd.DataFrame({
        'Tanggal': future_dates,
        'Prediksi': pred_mean.values,
        'Lower Bound': conf_int.iloc[:, 0].values,
        'Upper Bound': conf_int.iloc[:, 1].values
    })

    return model_fit, in_sample_pred, pred_df

def hitung_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
