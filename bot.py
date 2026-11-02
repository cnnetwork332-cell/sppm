"""
Telegram VPS Test Bot
---------------------
- Group me random messages bhejta rehta hai (jab tak aap stop na karo)
- Sirf ADMIN_ID wala user control kar sakta hai
- Telegram ki rate limit (429) automatically handle karta hai

Install:   pip install requests
Run:       python3 telegram_test_bot.py
Background: nohup python3 telegram_test_bot.py &
"""

import random
import threading
import time

import requests

# ================== CONFIG (yahan apni values daalo) ==================
BOT_TOKEN = "8501734917:AAEv-j5tJ795G9aDAZksIvCBQVZ4I_wxgzw"        # @BotFather se mila token
GROUP_ID = -1002381061691           # group ka chat id (negative number)
ADMIN_ID = 7271198694               # aapka Telegram user id
DELAY_SECONDS = 3                   # 2 messages ke beech gap (kam se kam 3 rakho)
# =====================================================================

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

MESSAGES = [
    "hi", "hello", "bye", "test", "hey", "good morning", "good night",
    "kaise ho?", "all ok?", "ping", "pong", "VPS test running",
    "random message", "testing 123", "hello world", "👋", "✅", "🚀",
]

running = threading.Event()
sent_count = 0


def call(method, **params):
    try:
        r = requests.post(f"{API}/{method}", json=params, timeout=40)
        return r.json()
    except Exception as e:
        print("Request error:", e)
        return {"ok": False}


def send(chat_id, text):
    res = call("sendMessage", chat_id=chat_id, text=text)
    if not res.get("ok"):
        # Telegram flood limit: jitna bola utna ruko
        retry = res.get("parameters", {}).get("retry_after")
        if retry:
            print(f"Rate limited, {retry}s wait...")
            time.sleep(retry + 1)
        else:
            print("Send failed:", res)
    return res


def sender_loop():
    global sent_count
    while True:
        running.wait()  # /start_test tak yahin ruka rahega
        msg = f"{random.choice(MESSAGES)} #{random.randint(1000, 9999)}"
        res = send(GROUP_ID, msg)
        if res.get("ok"):
            sent_count += 1
            print(f"[{sent_count}] sent: {msg}")
        time.sleep(DELAY_SECONDS)


def handle_update(update):
    msg = update.get("message")
    if not msg:
        return
    user_id = msg.get("from", {}).get("id")
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip().lower()

    if user_id != ADMIN_ID:
        return  # sirf admin ki command chalegi

    if text.startswith("/start_test"):
        running.set()
        send(chat_id, "✅ Test shuru. Group me messages jaa rahe hain.")
    elif text.startswith("/stop_test"):
        running.clear()
        send(chat_id, f"⏹ Test band. Total sent: {sent_count}")
    elif text.startswith("/status"):
        state = "RUNNING" if running.is_set() else "STOPPED"
        send(chat_id, f"Status: {state}\nSent: {sent_count}\nDelay: {DELAY_SECONDS}s")
    elif text.startswith("/start"):
        send(chat_id, "Commands:\n/start_test - shuru\n/stop_test - band\n/status - status")


def main():
    me = call("getMe")
    if not me.get("ok"):
        print("Bot token galat hai ya network issue:", me)
        return
    print("Bot chalu:", me["result"]["username"])

    threading.Thread(target=sender_loop, daemon=True).start()

    offset = None
    while True:
        res = call("getUpdates", offset=offset, timeout=30)
        for upd in res.get("result", []):
            offset = upd["update_id"] + 1
            handle_update(upd)


if __name__ == "__main__":
    main()
