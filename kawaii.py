from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

import openai
import asyncio
import sqlite3
import datetime
from gtts import gTTS
import requests

import config
import inline_markups






#  LIBRARY VARIABLES

storage = MemoryStorage()

openai.api_key = config.OPENAI_TOKEN
bot = Bot(config.TOKEN)

dp = Dispatcher(bot, storage = MemoryStorage())

db = sqlite3.connect('kawaii_database.db', check_same_thread = False)
sql = db.cursor()

date_time = datetime.datetime.now().date()



#  STATES

class States(StatesGroup):
    value = State()



#  CREATING DATABASE
sql.execute('CREATE TABLE IF NOT EXISTS user_access (id INTEGER, username TEXT, firstname TEXT, lastname TEXT, date DATE)')
db.commit()






#  FORWARD TEXT

@dp.message_handler(commands = ['forward'])
async def forward_command(message: types.Message):
    if message.chat.id == 284929331:
        total = 0

        data = sql.execute('SELECT * FROM user_access').fetchall()
        all_users = sql.execute('SELECT COUNT(id) FROM user_access').fetchone()[0]

        for row in data:
            try:
                await bot.send_message(
                    chat_id = row[0],
                    text ='<b>Мне скучно, давайте пообщаемся 🥲 </b>',
                    parse_mode = 'html')
                print(f'{row[0]}:  Получил сообщение  ✅')
                total += 1
            except:
                print(f'{row[0]}:  Заблокировал бота  ❌')
        else:
            blocked_users = all_users - total
            await bot.send_message(
                chat_id = message.chat.id,
                text =
                f'<b>📊  Количество пользователей:</b>  {all_users}'
                f'<b>\n\n✅  Успешно получили:</b> {total}'
                f'<b>\n❌  Заблокировавшие:</b> {blocked_users}',
                parse_mode = 'html',
                reply_markup = None)









greeting_text = '''
<b>Привет! Меня зовут Kawaii 💖</b>

Я чат-бот с искусственным интеллектом 😇.
Не стесняйся обращаться ко мне просто как Каваи 🥰.
Задавай мне вопросы, и я с удовольствием на них отвечу.

<b>Также я готова общаться в группах – добавь меня, нажав на кнопку ниже.</b>

<b>Примеры обращений:</b>
<i> - Каваи как дела ?</i>
<i> - Каваи реши задачу ... ?</i>
<i> - Каваи что такое ... ?</i>

<b>Примеры использования генераций картинок:</b>
<i> - Сгенерируй кошку</i>
<i> - Сгенерируй закат</i>

<i>Ответы и генерации картинок будут более четкими при использовании английского языка.</i>
'''


help_text = '''
<b>Что умеет - Kawaii ?</b>

<b>Генерация текста:</b>
<i> - Отвечать на любые вопросы.</i>
<i> - Отвечать на логические вопросы.</i>
<i> - Решение разных и сложных задач.</i>
<i> - Писать коды для программистов.</i>
<i> - Писать сочинения.</i>
<i> - Сочинять текста для песен.</i>

<b>Генерация картинок:</b>
<i> - Генерация любой картинки по запросам.</i>
<i> - Понимание английского языка.</i>
<i> - Понимание русского языка.</i>

<b>Отвечать голосом:</b>
<i> - Отвечать голосом на ваши вопросы заодно имея текст.</i>
<i> - Четкое озвучивание на русском языке.</i>
<i> - Хорошее озвучивание на английском языке.</i>
'''



