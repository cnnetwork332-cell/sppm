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


"""
Telegram VPS Test Bot (v2)
--------------------------
Group me random content bhejta hai: text, jokes, shayari, quotes, quiz polls,
dice/emoji animations, stickers aur GIFs. Delay 1-2 sec random.

Commands (sirf ADMIN_ID):
  /start_test   - shuru
  /stop_test    - band
  /status       - status

Install:  pip install -r requirements.txt
Run:      python3 telegram_test_bot.py
"""

DELAY_MIN = 1.0   # seconds
DELAY_MAX = 2.0   # seconds

# Kis type ka message kitni baar aaye (weight jitna zyada, utna zyada)
WEIGHTS = {
    "text": 3,
    "joke": 3,
    "shayari": 3,
    "quote": 2,
    "fact": 2,
    "quiz": 2,
    "dice": 2,
    "sticker": 2,
    "gif": 1,
}

# Telegram ke public sticker packs (short name). Galat ho to skip ho jayega.
STICKER_SETS = ["HotCherry", "Fred_the_Frog", "UtyaDuck"]

# GIF direct links (.gif / .mp4). Aap apne links daal sakte ho.
GIF_URLS = [
    "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif",
    "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",
]
# ============================================

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

GREETINGS = [
    "Hello everyone! 👋 Kaise ho sab?",
    "Hi hi hi! 😄 Aaj ka din mast jaye aapka.",
    "Good morning ☀️ Chai pi li ya nahi?",
    "Good night 🌙 Ab so jao, kal phir milte hain.",
    "Bye bye! 👋 Phir milenge, apna khayal rakhna 💙",
    "Test message ✅ VPS bilkul sahi chal raha hai 🚀",
    "Ping! 🏓 ... Pong! Server zinda hai 💪",
    "Hey! 😎 Kya chal raha hai aajkal?",
    "Namaste 🙏 Sabko mera pranam!",
    "Sab badhiya? 🔥 Bot full speed me hai!",
]

JOKES = [
    "😂 Teacher: Tum late kyun aaye?\nStudent: Sir, board pe likha tha 'School ahead, go slow'!",
    "🤣 Patni: Main mar gayi to tum kya karoge?\nPati: Pagal ho jaunga.\nPatni: Aur doosri shaadi?\nPati: Pagal aadmi ko kaun ladki dega?",
    "😆 Doctor: Aapko aaram ki zarurat hai.\nMareez: Wahi to chahiye, par boss maanta nahi!",
    "😜 Bhikari: Bhagwan ke naam pe kuch de do.\nAadmi: Bhagwan ka naam to free hai, tum bhi free me lo!",
    "🤪 Bete ne bola: Papa, main exam me fail ho gaya.\nPapa: Koi baat nahi beta, next time bhi yahi score aayega, bharosa rakho!",
    "😅 WiFi password poochha to dost ne bola: 'Pehle bata, tu mera dost hai ya data ka dushman?'",
    "🤭 Programmer ki biwi: Bazaar se ek dahi laana, agar ande mile to 6 le aana.\nProgrammer 6 dahi le aaya. Kyunki ande mil gaye the!",
    "😂 Alarm ne subah 6 baje kaha: Uth ja.\nMaine kaha: Tu pehle bata, kal raat tune mujhe kyun nahi uthaya movie dekhte time?",
]

SHAYARI = [
    "✨ Dil ki baat labon pe aati nahi,\nYaad teri dil se jaati nahi,\nKaash tu bhi samajh paata humein,\nKi neend bhi ab raaton ko aati nahi. 🌙",
    "🌹 Chand ko dekha to teri yaad aayi,\nTaaron ne bhi teri hi baat sunayi,\nHum to bas muskura kar chup rahe,\nKhamoshi ne sari kahani kehkar sunayi. 💫",
    "💙 Zindagi ek safar hai suhana,\nHar mod pe naya hai fasana,\nJo mile unhe dil se apna lena,\nYahi hai khushiyon ka khazana. 🌈",
    "🔥 Himmat-e-marda to madad-e-khuda,\nMushkilein aayengi, par rukna nahi,\nJo girkar uthta hai har baar yahan,\nWahi manzil ko paata hai, jhukna nahi. 💪",
    "🌙 Raat ka sannata kuch keh gaya,\nAankhon me ek sapna reh gaya,\nSubah ki roshni jab aayegi,\nHar gham pal me beh gaya. ☀️",
    "💌 Dosti ka rishta sabse pyara hota hai,\nDil se dil ka nata nyara hota hai,\nChahe kitni bhi ho doori humare darmiyan,\nYaad karna, dost sahara hota hai. 🤝",
]

