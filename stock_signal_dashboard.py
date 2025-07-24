import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 🔁 Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="data_refresh")

# Stock list
stock_list = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ACC.NS", "ADANIENT.NS",
    "AMBUJACEM.NS", "APOLLOHOSP.NS", "JSWSTEEL.NS", "JINDALSTEL.NS",
    "CHOLAFIN.NS", "BHARATFORG.NS", "WOCKPHARMA.NS"
]

st.set_page_config(page_title="Stock Signal Dashboard", layout="wide")
st.title("📊 Stock Signal Dashboard")
st.caption("Logic: Green candle + volume spike → WATCH. Price falls below open → SELL.")

# Filter selection
filter_option = st.selectbox("Filter signals:", ["All", "WATCHING", "SELL"])

tz = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(tz)
results = []

for symbol in stock_list:
    try:
        df = yf.download(symbol, interval="5m", period="10m", progress=False)
        if len(df) < 2:
            continue

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        if latest["Close"] > latest["Open"] and latest["Volume"] > prev["Volume"]:
            live_price = yf.Ticker(symbol).info['regularMarketPrice']
            signal = "WATCHING"
            if live_price < latest["Open"]:
                signal = "SELL"
            results.append({
                "Stock": symbol,
                "Signal": signal,
                "Candle Open": round(latest["Open"], 2),
                "Live Price": round(live_price, 2),
                "Volume": int(latest["Volume"]),
                "Prev Volume": int(prev["Volume"]),
                "Last Checked": now.strftime('%Y-%m-%d %H:%M:%S')
            })

    except Exception as e:
        st.warning(f"⚠️ Error loading {symbol}: {e}")

if results:
    df_result = pd.DataFrame(results)

    if filter_option == "WATCHING":
        df_result = df_result[df_result["Signal"] == "WATCHING"]
    elif filter_option == "SELL":
        df_result = df_result[df_result["Signal"] == "SELL"]

    st.dataframe(df_result, use_container_width=True)
else:
    st.info("No matching signals found right now.")

st.caption("⏱ Updated at: " + now.strftime('%Y-%m-%d %H:%M:%S'))
