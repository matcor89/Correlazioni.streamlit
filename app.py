import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# Asset sample
ASSETS = {
    'Azioni': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'LDO.MI'],
    'ETF': ['SPY', 'QQQ', 'GLD', 'TLT', 'XLK', 'XLF', 'SPHB'],
    'Crypto': ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LINK-USD', 'ADA-USD', 'SOL-USD'],
    'Valute': ['AUDCAD=X', 'AUDCHF=X', 'AUDJPY=X', 'AUDNZD=X', 'AUDUSD=X', 'CADCHF=X', 'CADJPY=X', 'CHFJPY=X', 'EURAUD=X', 'EURCAD=X', 'EURCHF=X', 'EURGBP=X', 'EURJPY=X', 'EURNZD=X', 'EURSEK=X', 'EURUSD=X', 'GBPAUD=X', 'GBPCAD=X', 'GBPCHF=X', 'GBPJPY=X', 'GBPNZD=X', 'GBPUSD=X', 'NZDCAD=X', 'NZDCHF=X', 'NZDJPY=X', 'NZDUSD=X', 'USDCAD=X', 'USDCHF=X', 'USDCNH=X', 'USDJPY=X', 'USDSEK=X', 'USDBRL=X'],
    'Indici': ['^N225', '^NSEI', '^STOXX50E', '^IBEX', '^GDAXI', '^FCHI', 'FTSEMIB.MI', '^FTSE', '^SPX', '^VIX', '000300.SS', '^HSI', '^NDX', 'RTY=F'],
    'Commodities': ['GC=F', 'CL=F', 'SI=F', 'NG=F', 'HG=F']
}

st.set_page_config(page_title="Correlazioni Asset Finanziari", layout="wide")

st.title("Correlazioni tra Asset Finanziari - Multi Asset & Interattivo")

# Selezione tipo di asset
asset_types = st.multiselect("Seleziona tipo/i di asset:", list(ASSETS.keys()), default=list(ASSETS.keys()))

# Lista ticker da tipi selezionati
tickers = []
for t in asset_types:
    tickers.extend(ASSETS[t])

# Selezione asset specifici
selected_assets = st.multiselect("Seleziona asset da includere nell'analisi:", tickers, default=tickers[:10])

if len(selected_assets) < 2:
    st.warning("Seleziona almeno due asset per calcolare la correlazione.")
    st.stop()

# Selezione data inizio
end_date = datetime.date.today()
start_date = st.date_input("Data inizio", end_date - datetime.timedelta(days=365*2), max_value=end_date)

# Selezione timeframe
timeframe = st.selectbox("Seleziona il timeframe", options=["1d", "1h", "30m", "15m", "5m", "1m"], index=0)

# Scarica dati
@st.cache_data(show_spinner=True)
def download_data(tickers, start, end, interval):
    data = yf.download(tickers, start=start, end=end, interval=interval, group_by='ticker', progress=False)
    close_prices = pd.DataFrame()
    for ticker in tickers:
        if ticker in data.columns.levels[0]:
            close_prices[ticker] = data[ticker]['Close']
        else:
            close_prices[ticker] = data['Close']
    return close_prices

prices = download_data(selected_assets, start_date, end_date, timeframe)
prices.dropna(how='all', inplace=True)
prices.fillna(method='ffill', inplace=True)

# Calcola e arrotonda la matrice di correlazione
corr = prices.corr().round(2)

# Heatmap
st.subheader("Matrice di Correlazione")
fig = px.imshow(corr,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                origin='lower',
                labels=dict(x="Asset", y="Asset", color="Correlazione"),
                title="Correlazione Pearson tra asset")
st.plotly_chart(fig, use_container_width=True)

# Line chart
st.subheader("Grafico comparativo prezzi")
selected_for_chart = st.multiselect("Seleziona asset da visualizzare nel grafico:", selected_assets, default=selected_assets[:3])
if selected_for_chart:
    fig2 = px.line(prices[selected_for_chart], labels={'value': 'Prezzo', 'index': 'Data'}, title='Prezzi storici selezionati')
    st.plotly_chart(fig2, use_container_width=True)
