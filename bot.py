"""
Telegram VPS Test Bot (v3 - UNLIMITED auto-generate)
----------------------------------------------------
Fixed lists nahi, har baar NAYA content banta hai:
  * Live APIs se: jokes, quotes, facts, advice, number trivia, quiz (opentdb), photos
  * Khud generate: shayari, greetings, math quiz, emoji bursts
  * Telegram: dice animations, stickers, GIFs
Agar koi API fail ho to bot khud dusre type pe chala jata hai.

Commands (sirf ADMIN_ID):  /start_test  /stop_test  /status

Install:  pip install -r requirements.txt
Run:      python3 telegram_test_bot.py
"""

import html
import os
import random
import threading
import time
from datetime import datetime

import requests

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1001234567890"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

DELAY_MIN = 1.0
DELAY_MAX = 2.0

# Weight jitna zyada, utni baar aayega. 0 = band.
WEIGHTS = {
    # ---- QUIZZES (zyada) ----
    "quiz_api": 5,       # opentdb: alag-alag category (GK, science, movies, sports...)
    "quiz_trivia": 5,    # the-trivia-api: alag category/sawal
    "quiz_tf": 3,        # True/False quiz
    "quiz_math": 4,      # +, -, x, square, remainder
    "quiz_pattern": 3,   # series ka agla number
    "quiz_percent": 2,   # percentage
    "quiz_binary": 2,    # binary/hex <-> decimal
    "quiz_roman": 2,     # roman numerals
    "quiz_date": 3,      # kaunsa din tha / hoga
    "quiz_emoji": 2,     # emoji gino
    # ---- baaki (kam) ----
    "greeting": 1,
    "joke": 2,
    "shayari": 2,
    "quote": 1,
    "fact": 1,
    "advice": 1,
    "numfact": 1,
    "emoji": 1,
    "dice": 2,
    "sticker": 1,
    "gif": 1,
    "photo": 1,
}

STICKER_SETS = ["HotCherry", "Fred_the_Frog", "UtyaDuck"]
# ============================================

API = f"https://api.telegram.org/bot{BOT_TOKEN}"
HTTP = requests.Session()

_stickers = []
running = threading.Event()
sent_count = 0

# ---------------------------------------------------------------- helpers


def call(method, **params):
    try:
        r = HTTP.post(f"{API}/{method}", json=params, timeout=40)
        return r.json()
    except Exception as e:
        print("Telegram request error:", e)
        return {"ok": False}


def get_json(url, **kw):
    try:
        r = HTTP.get(url, timeout=10, **kw)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("API error:", url.split("/")[2], e)
    return None


def get_text(url):
    try:
        r = HTTP.get(url, timeout=10)
        if r.status_code == 200:
            return r.text.strip()
    except Exception as e:
        print("API error:", url.split("/")[2], e)
    return None


def say(text):
    return call("sendMessage", chat_id=GROUP_ID, text=text[:4000])


def handle_result(res):
    if res.get("ok"):
        return True
    retry = res.get("parameters", {}).get("retry_after")
    if retry:
        print(f"Rate limited, {retry}s wait...")
        time.sleep(retry + 1)
    else:
        print("Send failed:", res.get("description", res))
    return False


# ------------------------------------------------------- generated content

HELLOS = ["Hello", "Hi", "Hey", "Namaste", "Salaam", "Good morning", "Good evening",
          "Good night", "Bye bye", "Alvida", "Ram Ram", "Sat Sri Akal", "Hola", "Yo"]
PEOPLE = ["everyone", "dosto", "doston", "mere pyare group members", "sabko",
          "champions", "legends", "yaaron", "bhaiyon aur behno", "team"]
MOODS = ["Kaise ho?", "Sab badhiya?", "Chai pi li?", "Khana khaya?", "Aaj ka plan kya hai?",
         "Mast raho!", "Muskurate raho!", "Apna khayal rakhna!", "Din shaandar ho!",
         "Kya chal raha hai?", "Neend aa rahi hai kya?", "Coffee ya chai?"]