#  START COMMAND
@dp.message_handler(commands = ['start'])
async def start_command(message: types.Message):
    sql.execute('SELECT id FROM user_access WHERE id = ?', (message.chat.id,))
    user_id = sql.fetchone()

    if user_id == None:
        sql.execute('INSERT INTO user_access (id, username, firstname, lastname, date) VALUES (?, ?, ?, ?, ?)',
        (message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, date_time))
        db.commit()

        with open('photo/profile_photo.jpg', 'rb') as photo:
            await bot.send_photo(
                chat_id = message.chat.id,
                photo = photo,
                caption = greeting_text,
                parse_mode = 'html',
                reply_markup = inline_markups.add_group)

    else:
        with open('photo/profile_photo.jpg', 'rb') as photo:
            await bot.send_photo(
                chat_id = message.chat.id,
                photo = photo,
                caption = greeting_text,
                parse_mode = 'html',
                reply_markup = inline_markups.add_group)



#  HELP COMMAND
@dp.message_handler(commands = ['help'])
async def help_command(message: types.Message):
    await bot.send_message(
        chat_id = message.chat.id,
        text = help_text,
        parse_mode = 'html')







#  VOICE
@dp.message_handler(content_types = ['voice'])
async def get_voice(message: types.Message):
    await message.voice.download(destination_file = "voice/voice.ogg")

















#  SEND MESSAGE TO PRIVATE CHAT
async def send_message_private(message):
    prompt_text = message.text.split('каваи')
    message.text = ' '.join(prompt_text).strip()
    try:
        await bot.send_chat_action(message.chat.id, 'record_voice')
        await asyncio.sleep(3)
        response = openai.Completion.create(
            model = "babbage-002",
            prompt = message.text,
            temperature = 0.5,
            max_tokens = 1000,
            frequency_penalty = 0.2,
            presence_penalty = 0.0)
        answer = response.choices[0].text.strip()

        tts = gTTS(answer, lang = 'ru')
        tts.save(f'voice/{message.chat.id}.mp3')

        with open(f'voice/{message.chat.id}.mp3', 'rb') as audio:
            await bot.send_voice(chat_id = message.chat.id, caption = answer, voice = audio)
    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Произошла ошибка.')



#  SEND MESSAGE TO GROUP CHAT
async def send_message_group(message):
    prompt_text = message.text.split('каваи')
    message.text = ' '.join(prompt_text).strip()
    try:
        await bot.send_chat_action(message.chat.id, 'record_voice')
        await asyncio.sleep(3)
        response = openai.Completion.create(
            model = "babbage-002",
            prompt = message.text,
            temperature = 0.5,
            max_tokens = 100,
            frequency_penalty = 0.2,
            presence_penalty = 0.0)
        answer = response.choices[0].text.strip()

        tts = gTTS(answer, lang = 'ru')
        tts.save(f'voice/{message.chat.id}.mp3')

        with open(f'voice/{message.chat.id}.mp3', 'rb') as audio:
            await bot.send_voice(chat_id = message.chat.id, caption = answer, voice = audio)
    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Произошла ошибка.')



#  SEND IMAGE TO PRIVATE CHAT
async def send_image_private(message):
    prompt_text = message.text.split('сгенерируй')
    message.text = ' '.join(prompt_text).strip()
    try:
        await bot.send_chat_action(message.chat.id, 'upload_photo')
        await asyncio.sleep(3)

        response = openai.Image.create(
            prompt = message.text,
            n = 1,
            size = '1024x1024')
        image_url = response['data'][0]['url']

        downloaded_image = requests.get(image_url)
        image_path = f'images/{message.chat.id}.jpg'
        with open(image_path, 'wb') as file:
            file.write(downloaded_image.content)
            with open(f'images/{message.chat.id}.jpg', 'rb') as photo:
                await bot.send_photo(chat_id = message.chat.id, photo = photo)
    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Произошла ошибка.')



#  SEND IMAGE TO GROUP CHAT
async def send_image_group(message):
    prompt_text = message.text.split('сгенерируй')
    message.text = ' '.join(prompt_text).strip()
    try:
        await bot.send_chat_action(message.chat.id, 'upload_photo')
        await asyncio.sleep(3)

        response = openai.Image.create(
            prompt = message.text,
            n = 1,
            size = '1024x1024')
        image_url = response['data'][0]['url']

        downloaded_image = requests.get(image_url)
        image_path = f'images/{message.chat.id}.jpg'
        with open(image_path, 'wb') as file:
            file.write(downloaded_image.content)
            with open(f'images/{message.chat.id}.jpg', 'rb') as photo:
                await bot.send_photo(chat_id = message.chat.id, photo = photo)
    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Произошла ошибка.')

















