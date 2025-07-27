
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

# === CONFIG ===
BOT_TOKEN = "7603257716:AAHYHZF8H6S-LyuXp8l-h1W0h40fSPp3WZU"
CHAT_ID = "66336138"
CHECK_INTERVAL = 120  # in secondi
QUOTE_LIMIT = 1.70
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
URL = "https://www.diretta.it/tennis/"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print(f"[Errore Telegram] {e}")

def check_favoriti():
    try:
        print("[*] Controllo match con quota < 1.70...")
        res = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        msg_lines = []

        for event in soup.select(".event__match--live"):
            try:
                torneo = event.find_previous("div", class_="event__header").text.strip()
                if not ("ATP" in torneo or "WTA" in torneo):
                    continue

                players = event.select(".event__participant")
                odds = event.select(".event__odd")

                if len(players) != 2 or len(odds) != 2:
                    continue

                p1 = players[0].text.strip()
                p2 = players[1].text.strip()
                o1 = float(odds[0].text.strip())
                o2 = float(odds[1].text.strip())

                if o1 < QUOTE_LIMIT or o2 < QUOTE_LIMIT:
                    msg_lines.append(f"🎾 {torneo}: {p1} ({o1}) vs {p2} ({o2})")
            except:
                continue

        if msg_lines:
            full_msg = "📋 Match con favorito < 1.70: " + "\n".join(msg_lines)
            send_telegram(full_msg)
            print("[+] Notifica inviata")
        else:
            print("[!] Nessun match trovato con favorito < 1.70")

    except Exception as e:
        print(f"[Errore parsing] {e}")

@app.route("/")
def home():
    return "Bot test attivo."

if __name__ == "__main__":
    send_telegram("🔍 Test: ricerca favoriti < 1.70 avviata.")
    threading.Thread(target=check_favoriti, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
