
import os
import random
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

INTERVAL = 3
MAX_MESSAGES = 100

logging.basicConfig(level=logging.INFO)

running = False
sent_count = 0
sender_task = None

OPENERS = [
    "Hey everyone",
    "Hello guys",
    "Just wondering",
    "Random thought",
    "By the way",
    "Honestly",
    "Quick question",
    "Well",
    "Interesting",
    "Not gonna lie"
]

MESSAGES = [
    "how is everyone doing today?",
    "what are you all up to?",
    "hope everyone is having a great day!",
    "any interesting plans for today?",
    "what's everyone thinking about?",
    "this group is pretty active!",
    "anyone got something interesting to share?",
    "hope everything is going well!",
    "what's happening everyone?",
    "anyone around right now?",
    "today feels like a good day!",
    "what's your favorite thing to do?",
    "let's have a good conversation!",
    "any interesting updates?",
    "how was your day?"
]


def admin_only(update):
    return (
        update.effective_user
        and update.effective_user.id == ADMIN_ID
    )


def random_message(previous):
    for _ in range(20):
        message = (
            random.choice(OPENERS)
            + ", "
            + random.choice(MESSAGES)
        )
        if message != previous:
            return message
    return random.choice(MESSAGES)


async def sender(context):
    global running, sent_count

    previous = ""

    try:
        while running and sent_count < MAX_MESSAGES:
            message = random_message(previous)
            previous = message

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=message
            )

            sent_count += 1
            await asyncio.sleep(INTERVAL)

    except asyncio.CancelledError:
        raise
    except Exception:
        logging.exception("Sending error")
    finally:
        running = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global running, sender_task, sent_count

    if not admin_only(update):
        return

    if running:
        await update.message.reply_text("Bot is already running.")
        return

    sent_count = 0
    running = True

    sender_task = asyncio.create_task(sender(context))

    await update.message.reply_text(
        "Random message bot started!\n"
        f"Interval: {INTERVAL} seconds\n"
        f"Message limit: {MAX_MESSAGES}"
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global running, sender_task

    if not admin_only(update):
        return

    running = False

    if sender_task and not sender_task.done():
        sender_task.cancel()

    await update.message.reply_text("Bot stopped!")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin_only(update):
        return

    await update.message.reply_text(
        f"Running: {running}\n"
        f"Messages sent: {sent_count}/{MAX_MESSAGES}\n"
        f"Interval: {INTERVAL}s"
    )


def main():
    if not BOT_TOKEN or not ADMIN_ID or not CHAT_ID:
        raise RuntimeError("Missing environment variables")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    app.run_polling()


if __name__ == "__main__":
    main()
