import yfinance as yf
import requests
import datetime
import pytz
import time

# === YOUR CONFIG ===
BOT_TOKEN = "your_bot_token_here"
CHAT_ID = "your_chat_id_here"

stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ACC.NS", "ADANIENT.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS",
    "JSWSTEEL.NS", "JINDALSTEL.NS", "CHOLAFIN.NS", "BHARATFORG.NS", "WOCKPHARMA.NS", "AUROPHARMA.NS"
]

# === TELEGRAM ALERT FUNCTION ===
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Failed to send Telegram message:", e)

def check_signal(stock):
    try:
        df = yf.download(stock, period="1d", interval="5m", auto_adjust=False, progress=False)
        if df is None or df.empty or len(df) < 2:
            print(f"No data for {stock}")
            return None

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # FIXED: Using .item() safely
        latest_close = latest["Close"].item()
        latest_open = latest["Open"].item()
        latest_volume = latest["Volume"].item()
        previous_volume = previous["Volume"].item()

        is_green = latest_close > latest_open
        volume_spike = latest_volume > previous_volume

        if is_green and volume_spike:
            return f"📈 {stock} signal detected!\nPrice: {latest_close:.2f}\nVolume: {int(latest_volume)}"
        return None

    except Exception as e:
        print(f"Error checking {stock}: {e}")
        return None


# === MAIN SCRIPT ===
def run():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    print(f"🔍 Running check at {now}")

    for stock in stocks:
        signal = check_signal(stock)
        if signal:
            send_telegram_alert(signal)
        time.sleep(3)  # delay to prevent rate-limit block

if __name__ == "__main__":
    run()
