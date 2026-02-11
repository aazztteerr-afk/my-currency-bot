import telebot
import requests
import os
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

# Твій токен
TOKEN = '8048666406:AAGuIA7o4lYNjVtpF_gy_Rm1sq34xukPzlI'
bot = telebot.TeleBot(TOKEN)

# Веб-сервер для Render (щоб не засинав)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Функція: дізнатися курс за конкретну дату
def get_usd_rate(date_obj):
    date_str = date_obj.strftime("%Y%m%d") # перетворюємо дату у формат 20231025
    url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={date_str}&json"
    response = requests.get(url).json()
    for item in response:
        if item['cc'] == 'USD':
            return item['rate']
    return 0

@bot.message_handler(commands=['start', 'rate'])
def analytics(message):
    try:
        # 1. Беремо дати
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # 2. Беремо курси
        rate_today = get_usd_rate(today)
        rate_yesterday = get_usd_rate(yesterday)

        if rate_today == 0 or rate_yesterday == 0:
            bot.send_message(message.chat.id, "Помилка НБУ. Спробуйте пізніше.")
            return

        # 3. Аналізуємо різницю
        diff = rate_today - rate_yesterday
        
        # Логіка порад
        if diff > 0.05:
            trend = "📈 **Тренд: Долар дорожчає!**"
            advice = "🔴 **ПОРАДА:** Краще зачекати. Курс пішов вгору порівняно з вчорашнім днем."
        elif diff < -0.05:
            trend = "📉 **Тренд: Долар падає!**"
            advice = "🟢 **ПОРАДА:** Гарний момент для купівлі! Гривня зміцнилася."
        else:
            trend = "⚖️ **Тренд: Стабільність.**"
            advice = "🟡 **ПОРАДА:** Курс майже не змінився. Можна купувати/продавати у звичному режимі."

        # 4. Формуємо красиву відповідь
        text = (
            f"💵 **Курс сьогодні:** {rate_today:.2f} грн\n"
            f"🗓 **Курс вчора:** {rate_yesterday:.2f} грн\n"
            f"📊 **Зміна за добу:** {diff:+.2f} грн\n\n"
            f"{trend}\n{advice}"
        )
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Щось пішло не так: {e}")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
