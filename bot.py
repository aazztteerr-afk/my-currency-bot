import telebot
import requests
import os
import time
from flask import Flask
from threading import Thread
from datetime import datetime

# Налаштування
TOKEN = '8048666406:AAGuIA7o4lYNjVtpF_gy_Rm1sq34xukPzlI'
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# Сховище для підписок (в реалі краще використовувати БД)
alerts = {} 

@app.route('/')
def home(): return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def get_rates():
    """Отримує дані НБУ та ринку одночасно"""
    try:
        nbu_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        mono_url = "https://api.monobank.ua/bank/currency"
        
        nbu_res = requests.get(nbu_url).json()
        mono_res = requests.get(mono_url).json()
        
        nbu_usd = next(item['rate'] for item in nbu_res if item['cc'] == 'USD')
        mono_usd = next(item for item in mono_res if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
        
        return {
            'nbu': nbu_usd,
            'buy': mono_usd['rateBuy'],
            'sell': mono_usd['rateSell']
        }
    except Exception as e:
        print(f"Помилка даних: {e}")
        return None

# Команда для встановлення ціни-сповіщення: /set 41.50
@bot.message_handler(commands=['set'])
def set_alert(message):
    try:
        target_price = float(message.text.split()[1].replace(',', '.'))
        alerts[message.chat.id] = target_price
        bot.reply_to(message, f"🎯 Ок! Я напишу, щойно курс продажу впаде до **{target_price} грн**.")
    except:
        bot.reply_to(message, "⚠️ Напишіть ціну у форматі: `/set 41.20`", parse_mode='Markdown')

@bot.message_handler(commands=['start', 'rate'])
def check_rate(message):
    data = get_rates()
    if not data:
        bot.send_message(message.chat.id, "❌ Помилка зв'язку з банками.")
        return

    # Логіка "зачекати 2 дні"
    diff = data['sell'] - data['nbu']
    advice = "🟢 Можна купувати." if diff < 0.6 else "🔴 Дорого! Різниця з НБУ велика, краще зачекати 2 дні."
    
    text = (
        f"🏛 НБУ: `{data['nbu']:.2f}`\n"
        f"💰 Ринок: `{data['buy']:.2f} / {data['sell']:.2f}`\n\n"
        f"📢 **Порада:** {advice}"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# Фонова перевірка курсу для сповіщень
def alert_checker():
    while True:
        try:
            data = get_rates()
            if data:
                current_sell = data['sell']
                for chat_id, target in list(alerts.items()):
                    if current_sell <= target:
                        bot.send_message(chat_id, f"🔔 **ЧАС КУПУВАТИ!**\nКурс впав до `{current_sell:.2f}` (ваша ціль: {target})", parse_mode='Markdown')
                        del alerts[chat_id] # Видаляємо після спрацювання
            time.sleep(600) # Перевіряти кожні 10 хвилин
        except Exception as e:
            print(f"Alert error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    Thread(target=run_web).start()
    Thread(target=alert_checker).start()
    bot.infinity_polling()
