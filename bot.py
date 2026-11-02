
import os
import random
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

INTERVAL = max(30, int(os.getenv("INTERVAL", "30")))
MAX_MESSAGES = 100

# ==========================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

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
    "Not gonna lie",
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
    "how was your day?",
]


def is_admin(update: Update) -> bool:
    return (
        update.effective_user is not None
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


async def sender(context: ContextTypes.DEFAULT_TYPE):
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

            logger.info(
                "Message sent: %s/%s",
                sent_count,
                MAX_MESSAGES
            )

            await asyncio.sleep(INTERVAL)

    except asyncio.CancelledError:
        logger.info("Sender cancelled")
        raise

    except Exception:
        logger.exception("Message sending failed")

    finally:
        running = False


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    global running, sender_task, sent_count

    if not is_admin(update):
        return

    if running:
        await update.message.reply_text(
            "Bot is already running!"
        )
        return

    sent_count = 0
    running = True

    sender_task = asyncio.create_task(
        sender(context)
    )

    await update.message.reply_text(
        "Random message bot started!\n\n"
        f"Interval: {INTERVAL} seconds\n"
        f"Maximum messages: {MAX_MESSAGES}"
    )


async def stop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    global running, sender_task

    if not is_admin(update):
        return

    running = False

    if sender_task and not sender_task.done():
        sender_task.cancel()

    await update.message.reply_text(
        "Bot stopped successfully!"
    )


async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not is_admin(update):
        return

    await update.message.reply_text(
        f"Bot status: {'Running' if running else 'Stopped'}\n"
        f"Messages sent: {sent_count}/{MAX_MESSAGES}\n"
        f"Interval: {INTERVAL} seconds"
    )


def main():

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing")

    if not ADMIN_ID or not CHAT_ID:
        raise RuntimeError("ADMIN_ID or CHAT_ID missing")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("status", status))

    logger.info("Telegram bot starting...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        app.run_polling()
    finally:
        loop.close()


if __name__ == "__main__":
    main()
