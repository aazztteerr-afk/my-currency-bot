import telebot
import requests
import os
from flask import Flask
from threading import Thread

# Твій токен
TOKEN = '8048666406:AAGuIA7o4lYNjVtpF_gy_Rm1sq34xukPzlI'
bot = telebot.TeleBot(TOKEN)

# Створюємо мікро-сайт для Render
app = Flask('')

@app.route('/')
def home():
    return "Бот активний!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start', 'rate'])
def start_message(message):
    try:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        data = requests.get(url, timeout=10).json()
        usd = next(item for item in data if item["cc"] == "USD")["rate"]
        eur = next(item for item in data if item["cc"] == "EUR")["rate"]
        text = f"🏦 **Курс НБУ:**\n💵 USD: {usd:.2f}\n💶 EUR: {eur:.2f}"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, "❌ Помилка зв'язку з НБУ.")

if __name__ == "__main__":
    # Запуск веб-сервера в окремому потоці
    t = Thread(target=run)
    t.start()
    # Запуск бота
    bot.infinity_polling()