QUOTES = [
    "💡 \"Sapne wo nahi jo hum neend me dekhte hain, sapne wo hain jo hume neend nahi aane dete.\" — A.P.J. Abdul Kalam",
    "🌟 \"Mehnat itni khamoshi se karo ki safalta shor macha de.\"",
    "🚀 \"Chhoti shuruaat bhi badi manzil tak le jaati hai. Bas chalte raho.\"",
    "🧠 \"Seekhna kabhi band mat karo, kyunki zindagi kabhi sikhana band nahi karti.\"",
    "🔥 \"Haar tab hoti hai jab aap koshish karna chhod dete ho.\"",
    "🌈 \"Aaj ka din dobara nahi aayega, isliye ise khubsurat banao.\"",
    "⏰ \"Waqt aur lehron ka intezaar koi nahi karta. Aaj hi shuru karo.\"",
]

FACTS = [
    "🧐 Kya aap jaante ho? Shahad kabhi kharab nahi hota. Mishr ke maqbaron me 3000 saal purana shahad bhi khane layak mila!",
    "🐙 Octopus ke 3 dil hote hain aur uska khoon neela hota hai.",
    "🌍 Dharti par rozana lagbhag 80 lakh bijli ki chamak (lightning) girti hain.",
    "🧠 Insaani dimaag me lagbhag 86 billion neurons hote hain.",
    "🐘 Haathi akela aisa janwar hai jo kood nahi sakta.",
    "☀️ Surya ki roshni dharti tak aane me lagbhag 8 minute 20 second leti hai.",
    "🍌 Kela technically ek berry hai, lekin strawberry nahi!",
    "🐝 Ek madhumakkhi apni poori zindagi me sirf 1/12 chammach shahad banati hai.",
]

