
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

# === CONFIG ===
BOT_TOKEN = "7603257716:AAHYHZF8H6S-LyuXp8l-h1W0h40fSPp3WZU"
CHAT_ID = "66336138"
CHECK_INTERVAL = 60  # in secondi

# === FUNZIONE NOTIFICA ===
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print(f"[Errore Telegram] {e}")

# === FUNZIONE DI CONTROLLO ===
def check_matches():
    while True:
        try:
            print("[*] Controllo in corso...")
            # Qui andrebbe il parsing da Diretta.it
            # Per ora simuliamo un controllo
            time.sleep(3)
            print("[*] Nessun match rilevante al momento.")
        except Exception as e:
            print(f"[Errore controllo] {e}")
        time.sleep(CHECK_INTERVAL)

# === AVVIO THREAD IN BACKGROUND ===
def start_background_task():
    try:
        send_telegram("✅ Bot fav-sotto-set attivo!")
        thread = threading.Thread(target=check_matches)
        thread.daemon = True
        thread.start()
        print("[+] Thread di controllo avviato.")
    except Exception as e:
        print(f"[Errore avvio thread] {e}")

# === ROUTE PRINCIPALE ===
@app.route("/")
def home():
    return "Bot attivo."

# === AVVIO ===
if __name__ == "__main__":
    start_background_task()
    app.run(host="0.0.0.0", port=10000)
