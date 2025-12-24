import telebot
from datetime import datetime
import requests

# Получаем токен вашего ботa
TOKEN = ''
bot = telebot.TeleBot(TOKEN)

def get_weather(city):
    # Здесь мы используем OpenWeatherMap API для получения погоды
    api_key = ''  # Ваш ключ от OpenWeatherMap
    
    base_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"
    response = requests.get(base_url)
    data = response.json()
    
    if data['cod'] != '200':
        return None
    
    weather_data = {}
    
    for item in data['list']:
        dt_txt = item['dt_txt']
        
        time_part = dt_txt.split(' ')[1]
        hour = int(time_part[:2])
        
        if hour >= 6 and hour <= 12:
            period = 'утро'
        elif hour > 12 and hour <= 18:
            period = 'день'
        else:
            period = 'вечер'
            
        temp_celsius = round(item['main']['temp'] - 273.15)
        description = item['weather'][0]['description']
        
        if period not in weather_data:
            weather_data[period] = {'temperature': [], 'descriptions': []}
        
        weather_data[period]['temperature'].append(temp_celsius)
        weather_data[period]['descriptions'].append(description)
    
    result = []
    for period, values in weather_data.items():
        avg_temp = sum(values['temperature']) / len(values['temperature'])
        result.append(f"{period.capitalize()}: {avg_temp:.1f}C, погода: {', '.join(set(values['descriptions']))}")
    
    return '\n'.join(result)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я погодный бот. Напишите название города.")

@bot.message_handler(func=lambda message: True)
def handle_city(message):
    city = message.text.strip()  # Просто удалили ".lower()", теперь учитывается исходный регистр
    today = datetime.now().strftime('%Y-%m-%d')
    weather_info = get_weather(city)
    
    if weather_info is None:
        bot.reply_to(message, "Город не найден или произошла ошибка")
    else:
        bot.reply_to(message, f"Погода в городе {city.title()} на сегодня ({today}):\n\n{weather_info}\n\n"
                              + recommend_clothing(weather_info))

def recommend_clothing(weather_info):
    recommendations = {
        'Утро': '',
        'День': '',
        'Вечер': ''
    }
    
    lines = weather_info.split('\n')
    for line in lines:
        parts = line.split(': ')
        period = parts[0].strip()
        temperature_str = parts[1].split(',')[0].strip()
        temperature = float(temperature_str[:-1])  # Убираем символ градуса C
        
        if temperature < 10:
            recommendation = "Оденьтесь теплее!"
        elif temperature < 20:
            recommendation = "Возьмите куртку."
        else:
            recommendation = "Легкая одежда подойдет."
        
        recommendations[period] = recommendation
    
    rec_text = "\n".join([f"{k}: {v}" for k, v in recommendations.items()])
    return f"\nРекомендации:\n{rec_text}"

if __name__ == "__main__":
    print("Запускаю бота...")
    bot.polling(none_stop=True)