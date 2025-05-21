# app.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Modul lokal
from utils.yf_loader import load_yfinance_data
from utils.stats import hitung_statistik, hitung_laju_perubahan
from utils.prediction import buat_prediksi_autoarima, hitung_mape

# Daftar aset yang tersedia
tickers = {
    "Emas (GLD)": "GLD",
    "Minyak (USO)": "USO",
    "S&P 500": "^GSPC",
    "USD/IDR": "IDR=X",
    "Bitcoin": "BTC-USD"
}



# Layout utama
app.layout = html.Div([
    html.Div([
        html.H1("📊 Dashboard Pasar Keuangan Realtime"),
        html.Label("📈 Pilih Aset:"),
        dcc.Dropdown(
            id='ticker-dropdown',
            options=[{"label": k, "value": v} for k, v in tickers.items()],
            value="GLD"
        )
    ], className="card"),

    html.Div([
        html.Div([
            dcc.Graph(id='harga-graph')
        ], style={"width": "70%", "display": "inline-block", "verticalAlign": "top"}),

        html.Div([
            html.H4("📊 Statistik Deskriptif (1 Tahun Terakhir)"),
            html.Div(id='statistik-container')
        ], style={"width": "28%", "display": "inline-block", "paddingLeft": "20px"})
    ], className="card"),

    html.Div([
        html.H3("📈 Laju Perubahan Harian"),
        dcc.Graph(id='perubahan-graph')
    ], className="card"),

    html.Div([
        html.H3("📉 Perbandingan In-Sample: Data Asli vs Output Model"),
        dcc.Graph(id='insample-graph'),
        # Bagian persamaan ARIMA dihilangkan
        # html.H4("🧮 Persamaan ARIMA"),
        # html.Div(id='formula-arima', style={"fontFamily": "monospace", "whiteSpace": "pre-wrap"})
    ], className="card"),

    html.Div([
        html.H3("🔮 Prediksi Harga (30 Hari Mendatang)"),
        dcc.Graph(id='prediksi-graph'),
        html.Div(id='mape-output', style={"textAlign": "center", "marginTop": "10px"})
    ], className="card")
])

# Callback utama
@app.callback(
    [Output('harga-graph', 'figure'),
     Output('statistik-container', 'children'),
     Output('perubahan-graph', 'figure'),
     Output('prediksi-graph', 'figure'),
     Output('mape-output', 'children'),
     Output('insample-graph', 'figure')],
    [Input('ticker-dropdown', 'value')]
)
def update_dashboard(ticker):
    df = load_yfinance_data(ticker)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = hitung_laju_perubahan(df)

    # Grafik harga historis
    fig_harga = px.line(df, x='Tanggal', y='Harga', title="Harga Historis")

    # Statistik deskriptif
    stats = hitung_statistik(df)
    stat_cards = [html.Div(f"{k}: {v:,.2f}", className="stat-card") for k, v in stats.items()]

    # Grafik perubahan harga
    fig_perubahan = px.line(df, x='Tanggal', y='Perubahan (%)', title="Laju Perubahan Harga (%)")

    # Prediksi ARIMA
    df.set_index('Tanggal', inplace=True)
    model, in_sample_pred, pred_df = buat_prediksi_autoarima(df['Harga'])

    # Grafik prediksi ke depan dengan CI
    fig_prediksi = go.Figure()
    fig_prediksi.add_trace(go.Scatter(
        x=pred_df['Tanggal'], y=pred_df['Prediksi'],
        mode='lines', name='Prediksi'
    ))
    fig_prediksi.add_trace(go.Scatter(
        x=pred_df['Tanggal'], y=pred_df['Upper Bound'],
        mode='lines', line=dict(width=0), showlegend=False
    ))
    fig_prediksi.add_trace(go.Scatter(
        x=pred_df['Tanggal'], y=pred_df['Lower Bound'],
        mode='lines', fill='tonexty', fillcolor='rgba(0,100,80,0.2)',
        line=dict(width=0), showlegend=False
    ))
    fig_prediksi.update_layout(title='Prediksi Harga 30 Hari')

    # Grafik in-sample
    insample_df = pd.DataFrame({
        'Tanggal': df.index[-len(in_sample_pred):],
        'Data Asli': df['Harga'][-len(in_sample_pred):],
        'Output Model': in_sample_pred
    })
    fig_insample = px.line(insample_df, x='Tanggal', y=['Data Asli', 'Output Model'],
                           title="In-sample Fit: Data Asli vs Output Model")

    # MAPE
    y_true = df['Harga'][-len(in_sample_pred):]
    y_pred = in_sample_pred
    mape = hitung_mape(y_true, y_pred)
    mape_output = f"📉 MAPE Model (in-sample): {mape:.2f}%"

    return fig_harga, stat_cards, fig_perubahan, fig_prediksi, mape_output, fig_insample

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
