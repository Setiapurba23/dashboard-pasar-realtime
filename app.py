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
from dash.dependencies import State

# Daftar aset yang tersedia
tickers = {
    "Emas (GLD)": "GLD",
    "Minyak (USO)": "USO",
    "S&P 500": "^GSPC",
    "USD/IDR": "IDR=X",
    "Bitcoin": "BTC-USD"
}

# Inisialisasi aplikasi
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Styling modern melalui index_string
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
          integrity="sha512-pO6A5e+Q5Vpe+HjdbN2pyLDjDWq+U4SjXKQntwNVWQKblZ3I3GPo2F5y94uP8hjYxoTsB+J62FhLq6t84hU9EA=="
          crossorigin="anonymous"
          referrerpolicy="no-referrer"
        />
        <style>
            body, html {
                margin: 0; padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #121212;
                color: #eee;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            .card {
                background: #1e1e1e;
                border-radius: 14px;
                box-shadow: 0 6px 15px rgba(0,0,0,0.7);
                padding: 25px;
                margin: 25px auto;
                max-width: 1100px;
                transition: box-shadow 0.3s ease;
            }
            .card:hover {
                box-shadow: 0 12px 30px rgba(0,0,0,0.9);
            }
            h1, h3, h4 {
                color: #00bcd4;
                margin-bottom: 20px;
                font-weight: 700;
                letter-spacing: 0.05em;
            }
            .Select-control, .Select-menu-outer {
                border-radius: 10px !important;
                border: 1.8px solid #00bcd4 !important;
                background: #121212 !important;
                color: #eee !important;
                font-weight: 600;
                transition: border-color 0.25s ease;
                box-shadow: none !important;
            }
            .Select-control:hover {
                border-color: #00e5ff !important;
                box-shadow: 0 0 10px #00e5ff !important;
            }
            .Select-menu-outer {
                background: #222 !important;
                color: #eee !important;
            }
            .Select-option.is-focused {
                background-color: #00bcd4 !important;
                color: #121212 !important;
            }
            .stat-card {
                background: #00bcd4;
                border-radius: 12px;
                padding: 15px 22px;
                margin-bottom: 14px;
                font-weight: 700;
                color: #121212;
                box-shadow: inset 0 0 8px rgba(0,188,212,0.6);
                transition: background-color 0.3s ease;
            }
            .stat-card:hover {
                background-color: #00e5ff;
                cursor: default;
            }
            footer {
                text-align: center;
                font-size: 0.8em;
                color: #666;
                padding: 12px 0;
            }
            @media (max-width: 768px) {
                .card > div {
                    width: 100% !important;
                    display: block !important;
                }
            }
            #refresh-button {
                background: #00bcd4;
                border: none;
                color: #121212;
                font-weight: 700;
                padding: 10px 18px;
                border-radius: 10px;
                cursor: pointer;
                transition: background-color 0.3s ease;
                margin-left: 15px;
                font-size: 1em;
                vertical-align: middle;
                box-shadow: 0 4px 10px rgba(0,188,212,0.6);
            }
            #refresh-button:hover {
                background-color: #00e5ff;
                box-shadow: 0 6px 15px rgba(0,229,255,0.9);
            }
            #refresh-button:active {
                transform: scale(0.97);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>Dashboard Pasar Keuangan &bull; Created with <i class="fa fa-heart" style="color:#e91e63;"></i> by You</footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

