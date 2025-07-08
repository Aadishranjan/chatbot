# --- Flask server for uptime ping (Render/Heroku) ---
from flask import Flask
import threading
import os

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Setup ---
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, USER1_ID, USER2_ID
from personalities import user1, user2

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text

    if user_id == USER1_ID:
        prompt = user1.format_prompt(message_text)
    elif user_id == USER2_ID:
        prompt = user2.format_prompt(message_text)
    else:
        await update.message.reply_text("Sorry, this bot is for two specific users only.")
        return

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Error from Gemini: {e}")

# Run Telegram bot
def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Telegram bot is running...")
    app.run_polling()

# --- Combined Runner ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
