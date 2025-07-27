
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = "7603257716:AAHYHZF8H6S-LyuXp8l-h1W0h40fSPp3WZU"
CHAT_ID = "66336138"
CHECK_INTERVAL = 120
QUOTE_LIMIT = 1.70
URL = "https://www.diretta.it/tennis/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

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

        for match in soup.select("div.event__match--live"):
            try:
                torneo = match.find_previous("div", class_="event__header").text.strip()
                if not ("ATP" in torneo or "WTA" in torneo):
                    continue

                p1 = match.select_one(".event__participant--home").text.strip()
                p2 = match.select_one(".event__participant--away").text.strip()
                odd1 = match.get("data-odd1")
                odd2 = match.get("data-odd2")

                if odd1 is None or odd2 is None:
                    continue

                o1 = float(odd1)
                o2 = float(odd2)

                if o1 < QUOTE_LIMIT or o2 < QUOTE_LIMIT:
                    msg_lines.append(f"🎾 {torneo}: {p1} ({o1}) vs {p2} ({o2})")
            except Exception as e:
                print(f"[!] Errore match: {e}")
                continue

        if msg_lines:
            full_msg = "📋 Match con favorito < 1.70: " + "\n".join(msg_lines)
            send_telegram(full_msg)
            print("[+] Notifica inviata")
        else:
            print("[!] Nessun match con quota < 1.70 trovato")

    except Exception as e:
        print(f"[Errore parsing] {e}")

@app.route("/")
def home():
    return "Bot aggiornato attivo."

if __name__ == "__main__":
    send_telegram("🔍 Bot avviato: ricerca favoriti < 1.70 (data-odd)")
    threading.Thread(target=check_favoriti, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