# Layout utama
app.layout = html.Div([
    # Tombol toggle sidebar
    html.Button("👤 Profil Tim", id="toggle-button", n_clicks=0, style={
        "position": "fixed",
        "top": "20px",
        "left": "20px",
        "zIndex": "1000",
        "backgroundColor": "#00bcd4",
        "color": "#121212",
        "fontWeight": "700",
        "border": "none",
        "padding": "10px 15px",
        "borderRadius": "8px",
        "cursor": "pointer"
    }),

    # Sidebar profil (default tersembunyi)
    html.Div([
        html.H3("👥 Tim Dashboard"),
        html.P("Setia Hot Dameria Purba (122160021)"),
        html.P("Desi Wulandari (122160036)"),
        html.P("Raymon Dacesta Barus (122160053)"),
        html.P("Kiki Priadi Hutajulu (122160056)"),
        html.P("Arnodl Prananta Ginting (122160072)"),
        html.Hr(style={"borderColor": "#444"}),
        html.P("Program Studi Matematika"),
        html.P("Fakultas Sains"),
        html.P("Institut Teknologi Sumatera"),
    ], id="sidebar", style={
        "position": "fixed",
        "top": "70px",
        "left": "20px",
        "width": "260px",
        "backgroundColor": "#1e1e1e",
        "borderRadius": "14px",
        "padding": "20px",
        "color": "#eee",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.5)",
        "zIndex": "999",
        "display": "none"
    }),

    # Konten utama dashboard
    html.Div([
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
            dcc.Graph(id='insample-graph')
        ], className="card"),

        html.Div([
            html.H3("🔮 Prediksi Harga (30 Hari Mendatang)"),
            dcc.Graph(id='prediksi-graph'),
            html.Div(id='mape-output', style={"textAlign": "center", "marginTop": "10px"})
        ], className="card")
    ], style={"flex": "1", "marginLeft": "0px"})  # Tidak terganggu sidebar
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
    fig_harga.update_traces(line=dict(color='deepskyblue'))
    fig_harga.update_layout(template='plotly_dark')

    # Statistik deskriptif
    stats = hitung_statistik(df)
    stat_cards = [html.Div(f"{k}: {v:,.2f}", className="stat-card") for k, v in stats.items()]

    # Grafik perubahan harga
    fig_perubahan = px.line(df, x='Tanggal', y='Perubahan (%)', title="Laju Perubahan Harga (%)")
    fig_perubahan.update_traces(line=dict(color='lime'))
    fig_perubahan.update_layout(template='plotly_dark')

    # Prediksi ARIMA
    df.set_index('Tanggal', inplace=True)
    model, in_sample_pred, pred_df = buat_prediksi_autoarima(df['Harga'])

    # Grafik prediksi ke depan dengan CI
    fig_prediksi = go.Figure()
    fig_prediksi.add_trace(go.Scatter(
        x=pred_df['Tanggal'], y=pred_df['Prediksi'],
        mode='lines', name='Prediksi', line=dict(color='orange')
    ))
    fig_prediksi.add_trace(go.Scatter(
        x=pred_df['Tanggal'], y=pred_df['Upper Bound'],
        mode='lines', line=dict(width=0), showlegend=False
    ))
    fig_prediksi.add_trace(go.Scatter(
        x=pred_df['Tanggal'], y=pred_df['Lower Bound'],
        mode='lines', fill='tonexty', fillcolor='rgba(255,165,0,0.2)',
        line=dict(width=0), showlegend=False
    ))
    fig_prediksi.update_layout(template='plotly_dark', title='Prediksi Harga 30 Hari')

    # Grafik in-sample
    insample_df = pd.DataFrame({
        'Tanggal': df.index[-len(in_sample_pred):],
        'Data Asli': df['Harga'][-len(in_sample_pred):],
        'Output Model': in_sample_pred
    })
    fig_insample = px.line(insample_df, x='Tanggal', y=['Data Asli', 'Output Model'],
                           title="In-sample Fit: Data Asli vs Output Model")
    fig_insample.update_layout(template='plotly_dark')

    # MAPE
    y_true = df['Harga'][-len(in_sample_pred):]
    y_pred = in_sample_pred
    mape = hitung_mape(y_true, y_pred)
    mape_output = f"📉 MAPE Model (in-sample): {mape:.2f}%"

    return fig_harga, stat_cards, fig_perubahan, fig_prediksi, mape_output, fig_insample


@app.callback(
    Output("sidebar", "style"),
    [Input("toggle-button", "n_clicks")],
    [State("sidebar", "style")]
)
def toggle_sidebar(n_clicks, current_style):
    if n_clicks % 2 == 1:
        current_style["display"] = "block"
    else:
        current_style["display"] = "none"
    return current_style


# Jalankan server
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
