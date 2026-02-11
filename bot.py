import telebot
import requests
import os
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

# Налаштування
TOKEN = '8048666406:AAGuIA7o4lYNjVtpF_gy_Rm1sq34xukPzlI'
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Finance Bot is active!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 1. Отримання курсу НБУ (Офіційний)
def get_nbu_rate():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    try:
        response = requests.get(url).json()
        for item in response:
            if item['cc'] == 'USD':
                return item['rate']
    except:
        return None

# 2. Отримання готівкового курсу (Обмінники/Банки)
# Використовуємо відкрите API Monobank або аналогічні джерела для реального ринку
def get_market_rate():
    url = "https://api.monobank.ua/bank/currency"
    try:
        response = requests.get(url).json()
        # Код валюти 840 - USD, 980 - UAH
        for item in response:
            if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980:
                return {
                    'buy': item['rateBuy'],
                    'sell': item['rateSell']
                }
    except:
        return None

@bot.message_handler(commands=['start', 'rate', 'p'])
def send_analytics(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    nbu = get_nbu_rate()
    market = get_market_rate()
    
    if not nbu or not market:
        bot.send_message(message.chat.id, "❌ Помилка отримання даних. Спробуйте через хвилину.")
        return

    # Розрахунок спреду (різниця між купівлею та продажем)
    spread = market['sell'] - market['buy']
    
    # Аналітична логіка
    # Якщо курс продажу в обміннику значно вищий за НБУ (> 0.60 грн) — це "перегрітий" ринок
    diff_nbu_market = market['sell'] - nbu
    
    if diff_nbu_market > 0.70:
        trend = "⚠️ **РИНОК ПЕРЕГРІТИЙ**"
        advice = "🔴 **ПОРАДА:** В обмінниках курс занадто завищений відносно НБУ. Краще **зачекати 2 дні**, поки спред зменшиться."
    elif spread > 0.40:
        trend = "📉 **ВИСОКА ВОЛАТИЛЬНІСТЬ**"
        advice = "🟡 **ПОРАДА:** Велика різниця між купівлею та продажем. Ринок нервує. Купуйте тільки якщо дуже потрібно."
    else:
        trend = "✅ **РИНОК СТАБІЛЬНИЙ**"
        advice = "🟢 **ПОРАДА:** Курс адекватний. Можна купувати зараз."

    response_text = (
        f"📊 **АНАЛІЗ РИНКУ ВАЛЮТ**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏛 **Курс НБУ:** `{nbu:.2f} грн`\n\n"
        f"💰 **Готівковий ринок (Mono):**\n"
        f"  • Купівля: `{market['buy']:.2f} грн`\n"
        f"  • Продаж:  `{market['sell']:.2f} грн`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{trend}\n\n"
        f"{advice}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"_Оновлено: {datetime.now().strftime('%H:%M:%S')}_"
    )

    bot.send_message(message.chat.id, response_text, parse_mode='Markdown')

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