TAILS = ["VPS full speed me hai", "Server zinda hai", "Bot ekdum fit hai", "Test successful",
         "Uptime 100%", "Ping-pong chal raha hai", "Sab systems normal", "Koi lag nahi"]
EMOJIS = list("😀😃😄😁😆😅😂🤣😊😇🙂😉😍🥰😘😎🤩🥳🤗🤔😴🤯🔥💯✨🌟⭐🌈☀️🌙🌸🌹🍀🎉🎊🎈🎁🏆🚀💻📱⚡💙💚💛🧡❤️💜🖤🤝👍👏🙌💪🙏👋🍕🍔🍟🍩🍦☕🍵🐱🐶🦁🐯🐼🦄🐧")

# (rhyme endings) -> shayari lines
RHYMES = [
    ["aata hai", "jaata hai", "sataata hai", "mehkaata hai", "yaad dilaata hai"],
    ["raha", "kaha", "saha", "bahaa", "reh gaya"],
    ["hai", "nahi", "yahi", "kahi", "sahi"],
    ["dil", "manzil", "mushkil", "haasil", "shaamil"],
    ["mohabbat", "ibaadat", "shikayat", "sharaafat", "inayat"],
    ["chala", "mila", "khila", "hila", "jala"],
]
STARTS = [
    "Har raat tera khayal", "Chandni me tera zikr", "Dil ka har ek kona", "Sapno me tera naam",
    "Is zindagi ka safar", "Tere bina ye sama", "Subah ki pehli kiran", "Dosti ka ye rishta",
    "Meri khamoshi ka matlab", "Waqt ka har ek lamha", "Teri muskaan ka jaadu", "Barish ki har boond",
    "Hawaon ka ye jhonka", "Meri har dua ka asar", "Raaton ka ye sannata",
]
HEADS = ["✨", "🌹", "💙", "🔥", "🌙", "💌", "🥀", "☀️", "💫", "🌸"]


def gen_greeting():
    return (f"{random.choice(EMOJIS)} {random.choice(HELLOS)} {random.choice(PEOPLE)}! "
            f"{random.choice(MOODS)} {random.choice(EMOJIS)}\n"
            f"{random.choice(TAILS)} {random.choice(EMOJIS)}  "
            f"[{datetime.now().strftime('%H:%M:%S')}] #{random.randint(1000, 99999)}")


def gen_shayari():
    ends = random.choice(RHYMES)
    lines = [f"{random.choice(STARTS)} {e}," for e in random.sample(ends, 4)]
    lines[-1] = lines[-1][:-1] + "."
    return f"{random.choice(HEADS)} " + "\n".join(lines) + f" {random.choice(HEADS)}"


def gen_emoji_burst():
    return " ".join(random.choices(EMOJIS, k=random.randint(8, 20)))


def gen_math_quiz():
    kind = random.choice(["+", "-", "x", "sq", "mod"])
    if kind == "+":
        a, b = random.randint(10, 999), random.randint(10, 999)
        q, ans = f"{a} + {b} = ?", a + b
    elif kind == "-":
        a, b = random.randint(100, 999), random.randint(10, 99)
        q, ans = f"{a} - {b} = ?", a - b
    elif kind == "x":
        a, b = random.randint(3, 25), random.randint(3, 25)
        q, ans = f"{a} x {b} = ?", a * b
    elif kind == "sq":
        a = random.randint(5, 30)
        q, ans = f"{a} ka square kya hai?", a * a
    else:
        a, b = random.randint(20, 200), random.randint(3, 12)
        q, ans = f"{a} ko {b} se divide karne par remainder kya bachega?", a % b
    wrong = set()
    while len(wrong) < 3:
        w = ans + random.choice([-1, 1]) * random.randint(1, 12)
        if w != ans and w >= 0:
            wrong.add(w)
    opts = [str(x) for x in wrong] + [str(ans)]
    random.shuffle(opts)
    return "🧮 Math Quiz: " + q, opts, opts.index(str(ans)), f"Sahi jawab: {ans}"


