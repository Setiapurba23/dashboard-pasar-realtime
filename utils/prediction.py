# utils/prediction.py
import pandas as pd
import numpy as np
from pmdarima import auto_arima

def buat_prediksi_autoarima(series, langkah=30):
    series = series.dropna()

    model = auto_arima(
        series,
        seasonal=True,
        m=5,  # 5 hari kerja/minggu
        suppress_warnings=True,
        error_action='ignore',
        stepwise=True
    )

    # Prediksi in-sample (untuk evaluasi)
    in_sample_pred = model.predict_in_sample()

    # Prediksi ke masa depan + interval
    prediksi, conf_int = model.predict(n_periods=langkah, return_conf_int=True)

    last_date = series.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=langkah, freq='B')

    pred_df = pd.DataFrame({
        'Tanggal': future_dates,
        'Prediksi': prediksi,
        'Lower Bound': conf_int[:, 0],
        'Upper Bound': conf_int[:, 1]
    })

    return model, in_sample_pred, pred_df

def hitung_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
