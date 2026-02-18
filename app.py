import os
from flask import Flask, request
import telebot
from openai import OpenAI

# ====== ТОКЕНЫ ИЗ ENVIRONMENT ======
TG_TOKEN = os.getenv("TG_TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

# ====== ИНИЦИАЛИЗАЦИЯ ======
bot = telebot.TeleBot(TG_TOKEN)
client = OpenAI(api_key=OPENAI_TOKEN)

app = Flask(__name__)

# ====== ГЛАВНАЯ СТРАНИЦА ======
@app.route("/")
def index():
    return "Bot is running"

# ====== WEBHOOK ОТ TELEGRAM ======
@app.route(f"/{TG_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# ====== УСТАНОВКА WEBHOOK ======
@app.route("/set_webhook")
def set_webhook():
    bot.remove_webhook()
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TG_TOKEN}"
    bot.set_webhook(url=url)
    return f"Webhook set to {url}"

# ====== ОБРАБОТКА /start ======
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(message, "Привет 👋 Напиши что-нибудь!")

# ====== ОБРАБОТКА ВСЕХ СООБЩЕНИЙ ======
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": message.text}
            ]
        )

        answer = response.choices[0].message.content
        bot.reply_to(message, answer)

    except Exception as e:
        print("OpenAI error:", e)
        bot.reply_to(message, "Ошибка 😔 Попробуй позже.")

# ====== ЗАПУСК ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