# ---------------------------------------------------------------- senders


def send_greeting():
    return say(gen_greeting())


def send_shayari():
    return say(gen_shayari())


def send_emoji():
    return say(gen_emoji_burst())


def send_joke():
    d = get_json("https://v2.jokeapi.dev/joke/Any?lang=en"
                 "&blacklistFlags=nsfw,religious,political,racist,sexist,explicit")
    if d and not d.get("error"):
        if d.get("type") == "twopart":
            return say(f"😂 {d['setup']}\n\n👉 {d['delivery']}")
        if d.get("joke"):
            return say(f"🤣 {d['joke']}")
    return None


def send_quote():
    d = get_json("https://zenquotes.io/api/random")
    if d and isinstance(d, list) and d[0].get("q"):
        return say(f"💡 \"{d[0]['q']}\"\n— {d[0].get('a', 'Unknown')}")
    return None


def send_fact():
    d = get_json("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en")
    if d and d.get("text"):
        return say(f"🧐 Did you know?\n{d['text']}")
    return None


def send_advice():
    d = get_json("https://api.adviceslip.com/advice")
    if d and d.get("slip"):
        return say(f"🧠 Advice of the moment:\n{d['slip']['advice']}")
    return None


def send_numfact():
    t = get_text("http://numbersapi.com/random/trivia")
    if t:
        return say(f"🔢 {t}")
    return None


_last_call = {}


def throttled(name, gap):
    """Free API ki rate limit ke liye: gap seconds se pehle dobara call nahi."""
    now = time.time()
    if now - _last_call.get(name, 0) < gap:
        return False
    _last_call[name] = now
    return True


def poll(question, options, correct_idx, explanation):
    return call(
        "sendPoll", chat_id=GROUP_ID,
        question=question[:295],
        options=[str(o)[:99] for o in options],
        type="quiz", correct_option_id=correct_idx,
        explanation=explanation[:195], is_anonymous=True,
    )


def mc_poll(question, correct, wrongs, prefix="🎯 ", expl=None):
    opts = list(wrongs) + [correct]
    random.shuffle(opts)
    return poll(prefix + question, opts, opts.index(correct), expl or f"Sahi jawab: {correct}")


def near_numbers(ans, k=3, spread=12):
    """ans ke aas-paas ke galat options (distinct, non-negative)."""
    wrong = set()
    tries = 0
    while len(wrong) < k and tries < 100:
        tries += 1
        w = ans + random.choice([-1, 1]) * random.randint(1, spread)
        if w != ans and w >= 0:
            wrong.add(w)
    return list(wrong)


def send_quiz_api():
    # opentdb: random category + difficulty => har baar alag topic
    if not throttled("opentdb", 5.5):
        return None
    cat = random.randint(9, 32)
    diff = random.choice(["easy", "medium", "hard"])
    d = get_json(f"https://opentdb.com/api.php?amount=1&type=multiple&category={cat}&difficulty={diff}")
    if d and d.get("response_code") == 0 and d.get("results"):
        r = d["results"][0]
        correct = html.unescape(r["correct_answer"])
        wrongs = [html.unescape(x) for x in r["incorrect_answers"]]
        cname = html.unescape(r.get("category", "GK")).split(":")[-1].strip()
        return mc_poll(html.unescape(r["question"]), correct, wrongs, prefix=f"🎯 [{cname}] ")
    return None


def send_quiz_tf():
    if not throttled("opentdb", 5.5):
        return None
    d = get_json("https://opentdb.com/api.php?amount=1&type=boolean")
    if d and d.get("response_code") == 0 and d.get("results"):
        r = d["results"][0]
        ans = r["correct_answer"]
        return poll("✅❌ Sahi ya Galat? " + html.unescape(r["question"]),
                    ["True", "False"], 0 if ans == "True" else 1, f"Jawab: {ans}")
    return None


