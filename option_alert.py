import time
import requests
from keys import ALPHAVANTAGE_KEY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# -----------------------------
# CONFIGURATION
# -----------------------------
CALL_TICKERS = [
    "APAM.AS",
    "LIGHT.AS",
    "PHIA.AS"
]

CALL_TARGETS = [
    50.00,   # Aperam
    16.80,   # Signify
    25.00    # Philips
]

PUT_TICKERS = [
    "PNL.AS",
    "TOM2.AS",
    "KPN.AS",
    "FUR.AS"
]

PUT_TARGETS = [
    0.92,   # PostNL
    4.40,   # TomTom
    4.00,   # KPN
    10.00   # Fugro
]

# -----------------------------
# FETCH PRICE
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

    return {
        "symbol": quote.get("01. symbol"),
        "price": float(quote.get("05. price", 0)),
        "previous_close": float(quote.get("08. previous close", 0)),
        "change": float(quote.get("09. change", 0))
    }

# -----------------------------
# SEND TELEGRAM MESSAGE
# -----------------------------
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

# -----------------------------
# MAIN LOGIC
# -----------------------------
def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    send_telegram(f"\n⏰ Stock Check — {now} CET")

    any_alert = False

    # ----- CALL SECTION -----
    for ticker, target in zip(CALL_TICKERS, CALL_TARGETS):
        info = get_price_data(ticker)
        if info is None:
            continue

        current = info["price"]

        if current > target:
            any_alert = True
            msg = (
                f"📈 CALL ALERT\n"
                f"{ticker}: €{current:.2f} > target (€{target:.2f})\n"
            )
            send_telegram(msg)

        time.sleep(13)

    # ----- PUT SECTION -----
    for ticker, target in zip(PUT_TICKERS, PUT_TARGETS):
        info = get_price_data(ticker)
        if info is None:
            continue

        current = info["price"]

        if current < target:
            any_alert = True
            msg = (
                f"📉 PUT ALERT\n"
                f"{ticker}: €{current:.2f} < target (€{target:.2f})\n"
            )
            send_telegram(msg)

        time.sleep(13)

    # ----- NO ALERT -----
    if not any_alert:
        send_telegram(f"ℹ️ No alerts — ({now} CET)")

if __name__ == "__main__":
    main()
