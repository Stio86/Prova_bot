
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = "7603257716:AAHYHZF8H6S-LyuXp8l-h1W0h40fSPp3WZU"
CHAT_ID = "66336138"
CHECK_INTERVAL = 300  # ogni 5 minuti
QUOTE_LIMIT = 1.70
SOFA_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print(f"[Telegram Error] {e}")

def check_favoriti_sofa():
    try:
        print("[*] Controllo match Sofascore in corso...")
        res = requests.get(SOFA_URL, headers=HEADERS)
        data = res.json()
        msg_lines = []

        for event in data.get("events", []):
            tournament = event["tournament"]["name"]
            category = event["tournament"]["category"]["name"]

            if not ("ATP" in category or "WTA" in category):
                continue

            home = event["homeTeam"]["name"]
            away = event["awayTeam"]["name"]

            # Verifica quote se presenti
            markets = event.get("markets", [])
            for market in markets:
                if market.get("name") == "Match Winner":
                    outcomes = market.get("outcomes", [])
                    if len(outcomes) >= 2:
                        home_odd = outcomes[0].get("value")
                        away_odd = outcomes[1].get("value")
                        if home_odd and home_odd < QUOTE_LIMIT:
                            msg_lines.append(f"🎾 {category} {tournament}:
{home} ({home_odd}) vs {away}")
                        elif away_odd and away_odd < QUOTE_LIMIT:
                            msg_lines.append(f"🎾 {category} {tournament}:
{home} vs {away} ({away_odd})")
                    break

        if msg_lines:
            send_telegram("📋 Match con favorito < 1.70:
" + "\n".join(msg_lines))
            print("[+] Notifica inviata.")
        else:
            print("[!] Nessun favorito < 1.70 trovato.")

    except Exception as e:
        print(f"[Errore parsing Sofascore] {e}")

@app.route("/")
def home():
    return "Bot Sofascore attivo."

if __name__ == "__main__":
    send_telegram("🔍 Bot avviato: controllo favorito < 1.70 da Sofascore")
    threading.Thread(target=check_favoriti_sofa, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