def send_quiz_trivia():
    d = get_json("https://the-trivia-api.com/v2/questions?limit=1")
    if d and isinstance(d, list) and d:
        r = d[0]
        cat = str(r.get("category", "GK")).replace("_", " ").title()
        return mc_poll(r["question"]["text"], r["correctAnswer"],
                       r["incorrectAnswers"][:3], prefix=f"🧠 [{cat}] ")
    return None


def send_quiz_pattern():
    kind = random.choice(["ap", "gp", "sq", "fib", "alt"])
    if kind == "ap":
        a, s = random.randint(1, 50), random.randint(2, 15)
        seq = [a + s * i for i in range(6)]
    elif kind == "gp":
        a, r = random.randint(1, 5), random.choice([2, 3])
        seq = [a * r ** i for i in range(6)]
    elif kind == "sq":
        o = random.randint(1, 8)
        seq = [(o + i) ** 2 for i in range(6)]
    elif kind == "fib":
        x, y = random.randint(1, 5), random.randint(1, 8)
        seq = [x, y]
        while len(seq) < 6:
            seq.append(seq[-1] + seq[-2])
    else:
        a, s1, s2 = random.randint(1, 20), random.randint(2, 9), random.randint(1, 5)
        seq = [a]
        for i in range(5):
            seq.append(seq[-1] + (s1 if i % 2 == 0 else s2))
    ans = seq[-1]
    shown = ", ".join(map(str, seq[:-1]))
    return mc_poll(f"Series me agla number kya hoga?\n{shown}, ?", ans, near_numbers(ans, spread=15),
                   prefix="🔢 ")


