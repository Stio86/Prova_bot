
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = "7603257716:AAHYHZF8H6S-LyuXp8l-h1W0h40fSPp3WZU"
CHAT_ID = "66336138"
HEADERS = {"User-Agent": "Mozilla/5.0"}
SOFA_LIVE_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print(f"[Telegram Error] {e}")

def get_quote(match_id):
    try:
        url = f"https://api.sofascore.com/api/v1/event/{match_id}/odds/pre-match"
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        for market in data.get("markets", []):
            if market.get("name") == "Match Winner":
                outcomes = market.get("outcomes", [])
                if len(outcomes) >= 2:
                    home_odd = outcomes[0].get("value")
                    away_odd = outcomes[1].get("value")
                    return home_odd, away_odd
        return None, None
    except:
        return None, None

def check_all_matches():
    try:
        res = requests.get(SOFA_LIVE_URL, headers=HEADERS)
        data = res.json()
        msg_lines = []

        for event in data.get("events", []):
            tournament = event["tournament"]["name"]
            category = event["tournament"]["category"]["name"]
            if not ("ATP" in category or "WTA" in category):
                continue

            match_id = event["id"]
            home = event["homeTeam"]["name"]
            away = event["awayTeam"]["name"]

            home_odd, away_odd = get_quote(match_id)

            msg = f"🎾 {category} {tournament}: {home} vs {away}"
            if home_odd and away_odd:
                msg += f" — Quote: {home} @ {home_odd}, {away} @ {away_odd}"
            else:
                msg += " — (quote non disponibili)"
            msg_lines.append(msg)

        if msg_lines:
            send_telegram("📋 Match ATP/WTA live trovati:" + "\n".join(msg_lines))
            print("[+] Notifica inviata.")
        else:
            print("[!] Nessun match ATP/WTA live trovato.")
    except Exception as e:
        print(f"[Errore parsing Sofascore] {e}")

@app.route("/")
def home():
    return "Bot test Sofascore (tutti i match ATP/WTA live)."

if __name__ == "__main__":
    send_telegram("🔍 Bot TEST avviato: tutti i match ATP/WTA live (con quote)")
    threading.Thread(target=check_all_matches, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