#  SAVE MESSAGE
async def save_message(message):
    try:
        with open(f'questions/{message.chat.id}.txt', 'a+') as file:
            file.write(f"{message.from_user.first_name}:  {message.text}\n")
    except:
        pass





#  TEXT

@dp.message_handler()
async def text(message: types.Message):
    message.text = str.lower(message.text)


#  PRIVATE

    if message.chat.type == types.ChatType.PRIVATE:
        await save_message(message)
        if "каваи" in message.text:
            await send_message_private(message)
        elif 'сгенерируй' in message.text:
            await send_image_private(message)
        else:
            await send_message_private(message)

#  GROUP

    elif message.chat.type == types.ChatType.GROUP:
        await save_message(message)
        if "каваи" in message.text:
            await send_message_group(message)
        elif 'сгенерируй' in message.text:
            await send_image_group(message)
        else:
            pass

#  SUPERGROUP

    elif message.chat.type == types.ChatType.SUPERGROUP:
        await save_message(message)
        if "каваи" in message.text:
            await send_message_group(message)
        elif 'сгенерируй' in message.text:
            await send_image_group(message)
        else:
            pass











#  CALLBACK
@dp.callback_query_handler(lambda call: True)
async def callback_queries(call: types.CallbackQuery):


#  SEND MESSAGE
    if call.data == 'callback_1':
        await bot.send_message(
            chat_id =call.message.chat.id,
            text = '<b> TEXT </b>',
            parse_mode = 'html',
            reply_markup = None)


#  DELETE INLINE MESSAGE
    elif call.data == 'delete_inline':
        await bot.delete_message(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id)


#  EDIT INLINE TEXT
    elif call.data == 'edit_inline':
        await bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = '<b> TEXT </b>',
            parse_mode = 'html',
            reply_markup = None)


#  EDIT INLINE PHOTO
    if call.data == 'edit_photo':
        with open('photo/photo.jpg', 'rb') as photo:
            bot.edit_message_media(
                media = types.InputMedia(
                type = 'photo',
                media = photo,
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                caption = '<b> TEXT </b>',
                parse_mode = 'html'),
                reply_markup = None)




#  STATES
@dp.message_handler(state = States.value)
async def check_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.text

        #  FINISH STATE
        if message.text == 'value':
            await state.finish()

        #  SET STATE
        if message.text == 'value':
            await States.value.set()

        #  NEXT STATE
        if message.text == 'value':
            await States.next()








#  DELETE MESSAGE 1
async def delete_message_1(message):
    try:
        await bot.delete_message(chat_id = message.chat.id, message_id = message.message_id)
    except:
        pass

#  DELETE MESSAGE 2
async def delete_message_2(message):
    try:
        await bot.delete_message(chat_id = message.chat.id, message_id = message.message_id)
        await bot.delete_message(chat_id = message.chat.id, message_id = message.message_id - 1)
    except:
        pass

#  DELETE MESSAGE 3
async def delete_message_3(message):
    try:
        await bot.delete_message(chat_id = message.chat.id, message_id = message.message_id)
        await bot.delete_message(chat_id = message.chat.id, message_id = message.message_id - 1)
        await bot.delete_message(chat_id = message.chat.id, message_id = message.message_id - 2)
    except:
        pass





#  ON START UP
async def start_bot(_):
    await bot.send_message(284929331, 'The bot is successfully enabled ✅')



#  LAUNCH THE BOT
if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates = True, on_startup = start_bot)
        except Exception as e:
            print(e)
            continue