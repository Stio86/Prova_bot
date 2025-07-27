
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
        print("[*] Controllo match con quota < 1.70 (nuovo HTML)...")
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

                quote_elements = match.select('[data-testid="wcl-oddsValue"]')
                if len(quote_elements) < 2:
                    continue

                o1 = float(quote_elements[0].text.strip())
                o2 = float(quote_elements[1].text.strip())

                if o1 < QUOTE_LIMIT or o2 < QUOTE_LIMIT:
                    msg_lines.append(f"🎾 {torneo}: {p1} ({o1}) vs {p2} ({o2})")
            except Exception as e:
                print(f"[!] Errore match: {e}")
                continue

        if msg_lines:
            full_msg = "📋 Match con favorito < 1.70:
" + "\n".join(msg_lines)
            send_telegram(full_msg)
            print("[+] Notifica inviata")
        else:
            print("[!] Nessun match con quota < 1.70 trovato")

    except Exception as e:
        print(f"[Errore parsing] {e}")

@app.route("/")
def home():
    return "Bot attivo con struttura HTML aggiornata."

if __name__ == "__main__":
    send_telegram("🔍 Bot avviato (HTML nuovo): ricerca favoriti < 1.70")
    threading.Thread(target=check_favoriti, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
