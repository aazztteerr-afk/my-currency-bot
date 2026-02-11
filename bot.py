import telebot
import requests
import time

TOKEN = '8048666406:AAGuIA7o4lYNjVtpF_gy_Rm1sq34xukPzlI'
bot = telebot.TeleBot(TOKEN)

def get_rates():
    try:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        data = requests.get(url, timeout=10).json()
        usd = next(item for item in data if item["cc"] == "USD")["rate"]
        eur = next(item for item in data if item["cc"] == "EUR")["rate"]
        return usd, eur
    except Exception as e:
        return None, None

@bot.message_handler(commands=['start', 'rate'])
def start_message(message):
    usd, eur = get_rates()
    if usd:
        analysis = "📉 НБУ трохи зміцнив гривню. Гарний момент для купівлі!" if usd < 43.10 else "🚀 Курс росте. Якщо не терміново — зачекай."
        text = (f"🏦 **Курс НБУ:**\n"
                f"💵 USD: {usd:.2f}\n"
                f"💶 EUR: {eur:.2f}\n\n"
                f"💡 **Аналіз:** {analysis}")
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Помилка отримання даних.")

if __name__ == "__main__":
    bot.infinity_polling()
