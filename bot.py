import json

from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters
)

from config import TOPIC_MAP
from handlers.belanja import handle_belanja
from handlers.kedatangan import handle_kedatangan
from handlers.invoice import handle_invoice


# ================= LOAD CONFIG =================

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]


# ================= COMMANDS =================

async def get_id(update, context):
    await update.message.reply_text(
        f"ID: {update.effective_user.id}"
    )


async def get_topic(update, context):
    thread_id = update.message.message_thread_id

    await update.message.reply_text(
        f"Topic ID: {thread_id}"
    )


# ================= ROUTER =================

async def router(update, context):

    thread_id = update.message.message_thread_id

    mode = TOPIC_MAP.get(thread_id)

    if mode == "belanja":

        await handle_belanja(
            update,
            context
        )

    elif mode == "kedatangan":

        await handle_kedatangan(
            update,
            context
        )

    elif mode == "invoice":

        await handle_invoice(
            update,
            context
        )

    elif mode == "testing":

        await update.message.reply_text(
            "🧪 Testing mode"
        )


# ================= APP =================

app = ApplicationBuilder().token(
    BOT_TOKEN
).build()


# ================= HANDLERS =================

app.add_handler(
    CommandHandler(
        "id",
        get_id
    )
)

app.add_handler(
    CommandHandler(
        "topic",
        get_topic
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        router
    )
)


# ================= START =================

print("Bot jalan...")

app.run_polling()
