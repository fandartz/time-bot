from aiogram import Bot, types, asyncio
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram.types import ContentType, Message
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import time

version = '2.2'

TOKEN = 'token'
chat_id = -111111 #ид чата где будет работать бот


tz = pytz.timezone('Europe/Moscow')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
flag = True

print('[~] Успешно запущено | Версия: ', version)

#Запуск ночного режима
async def on_startup(dispatcher):
    asyncio.create_task(chek_current_time())

#Функция ночного режима       
async def chek_current_time():
    print('Работаю')
    while True:
        try:
            mydatetime = datetime.now(tz)
            if ((int(mydatetime.hour)>=22) or (int(mydatetime.hour) < 8)):
                global flag
                if flag:
                    await bot.send_message(chat_id, "НОЧНОЙ РЕЖИМ ВКЛЮЧЁН! \n\n❌ Начиная с этого времени и до 8 утра - НИКТО ИЗ ПОЛЬЗОВАТЕЛЕЙ не сможет присылать текстовые сообщения и ссылки в чат.")
                flag = False
                permissions = {
                    'can_send_messages': False, 
                    'can_send_media_messages': False, 
                    'can_send_polls': False, 
                    'can_send_other_messages': False, 
                    'can_add_web_page_previews': False, 
                    'can_change_info': False, 
                    'can_invite_users': False, 
                    'can_pin_messages': False
                }
                await bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
            else:
                if not flag:
                    await bot.send_message(chat_id, "НОЧНОЙ РЕЖИМ ОТКЛЮЧЁН \n\n✅ Доброе утро! Пользователи могут снова присылать текстовые сообщения и ссылки в чат.")
                flag = True
                permissions = {
                    'can_send_messages': True, 
                    'can_send_media_messages': True, 
                    'can_send_polls': True, 
                    'can_send_other_messages': True, 
                    'can_add_web_page_previews': True, 
                    'can_change_info': False, 
                    'can_invite_users': True, 
                    'can_pin_messages': False
                }
                await bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
            time.sleep(1)
        except:
            pass
            

#Добавление запрещённого слова
@dp.message_handler(commands=['addword'], user_id=["1111"]) #Админы для добавления слов
async def add_word(Message, command: Text):
    with open("/storage/emulated/0/bot/words.txt", "r", encoding="utf-8") as file:
        ban_words = [row.strip() for row in file]
    if any(word in command.args for word in ban_words):
        await bot.send_message(Message.chat.id, text = 'Данное слово уже есть')
    else:
        add = ban_words + [command.args]
        with open("/storage/emulated/0/bot/words.txt", "w", encoding="utf-8") as file:
            file.writelines("%s\n" % line for line in add)
        await bot.send_message(Message.chat.id, text = 'Слово добавлено!')
        
#Существующие слова
@dp.message_handler(commands=['words'], user_id=["1111"]) #Админы для добавления слов
async def words(Message):
    print('открыл')
    with open("/storage/emulated/0/bot/words.txt", "r", encoding="utf-8") as file:
        ban_words = [row.strip() for row in file]
    await bot.send_message(Message.chat.id, ban_words)
    
#/start
@dp.message_handler(commands=['start'])
async def start(Message):
    await bot.send_message(Message.chat.id, text = 'Привет!')

#Приветствие пользователей
#/storage/emulated/0/bot/words.txt
@dp.message_handler(content_types=[ContentType.NEW_CHAT_MEMBERS])
async def new_members_handler(Message):
    global flag
    await bot.delete_message(Message.chat.id, Message.message_id)
    inline_btn_1 = InlineKeyboardButton('Правила', url='https://google.com')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
    new_member = Message.new_chat_members[0]
    if flag:
        await bot.send_message(Message.chat.id, f"Добро пожаловать, {new_member.mention} \n\n ❗️Внимание, если вам предлагают доставку товара - это мошенники и никакого отношения к магазину '1111' не имеют❗️\nМы ❗️НЕ ОСУЩЕСТВЛЯЕМ❗️ продажу жидкостей, картриджей, испарителей, одноразовых и многоразовых электронных сигарет С ДОСТАВКОЙ.\n\nПожалуйста, ознакомьтесь с правилами", reply_markup=inline_kb1)
        
#Удаление сообщения о выходе
@dp.message_handler(content_types=[ContentType.LEFT_CHAT_MEMBER])
async def left_members_handler(Message):
    await bot.delete_message(Message.chat.id, Message.message_id)

#Проверка на запретку + пересыл тупых сообщений
@dp.message_handler(content_types=['text'])
async def send_message(Message):
    if(Message.chat.id != chat_id):
        await bot.forward_message(chat_id=-1111111, from_chat_id=Message.chat.id, message_id=Message.message_id) #Пересылка в мою группу
        await bot.send_message(Message.chat.id, text = 'Друг, я не умею отвечать на вопросы. Если тебя что-то интересует, то ты можешь задать свой вопрос с 8:00 до 22:00 в чате https://google.com')
    with open("/storage/emulated/0/bot/words.txt", "r", encoding="utf-8") as file:
        ban_words = [row.strip() for row in file]
    if any(word in Message.text.lower() for word in ban_words):
        await Message.delete()
        await bot.ban_chat_member(Message.chat.id, Message.from_user.id)




if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True,)