import telebot
import requests
import os
from flask import Flask
from threading import Thread

TOKEN = '8048666406:AAGuIA7o4lYNjVtpF_gy_Rm1sq34xukPzlI'
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Аналітик працює!"

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

        # Твій аналітичний блок
        if usd < 41.30:
            advice = "🟢 **КУПУВАТИ:** Курс вигідний. Рекомендую поповнити валютні запаси."
        elif usd > 41.90:
            advice = "🔴 **ЗАЧЕКАТИ:** Долар на піку. Зараз купувати дорого, краще почекати відкату."
        else:
            advice = "🟡 **ТРИМАТИ:** Курс стабільний. Купуй тільки якщо є гостра потреба."

        text = (f"🏦 **Курс НБУ:**\n💵 USD: {usd:.2f} грн\n💶 EUR: {eur:.2f} грн\n\n"
                f"🧠 **АНАЛІТИКА:**\n{advice}")
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, "❌ Помилка зв'язку з банком.")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
