import requests
import json
import telebot
from telebot import types

# Initialize the Telegram Bot API token
TOKEN = 'Ваш токен'
bot = telebot.TeleBot(TOKEN)

# Chat ID of the destination chat
CHAT_ID = 'Чат куда будет отправлен запрос'

# Dictionary to store user responses
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    # Create a keyboard with 'Calculate' and 'Make Order' buttons
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    calculate_button = types.KeyboardButton('Рассчитать курс')
    order_button = types.KeyboardButton('Сделать заказ')
    markup.add(calculate_button, order_button)
    bot.reply_to(message, f'Привет, {message.from_user.first_name}! Я бот для расчета курса Юаня.', reply_markup=markup)

@bot.message_handler(commands=['calculate'])
def calculate(message):
    response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB')
    if response.status_code == 200:
        data = json.loads(response.text)
        usdtToRub = float(data['price'])
        result1 = (usdtToRub + 2) * 1500
        result2 = 1500 * 7.34
        finalResult = result1 / result2
        # Create a keyboard with 'Update' button
        markup = types.InlineKeyboardMarkup()
        update_button = types.InlineKeyboardButton('Обновить', callback_data='update')
        markup.add(update_button)
        if finalResult is not None:
            bot.reply_to(message, f'{message.from_user.first_name}, текущий курс: {finalResult:.2f}', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Handle the 'Calculate' button
    if message.text == 'Рассчитать курс':
        calculate(message)
    # Handle the 'Make Order' button
    elif message.text == 'Сделать заказ':
        user_data[message.chat.id] = {}
        # Ask for the user's name
        bot.reply_to(message, 'Как вас зовут?')
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    name = message.text
    user_data[message.chat.id]['name'] = name
    # Ask for the user's last name
    bot.reply_to(message, 'Какая у вас фамилия?')
    bot.register_next_step_handler(message, get_last_name)

def get_last_name(message):
    last_name = message.text
    user_data[message.chat.id]['last_name'] = last_name
    # Ask for the user's Telegram profile link
    bot.reply_to(message, 'Какая ваша ссылка на профиль?')
    bot.register_next_step_handler(message, get_profile_link)

def get_profile_link(message):
    profile_link = message.text
    user_data[message.chat.id]['profile_link'] = profile_link
    # Ask for the user's city of delivery using a dropdown list
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    moscow_button = types.KeyboardButton('Москва')
    spb_button = types.KeyboardButton('Санкт-Петербург')
    markup.add(moscow_button, spb_button)
    bot.reply_to(message, 'В каком городе вы хотите получить товар?', reply_markup=markup)
    bot.register_next_step_handler(message, get_city)

def get_city(message):
    city = message.text
    user_data[message.chat.id]['city'] = city
    # Ask for the product link/photo/video without any buttons
    bot.reply_to(message, 'Введите ссылку / фото / видео товара:')
    bot.register_next_step_handler(message, get_product_info)

def get_product_info(message):
    product_info = message.text
    user_data[message.chat.id]['product_info'] = product_info
    # Ask for the product weight without any buttons
    bot.reply_to(message, 'Введите вес товара:')
    bot.register_next_step_handler(message, get_product_weight)

def get_product_weight(message):
    product_weight = message.text
    user_data[message.chat.id]['product_weight'] = product_weight
    # Send the collected information to the destination chat and thank the user for their order
    order_info = f"Новый заказ!\n\nИмя: {user_data[message.chat.id]['name']}\nФамилия: {user_data[message.chat.id]['last_name']}\nСсылка на профиль: {user_data[message.chat.id]['profile_link']}\nГород получения: {user_data[message.chat.id]['city']}\nСсылка на товар: {user_data[message.chat.id]['product_info']}\nВес товара: {user_data[message.chat.id]['product_weight']}"
    bot.send_message(CHAT_ID, order_info)
    bot.reply_to(message, 'Ваша заявка принята, не забудьте подписаться! Вам ответят в рабочие часы. Так же можете самостоятельно написать нам.')
    # Create a keyboard with links to the manager and channel
    markup = types.InlineKeyboardMarkup()
    manager_button = types.InlineKeyboardButton('Менеджер', url='https://t.me/chinaexpress1688')
    channel_button = types.InlineKeyboardButton('Канал', url='https://t.me/chinazakazfedorow')
    markup.add(manager_button, channel_button)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

if __name__ == '__main__':
    bot.polling(none_stop=True)
