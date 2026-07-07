import time
import requests
from keys import ALPHAVANTAGE_KEY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# -----------------------------
# CONFIGURATION
# -----------------------------
TICKERS = [
    "APAM.AS",   # Aperam
    "LIGHT.AS",  # Signify
    "PHIA.AS",   # Philips
    "PNL.AS",    # PostNL
    "TOM2.AS",   # TomTom
    "KPN.AS",    # KPN
    "FUR.AS"     # Fugro
]

TARGET_PRICES = [
    52.00,   # Aperam target
    17.50,   # Signify target
    25.50,   # Philips target
    0.98,    # PostNL target
    4.30,    # TomTom target
    4.00,    # KPN target
    10.00    # Fugro target
]



# -----------------------------
# FETCH PRICE FROM YAHOO FINANCE
# -----------------------------
def get_price_data(ticker):
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHAVANTAGE_KEY}"
    )

    r = requests.get(url)
    data = r.json()

    if "Global Quote" not in data:
        return None

    quote = data["Global Quote"]

    info = {
        "symbol": quote.get("01. symbol"),
        "open": float(quote.get("02. open", 0)),
        "high": float(quote.get("03. high", 0)),
        "low": float(quote.get("04. low", 0)),
        "price": float(quote.get("05. price", 0)),
        "volume": int(quote.get("06. volume", 0)),
        "latest_trading_day": quote.get("07. latest trading day"),
        "previous_close": float(quote.get("08. previous close", 0)),
        "change": float(quote.get("09. change", 0)),
        "change_percent": quote.get("10. change percent")
    }

    return info



# -----------------------------
# SEND TELEGRAM MESSAGE
# -----------------------------
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)



# -----------------------------
# MAIN LOGIC
# -----------------------------
def main():
    # send notification about run time
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    send_telegram(f"⏰ Notification at {now}")
    print(f"⏰ Notification at {now}")
    
    for ticker in TICKERS:
        info = get_price_data(ticker)

        if info is None:
            continue  # skip tickers with no data

        current = info["price"]
        previous = info["previous_close"]
        change = info["change"]
        target = TARGET_PRICES[TICKERS.index(ticker)]
        diff = current - target

        # percentage difference from target
        diff_percent = (diff / target) * 100

        # if current price is within 1% of target → send alert
        if abs(diff_percent) <= 1:
            message = (
                f"🔹 {ticker}\n"
                f"Current: €{current:.2f}\n"
                f"Target: €{target:.2f}\n"
                f"Diff: {diff:.2f} ({diff_percent:.2f}%)\n"
                f"Prev Close: €{previous:.2f}\n"
                f"Change: {change:.2f}\n"
            )

            print(message)
            send_telegram(message)

        else:
            # send simple message to confirm Telegram is working
            test_msg = f"{ticker}: No notification — just checking if msg is working"
            print(test_msg)
            send_telegram(test_msg)

        # wait between messages
        time.sleep(15)



if __name__ == "__main__":
    main()
