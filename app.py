import telebot
import openai
import re
import os
import requests
import sqlite3
import db
from PIL import Image

limited = 1000 #лимит символов для сообщений боту

bot = telebot.TeleBot("") #тут токен

@bot.message_handler(content_types=["photo"])
def photo(message):
    if message.caption and message.caption == "/edit":
        ban = db.ban('check', message.from_user.id)
        if ban:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(f'{message.from_user.id}.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)
            im = Image.open(f'{message.from_user.id}.jpg')
            new_image = im.resize((1024, 1024))
            new_image.save(f'{message.from_user.id}.png')
            os.remove(f'{message.from_user.id}.jpg')
            result = process_edit_step(f"{message.from_user.id}.png")
            if result == 'no key':
                bot.reply_to(message, f"Закончились активные ключи OpenAi\nПерейдите в бота и через комануд /token <api key> добавтье новый")
            elif result == 'error':
                bot.reply_to(message, f"Не удалось отредактировать картинку!")
            else:
                bot.send_photo(message.chat.id, result, caption=f'Успешно отредактировано!\n(Фото было ужато до формата 1024х1024)')
        else:
            try:
                bot.reply_to(message, f"Вы находитесь в черном списке!")
            except:
                try:
                    bot.send_message(message.chat.id, f"Вы находитесь в черном списке!")
                except:
                    pass
    else:
        pass

@bot.message_handler(commands=['chat'])
def handle_chat(message):
    ban = db.ban('check', message.from_user.id)
    if ban:
        result = process_chat_step(message.text.replace('/chat',  ''))
        if result == 'no key':
            bot.reply_to(message, f"Закончились активные ключи OpenAi\nПерейдите в бота и через комануд /token <api key> добавтье новый")
        elif result == 'limit':
            bot.reply_to(message, f"Вы не можете отправлять сообщения больше {str(limited)} символов!")
        elif result == 'error':
            bot.reply_to(message, f"Ошибка! ChatGPT прислал ошибку.")
        else:
            bot.reply_to(message, f"ChatGPT: {result}")
    else:
        try:
            bot.reply_to(message, f"Вы находитесь в черном списке!")
        except:
            try:
                bot.send_message(message.chat.id, f"Вы находитесь в черном списке!")
            except:
                pass
        
@bot.message_handler(commands=['img'])
def handle_chat(message):
    ban = db.ban('check', message.from_user.id)
    if ban:
        result = process_img_step(message.text.replace('/img',  ''))
        text_photo = message.text.replace('/img',  '')
        if result == 'no key':
            bot.reply_to(message, f"Закончились активные ключи OpenAi\nПерейдите в бота и через комануд /token <api key> добавтье новый")
        elif result == 'limit':
            bot.reply_to(message, f"Вы не можете отправлять сообщения больше 60 символов!")
        elif result == 'bad':
            bot.reply_to(message, f"Не удалось сгенерировать картинку!")
        else:
            bot.send_photo(message.chat.id, result, caption=f'Photo text: {text_photo}')
    else:
        try:
            bot.reply_to(message, f"Вы находитесь в черном списке!")
        except:
            try:
                bot.send_message(message.chat.id, f"Вы находитесь в черном списке!")
            except:
                pass

@bot.message_handler(commands=['token'])
def handle_chat(message):
    ban = db.ban('check', message.from_user.id)
    if ban:
        try:
            token = message.text.replace('/token ',  ' ')
        except:
            pass
        try:
            if token != '' or token != ' ':
                openai.api_key = f'{token}'
                openai.Completion.create(engine="text-davinci-002", prompt="Slava rossii")
                bot.send_message(message.chat.id, f"Ваш токен успешно добавлен!")
                db.add_token(token)
            else:
                pass
        except Exception as e:
            bot.send_message(message.chat.id, "Ваш токен не валидный!")
    else:
        try:
            bot.reply_to(message, f"Вы находитесь в черном списке!")
        except:
            try:
                bot.send_message(message.chat.id, f"Вы находитесь в черном списке!")
            except:
                pass

@bot.message_handler(commands=['ban'])
def handle_chat(message):
    try:
        target = message.reply_to_message.from_user.id
    except:
        try:
            target = message.text.replace('/ban ',  '')
        except:
            pass
    adm_list = db.get_adm(message.from_user.id)
    if adm_list != None:
        check = db.ban('ban', target)
        if check == '0':
            bot.reply_to(message, f"Пользователь заблокирован!")
        if check == '1':
            bot.reply_to(message, f"Пользователь уже был заблокирован!")
    else:
        pass


@bot.message_handler(commands=['addadmin'])
def handle_chat(message):
    try:
        target = message.reply_to_message.from_user.id
    except:
        try:
            target = message.text.replace('/addadmin ',  '')
        except:
            pass
    adm_list = db.get_adm(message.from_user.id)
    if adm_list != None:
        check = db.ban('addadmin', target)
        if check == '0':
            bot.reply_to(message, f"Пользователь успешно внесен в список админов!")
        if check == '1':
                bot.reply_to(message, f"Пользователь уже админ!")
    else:
        pass

@bot.message_handler(commands=['unban'])
def handle_chat(message):
    try:
        target = message.reply_to_message.from_user.id
    except:
        try:
            target = message.text.replace('/unban ',  '')
        except:
            pass
    adm_list = db.get_adm(message.from_user.id)
    if adm_list != None:
        check = db.ban('unban', target)
        if check == '0':
            bot.reply_to(message, f"Пользователь разблокирован!")
        if check == '1':
            bot.reply_to(message, f"Пользователь не найден в черном списке!")
    else:
        pass

def process_img_step(messages):
    if len(messages) >= 61:
    	return "limit"
    while True:
        keys = db.get_key('0')
        if keys == 'no key':
            return 'no key'
        try:
            response = requests.post(
                'https://api.openai.com/v1/images/generations',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {keys}'},
                json={'model': 'image-alpha-001', 'prompt': messages}
                )
            print(f"[LOG] - Запрос прошел успешно!")
            response_json = response.json()
            image_url = response_json['data'][0]['url']
            return image_url
            break
        except Exception as er:
            if str(er) == "You exceeded your current quota, please check your plan and billing details.":
                keys = db.get_key(keys)
                return "bad"
            elif "Incorrect API key provided" in str(er):
                keys = db.get_key(keys)
                return "bad"
            else:
                return 'bad'
                break

def process_chat_step(messages):
    if len(messages) >= limited+1:
    	return "limit"
    while True:
        keys = db.get_key('0')
        if keys == 'no key':
            return 'no key'
        try:
            openai.api_key = keys
            chat_response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=messages,
                max_tokens=2400,
                n=1,
                stop=None,
                temperature=0.3
            )
            return chat_response["choices"][0]["text"]
            break
        except Exception as er:
            if str(er) == "You exceeded your current quota, please check your plan and billing details.":
                keys = db.get_key(keys)
            elif "Incorrect API key provided" in str(er):
                keys = db.get_key(keys)
            else:
            	return f"Была вызвана ошибка: {str(er)}"

def process_edit_step(messages):
    while True:
        keys = db.get_key('0')
        if keys == 'no key':
            return 'no key'
        try:
            openai.api_key = keys
            chat_response = openai.Image.create_variation(
                image=open(f"{messages}", "rb"),
                n=1,
                size="1024x1024"
            )
            return chat_response['data'][0]['url']
            break
        except Exception as er:
            if str(er) == "You exceeded your current quota, please check your plan and billing details.":
                keys = db.get_key(keys)
            elif "Incorrect API key provided" in str(er):
                keys = db.get_key(keys)
            else:
            	return f"error"

bot.polling()

#Спасибо анечке за вдохновение, ты мой ангел!