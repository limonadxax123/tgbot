import os
import telebot
from flask import Flask, request
from openai import OpenAI

# Токены (лучше хранить в Environment Variables на Render)
TG_TOKEN = os.getenv("8560116253:AAEfLxYZAL2AK-e--atv9z0lq2Vpv1QUpqw")
OPENAI_TOKEN = os.getenv("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")

bot = telebot.TeleBot(TG_TOKEN)
user_histories = {}
client = OpenAI(api_key=OPENAI_TOKEN)

app = Flask(__name__)

@app.route(f"/{TG_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running"

MAX_HISTORY = 20  # можно написать вверху файла

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_text = message.text

    if user_id not in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": "Ты дружелюбный ИИ как character.ai"}
        ]

    # Добавляем сообщение пользователя
    user_histories[user_id].append(
        {"role": "user", "content": user_text}
    )

    # 🔥 ВОТ СЮДА вставлять ограничение памяти
    if len(user_histories[user_id]) > MAX_HISTORY:
        user_histories[user_id] = user_histories[user_id][-MAX_HISTORY:]

    # Теперь отправляем в OpenAI
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


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты дружелюбный ИИ как character.ai"},
            {"role": "user", "content": user_text}
        ]
    )

    bot.reply_to(message, response.choices[0].message.content)

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://ТВОЙ-RENDER-URL.onrender.com/{TG_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
