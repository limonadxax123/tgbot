import os
import telebot
from flask import Flask, request
from openai import OpenAI

# Берём токены из Environment Variables
TG_TOKEN = os.getenv("TG_TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

if not TG_TOKEN or not OPENAI_TOKEN:
    raise ValueError("❌ TG_TOKEN или OPENAI_TOKEN не установлены в Environment Variables")

bot = telebot.TeleBot(TG_TOKEN)
client = OpenAI(api_key=OPENAI_TOKEN)

app = Flask(__name__)

# Хранилище истории пользователей
user_histories = {}
MAX_HISTORY = 20


@app.route(f"/{TG_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def index():
    return "Bot is running"


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text

    # Игнорируем не текстовые сообщения
    if not user_text:
        return

    # Если пользователя ещё нет в истории
    if user_id not in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": "Ты дружелюбный ИИ как character.ai"}
        ]

    # Добавляем сообщение пользователя
    user_histories[user_id].append(
        {"role": "user", "content": user_text}
    )

    # Ограничиваем память
    if len(user_histories[user_id]) > MAX_HISTORY:
        user_histories[user_id] = user_histories[user_id][-MAX_HISTORY:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_histories[user_id]
        )

        answer = response.choices[0].message.content

        # Сохраняем ответ бота
        user_histories[user_id].append(
            {"role": "assistant", "content": answer}
        )

        bot.reply_to(message, answer)

    except Exception as e:
        print("OpenAI error:", e)
        bot.reply_to(message, "Произошла ошибка 😔 Попробуй позже.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

