import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.helpers import escape_markdown

# Load token from .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Local API endpoint (no SSL)
API_URL = os.getenv("API_URL", "http://api:8000/query")
# API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/query")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! Send me a Git/GitHub-related question and I’ll try to help."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.message.from_user.id
    print(f"🔹 [DEBUG] Sending user_id to API: {user_id}")
    try:
        response = requests.post(
            API_URL, json={"question": user_input, "top_k": 1, "user_id": str(user_id)}
        )
        data = response.json()

        if data.get("results"):
            top = data["results"][0]
            safe_answer = escape_markdown(top["answer"], version=2)
            message = f"✅ *Question*: {escape_markdown(top['question'], version=2)}\n\n🧠 *Answer*: {safe_answer}"
        else:
            message = "❌ Sorry, I couldn’t find a good answer."
    except Exception as e:
        message = f"⚠️ Error: {e}"

    await update.message.reply_text(message, parse_mode="MarkdownV2")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