def send_quiz_percent():
    p = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
    n = random.choice(range(40, 1001, 20))
    ans = n * p // 100
    return mc_poll(f"{n} ka {p}% kitna hota hai?", ans, near_numbers(ans, spread=max(5, ans // 4)),
                   prefix="💯 ", expl=f"{n} x {p}/100 = {ans}")


def send_quiz_binary():
    n = random.randint(5, 255)
    mode = random.choice(["b2d", "d2b", "h2d"])
    if mode == "b2d":
        return mc_poll(f"Binary {bin(n)[2:]} ka decimal kya hoga?", n, near_numbers(n, spread=10),
                       prefix="💻 ", expl=f"{bin(n)[2:]} (binary) = {n}")
    if mode == "h2d":
        return mc_poll(f"Hex {hex(n)[2:].upper()} ka decimal kya hoga?", n, near_numbers(n, spread=10),
                       prefix="💻 ", expl=f"{hex(n)[2:].upper()} (hex) = {n}")
    correct = bin(n)[2:]
    wrongs = set()
    while len(wrongs) < 3:
        b = list(correct)
        i = random.randrange(len(b))
        b[i] = "1" if b[i] == "0" else "0"
        w = "".join(b).lstrip("0") or "0"
        if w != correct:
            wrongs.add(w)
    return mc_poll(f"Decimal {n} ka binary kya hoga?", correct, list(wrongs), prefix="💻 ",
                   expl=f"{n} = {correct} (binary)")


def to_roman(n):
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
            (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def send_quiz_roman():
    n = random.randint(4, 1999)
    return mc_poll(f"Roman number {to_roman(n)} ka matlab kya hai?", n,
                   near_numbers(n, spread=max(6, n // 20)), prefix="🏛 ",
                   expl=f"{to_roman(n)} = {n}")


def send_quiz_date():
    from datetime import date, timedelta
    start = date(2000, 1, 1)
    dt = start + timedelta(days=random.randint(0, 365 * 45))
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    correct = days[dt.weekday()]
    wrongs = random.sample([x for x in days if x != correct], 3)
    return mc_poll(f"{dt.strftime('%d %B %Y')} ko kaunsa din tha/hoga?", correct, wrongs,
                   prefix="📅 ")


def send_quiz_emoji():
    pool = random.sample(EMOJIS, 3)
    target = pool[0]
    seq = [random.choice(pool) for _ in range(random.randint(12, 22))]
    if target not in seq:
        seq[0] = target
    cnt = seq.count(target)
    return mc_poll(f"Is line me {target} kitni baar hai?\n{' '.join(seq)}", cnt,
                   near_numbers(cnt, spread=4), prefix="👀 ")


def send_quiz_math():
    q, opts, correct, expl = gen_math_quiz()
    return call("sendPoll", chat_id=GROUP_ID, question=q, options=opts, type="quiz",
                correct_option_id=correct, explanation=expl, is_anonymous=True)


def send_dice():
    return call("sendDice", chat_id=GROUP_ID, emoji=random.choice(["🎲", "🎯", "🏀", "⚽", "🎳", "🎰"]))


def send_sticker():
    if not _stickers:
        return None
    return call("sendSticker", chat_id=GROUP_ID, sticker=random.choice(_stickers))


def send_gif():
    # cataas har baar random cat GIF deta hai; ?t= se cache bypass
    return call("sendAnimation", chat_id=GROUP_ID,
                animation=f"https://cataas.com/cat/gif?t={random.randint(1, 10**9)}")


def send_photo():
    if random.random() < 0.5:
        d = get_json("https://dog.ceo/api/breeds/image/random")
        url = d.get("message") if d else None
    else:
        url = f"https://cataas.com/cat?t={random.randint(1, 10**9)}"
    if url:
        return call("sendPhoto", chat_id=GROUP_ID, photo=url)
    return None


SENDERS = {
    "greeting": send_greeting, "joke": send_joke, "shayari": send_shayari,
    "quote": send_quote, "fact": send_fact, "advice": send_advice,
    "numfact": send_numfact, "quiz_api": send_quiz_api, "quiz_math": send_quiz_math,
    "quiz_trivia": send_quiz_trivia, "quiz_tf": send_quiz_tf, "quiz_pattern": send_quiz_pattern,
    "quiz_percent": send_quiz_percent, "quiz_binary": send_quiz_binary,
    "quiz_roman": send_quiz_roman, "quiz_date": send_quiz_date, "quiz_emoji": send_quiz_emoji,
    "emoji": send_emoji, "dice": send_dice, "sticker": send_sticker,
    "gif": send_gif, "photo": send_photo,
}

# API fail ho to ye (khud generate hone wale) quizzes chalenge
QUIZ_FALLBACKS = [send_quiz_math, send_quiz_pattern, send_quiz_percent, send_quiz_binary,
                  send_quiz_roman, send_quiz_date, send_quiz_emoji]


def make_message():
    kinds = [k for k, w in WEIGHTS.items() if w > 0]
    kind = random.choices(kinds, weights=[WEIGHTS[k] for k in kinds])[0]
    res = SENDERS[kind]()
    # API/sticker fail ho gaya ya Telegram ne reject kiya -> procedural fallback
    if res is None or not res.get("ok"):
        if res is not None and res.get("parameters", {}).get("retry_after"):
            return res
        res = random.choice(QUIZ_FALLBACKS)()
    return res


# ------------------------------------------------------------------ engine


def load_stickers():
    for name in STICKER_SETS:
        res = call("getStickerSet", name=name)
        if res.get("ok"):
            ids = [s["file_id"] for s in res["result"]["stickers"]]
            _stickers.extend(ids)
            print(f"Sticker set '{name}' loaded ({len(ids)})")
        else:
            print(f"Sticker set '{name}' nahi mila, skip.")


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
    if not msg or msg.get("from", {}).get("id") != ADMIN_ID:
        return
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip().lower()

    def reply(t):
        call("sendMessage", chat_id=chat_id, text=t)

    if text.startswith("/start_test"):
        running.set()
        reply("✅ Test shuru. Unlimited content group me jaa raha hai.")
    elif text.startswith("/stop_test"):
        running.clear()
        reply(f"⏹ Test band. Total sent: {sent_count}")
    elif text.startswith("/status"):
        state = "RUNNING" if running.is_set() else "STOPPED"
        reply(f"Status: {state}\nSent: {sent_count}\nDelay: {DELAY_MIN}-{DELAY_MAX}s")
    elif text.startswith("/start"):
        reply("Commands:\n/start_test - shuru\n/stop_test - band\n/status - status")


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