# (sawal, [options], sahi_option_index, explanation)
QUIZZES = [
    ("🇮🇳 Bharat ki rajdhani kaunsi hai?", ["Mumbai", "New Delhi", "Kolkata", "Chennai"], 1, "New Delhi Bharat ki rajdhani hai."),
    ("🌍 Sabse bada mahasagar kaunsa hai?", ["Atlantic", "Hind", "Prashant (Pacific)", "Arctic"], 2, "Pacific Ocean sabse bada hai."),
    ("🧪 Paani ka chemical formula kya hai?", ["CO2", "H2O", "O2", "NaCl"], 1, "Paani = H2O (2 hydrogen + 1 oxygen)."),
    ("🪐 Lal grah (Red Planet) kise kehte hain?", ["Venus", "Jupiter", "Mars", "Saturn"], 2, "Mars par iron oxide hone se wo laal dikhta hai."),
    ("💻 HTML ka full form kya hai?", ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyper Transfer Mark Language"], 0, "HTML = HyperText Markup Language."),
    ("🏏 Cricket team me kitne khiladi khelte hain?", ["9", "10", "11", "12"], 2, "Ek team me 11 khiladi hote hain."),
    ("📱 Telegram ke founder kaun hain?", ["Pavel Durov", "Elon Musk", "Mark Zuckerberg", "Jack Dorsey"], 0, "Telegram ko Pavel Durov ne banaya."),
    ("🐅 Bharat ka rashtriya pashu kaunsa hai?", ["Sher", "Bagh (Tiger)", "Haathi", "Tendua"], 1, "Royal Bengal Tiger rashtriya pashu hai."),
    ("🐧 Linux ka mascot kaunsa janwar hai?", ["Lomdi", "Panda", "Penguin", "Cheel"], 2, "Linux ka mascot 'Tux' naam ka penguin hai."),
    ("🔢 Python me list ka pehla index kya hota hai?", ["1", "0", "-1", "2"], 1, "Python me indexing 0 se shuru hoti hai."),
]

DICE_EMOJIS = ["🎲", "🎯", "🏀", "⚽", "🎳", "🎰"]

_stickers = []
running = threading.Event()
sent_count = 0


def call(method, **params):
    try:
        r = requests.post(f"{API}/{method}", json=params, timeout=40)
        return r.json()
    except Exception as e:
        print("Request error:", e)
        return {"ok": False}


def handle_result(res):
    """429 aaye to retry_after tak ruko."""
    if res.get("ok"):
        return True
    retry = res.get("parameters", {}).get("retry_after")
    if retry:
        print(f"Rate limited, {retry}s wait...")
        time.sleep(retry + 1)
    else:
        print("Send failed:", res.get("description", res))
    return False


def send_text(chat_id, text):
    return call("sendMessage", chat_id=chat_id, text=text)


def load_stickers():
    for name in STICKER_SETS:
        res = call("getStickerSet", name=name)
        if res.get("ok"):
            ids = [s["file_id"] for s in res["result"]["stickers"]]
            _stickers.extend(ids)
            print(f"Sticker set '{name}' loaded ({len(ids)})")
        else:
            print(f"Sticker set '{name}' nahi mila, skip.")


def make_message():
    kind = random.choices(list(WEIGHTS), weights=list(WEIGHTS.values()))[0]

    if kind == "text":
        return call("sendMessage", chat_id=GROUP_ID, text=random.choice(GREETINGS))
    if kind == "joke":
        return call("sendMessage", chat_id=GROUP_ID, text=random.choice(JOKES))
    if kind == "shayari":
        return call("sendMessage", chat_id=GROUP_ID, text=random.choice(SHAYARI))
    if kind == "quote":
        return call("sendMessage", chat_id=GROUP_ID, text=random.choice(QUOTES))
    if kind == "fact":
        return call("sendMessage", chat_id=GROUP_ID, text=random.choice(FACTS))
    if kind == "quiz":
        q, opts, correct, expl = random.choice(QUIZZES)
        return call(
            "sendPoll",
            chat_id=GROUP_ID,
            question=q,
            options=opts,
            type="quiz",
            correct_option_id=correct,
            explanation=expl,
            is_anonymous=True,
        )
    if kind == "dice":
        return call("sendDice", chat_id=GROUP_ID, emoji=random.choice(DICE_EMOJIS))
    if kind == "sticker" and _stickers:
        return call("sendSticker", chat_id=GROUP_ID, sticker=random.choice(_stickers))
    if kind == "gif" and GIF_URLS:
        return call("sendAnimation", chat_id=GROUP_ID, animation=random.choice(GIF_URLS))

    # fallback
    return call("sendMessage", chat_id=GROUP_ID, text=random.choice(GREETINGS))


def sender_loop():
    global sent_count
    while True:
        running.wait()
        res = make_message()
        if handle_result(res):
            sent_count += 1
            print(f"[{sent_count}] sent")
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def handle_update(update):
    msg = update.get("message")
    if not msg:
        return
    if msg.get("from", {}).get("id") != ADMIN_ID:
        return
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip().lower()

    if text.startswith("/start_test"):
        running.set()
        send_text(chat_id, "✅ Test shuru. Group me content jaa raha hai.")
    elif text.startswith("/stop_test"):
        running.clear()
        send_text(chat_id, f"⏹ Test band. Total sent: {sent_count}")
    elif text.startswith("/status"):
        state = "RUNNING" if running.is_set() else "STOPPED"
        send_text(chat_id, f"Status: {state}\nSent: {sent_count}\nDelay: {DELAY_MIN}-{DELAY_MAX}s")
    elif text.startswith("/start"):
        send_text(chat_id, "Commands:\n/start_test - shuru\n/stop_test - band\n/status - status")


def main():
    me = call("getMe")
    if not me.get("ok"):
        print("Bot token galat hai ya network issue:", me)
        return
    print("Bot chalu:", me["result"]["username"])

    load_stickers()
    threading.Thread(target=sender_loop, daemon=True).start()

    offset = None
    while True:
        res = call("getUpdates", offset=offset, timeout=30)
        for upd in res.get("result", []):
            offset = upd["update_id"] + 1
            handle_update(upd)


if __name__ == "__main__":
    main()
