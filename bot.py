import os
import config
import telebot
# from telebot import apihelper
from telebot import types

from google_translate import en_translator, ru_translator
from instagram_test import SeeStorris

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from exeptions import NoLogin, BadURL


# PROXY = 'socks5://127.0.0.1:9050'

# apihelper.proxy = {
#     'http': PROXY,
#     'https': PROXY
# }

bot = telebot.TeleBot(config.TOKEN)

user_message = ''
user_data = {
    'see': False,
    'login': None,
    'password': None,
    'url': None
}
see_users_data = {}
see_counter = 1
browser = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def remove_users_data(id):
    see_users_data[id]['login'] = None
    see_users_data[id]['password'] = None
    see_users_data[id]['url'] = None
    del see_users_data[id]

def chek_url(url:str):
    if url.startswith('https://www.instagram.com/') or url.startswith('www.instagram.com/') or url.startswith('https://instagram.com/'):
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def welcom(message):
    sti = open('static/welcom.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)

    bot.send_message(
        message.chat.id,
        ('Добро пожаловать {0.first_name}!\nЯ - <b>{1.first_name}</b>! :)'.format(message.from_user, bot.get_me()) +
        '\nЯ умею переводить текст с Английского на Русский и наоборот. Попробуй меня в деле! Давай, пиши уже!)))'),
        parse_mode='html'
    )

@bot.message_handler(commands=['rm'])
def claer(message):
    see_user_id = message.from_user.id
    remove_users_data(see_user_id)
    bot.send_message(
        message.chat.id,
        'Данные удалены'
    )

@bot.message_handler(commands=['see'])
def see_sroris(message):
    if see_counter > 10:
            bot.send_message(
                message.chat.id,
                'Извини, я пока сильно занят. Попробуй попозже!'
            )
            print('Я работаю на всю катушку, начальник')
    else:
        see_user_id = message.from_user.id
        bot.send_message(
            message.chat.id,
            'Введи свой логин в инстаграм'
        )
        see_users_data[see_user_id] = user_data
        see_users_data[see_user_id]['see'] = True

@bot.message_handler(content_types=['text'])
def main_work(message):
    print(see_users_data)
    see_user_id = message.from_user.id
    if see_user_id in see_users_data:
        if not see_users_data[see_user_id]['login']:
            see_users_data[see_user_id]['login'] = message.text
            bot.send_message(
                message.chat.id,
                'Введи пароль'
            )
        elif not see_users_data[see_user_id]['password']:
            see_users_data[see_user_id]['password'] = message.text
            bot.send_message(
                message.chat.id,
                'Введи URL целевого пользователя'
            )
        elif not see_users_data[see_user_id]['url']:
            global see_counter
            see_users_data[see_user_id]['url'] = message.text

            # Собственно старт
            try:
                if not chek_url(see_users_data[see_user_id]['url']):
                    raise BadURL('incorrect URL')

                bot.send_message(message.chat.id, 'Погнали нах!!!')

                global see_counter
                see_counter += 1

                storris = SeeStorris(
                    see_users_data[see_user_id]['login'],
                    see_users_data[see_user_id]['password'],
                    see_users_data[see_user_id]['url']
                )

                storris.run()

                remove_users_data(see_user_id)

                bot.send_message(message.chat.id, 'Я все!)))')
                see_counter -= 1

            except WebDriverException:
                remove_users_data(see_user_id)
                print('Браузер закрыт вручную')
                bot.send_message(
                    message.chat.id,
                    'Браузер кто-то закрыл!\nДанные удалены'
                )
                see_counter -= 1
            except NoLogin:
                remove_users_data(see_user_id)
                bot.send_message(
                    message.chat.id,
                    'Неверный логин или пароль. Попробуйте еще раз!\nДанные удалены'
                )
                see_counter -= 1
            except BadURL:
                remove_users_data(see_user_id)
                bot.send_message(
                    message.chat.id,
                    'Введен некоректный URL. Попробуйте еще раз!\n_URL должен начинаться на https://www.insta..._',
                    parse_mode='Markdown'
                )
                see_counter -= 1

    else: # подработка переводчиком
        if message.text.lower()[0] in 'qwertyuiopasdfghjklzxcvbnm':
            bot.send_message(message.chat.id, ru_translator(message.text))
            print(message.text)
        elif message.text.lower()[0] in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            bot.send_message(message.chat.id, en_translator(message.text))
            print(message.text)
        else:
            bot.send_message(message.chat.id, en_translator('Мне такой язык не знаком!((('))


#RUN
bot.polling(none_stop=True)
