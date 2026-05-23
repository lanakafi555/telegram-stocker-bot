import os

from flask import Flask
from threading import Thread

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


# ================= FLASK APP =================
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot jalan!"


# ================= COMMAND ID =================
async def get_id(update, context):

    await update.message.reply_text(
        f"ID: {update.effective_user.id}"
    )


# ================= COMMAND TOPIC =================
async def get_topic(update, context):

    thread_id = update.message.message_thread_id

    await update.message.reply_text(
        f"Topic ID: {thread_id}"
    )


# ================= ROUTER =================
async def router(update, context):

    thread_id = update.message.message_thread_id

    mode = TOPIC_MAP.get(thread_id)

    # ================= BELANJA =================
    if mode == "belanja":

        await handle_belanja(
            update,
            context
        )

    # ================= KEDATANGAN =================
    elif mode == "kedatangan":

        await handle_kedatangan(
            update,
            context
        )

    # ================= INVOICE =================
    elif mode == "invoice":

        await handle_invoice(
            update,
            context
        )

    # ================= TEST =================
    elif mode == "testing":

        await update.message.reply_text(
            "🧪 Testing mode"
        )


# ================= TELEGRAM APP =================
app = ApplicationBuilder().token(
    os.environ["BOT_TOKEN"]
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


# ================= RUN FLASK =================
def run_web():

    flask_app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )


Thread(
    target=run_web
).start()


# ================= RUN BOT =================
print("Bot jalan...")

app.run_polling()
