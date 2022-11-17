from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import operator


kb = types.ReplyKeyboardMarkup(row_width=3)
admin = types.InlineKeyboardButton(text="Сделать админом")
stat = types.InlineKeyboardButton(text="Статистика")
leave_off = types.InlineKeyboardButton(text="Выйти из чата")
count_message = types.InlineKeyboardButton(text="Топ активных")
kb.add(admin, stat, leave_off, count_message)
ban_person = types.InlineKeyboardButton(text="Забанить")
unban_person = types.InlineKeyboardButton(text="Разбанить")
kb.add(ban_person, unban_person)
pin_message = types.InlineKeyboardButton(text="Закрепить сообщение")
unpin_message = types.InlineKeyboardButton(text="Открепить последнее сообщение")
unpin_all_messages = types.InlineKeyboardButton(text="Открепить все сообщения")
kb.add(pin_message, unpin_message, unpin_all_messages)

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class dialog(StatesGroup):
    blacklist = State()
    adminlist = State()
    whitelist = State()
    pinn = State()


userlist = dict()
idlist = dict()


async def update(message: types.Message):
    userlist['@' + message.from_user.username] = message.from_user.id
    idlist[message.from_user.id] = '@' + message.from_user.username

    for member in message.new_chat_members:
        userlist['@' + member.username] = member.id
        idlist[member.id] = '@' + member.username


async def login(message: types.Message):
    for admin in (await bot.get_chat_administrators(chat_id=message.chat.id)):
        if admin["user"]["id"] == message.from_user.id:
            return True
    return False


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: Message):
    await message.answer('А что это за пупсик к нам пришёл? ☺️')
    await update(message)


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer('Привет!\nВыбирай, что хочешь)', reply_markup=kb)


@dp.message_handler(content_types=['text'], text='Сделать админом')
async def adminka(message: Message):
    if await login(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Назад"))
        await message.answer('Введи username пупса \n\nДля отмены нажми ниже', reply_markup=keyboard)
        await dialog.adminlist.set()
    else:
        await message.answer('Хорошо, что ты веришь в равноправие, но прав все-таки у тебя нет', reply_markup=kb)


@dp.message_handler(state=dialog.adminlist)
async def process(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer('Возвращаю назад', reply_markup=kb)
        await state.finish()
    else:
        if message.text.strip(' ')[0] != '@':
            await message.answer('Неправильный формат ввода', reply_markup=kb)
            await state.finish()
        else:
            try:
                user_id = int(userlist[message.text.strip(' ')])
                await bot.promote_chat_member(chat_id=message.chat.id, user_id=user_id, can_manage_chat=True,
                                              can_change_info=True,
                                              can_delete_messages=True,
                                              can_manage_video_chats=True,
                                              can_promote_members=True,
                                              can_pin_messages=True,
                                              can_edit_messages=True,
                                              can_post_messages=True,
                                              can_restrict_members=True,
                                              can_invite_users=True)
                await message.answer(f"{message.text} теперь стал админом)", reply_markup=kb)
            except:
                await message.answer('Я не знаю такую персону', reply_markup=kb)
            await state.finish()


@dp.message_handler(content_types=['text'], text='Забанить')
async def ban_handler(message: types.Message):
    if await login(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Назад"))
        await message.answer('Введите id пользователя, которого нужно заблокировать.\n\nДля отмены нажми ниже',
                             reply_markup=keyboard)
        await dialog.blacklist.set()
    else:
        await message.answer('Хорошо, что ты веришь в равноправие, но прав все-таки у тебя нет', reply_markup=kb)


@dp.message_handler(state=dialog.blacklist)
async def ban(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        await message.answer('Возвращаю назад.', reply_markup=kb)
        await state.finish()
    else:
        if message.text.strip(' ')[0] != '@':
            await message.answer('Неправильный формат ввода', reply_markup=kb)
            await state.finish()
        else:
            try:
                user_id = int(userlist[message.text.strip(' ')])
                await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
                await message.answer(f"{message.text} забанен, поздравляю!", reply_markup=kb)
            except:
                await message.answer('Я не знаю такую персону, попробуй вручную', reply_markup=kb)
            await state.finish()


@dp.message_handler(content_types=['text'], text='Разбанить')
async def unban_handler(message: types.Message):
    if await login(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Назад"))
        await message.answer('Введите id пользователя, которого нужно разблокировать.\n\nДля отмены нажми ниже',
                             reply_markup=keyboard)
        await dialog.whitelist.set()
    else:
        await message.answer('Хорошо, что ты веришь в равноправие, но прав все-таки у тебя нет', reply_markup=kb)


@dp.message_handler(state=dialog.whitelist)
async def unban(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        await message.answer('Возвращаю назад.', reply_markup=kb)
        await state.finish()
    else:
        if message.text.strip(' ')[0] != '@':
            await message.answer('Неправильный формат ввода', reply_markup=kb)
            await state.finish()
        else:
            try:
                user_id = int(userlist[message.text.strip(' ')])
                await bot.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
                await message.answer(f"{message.text} разбанен, поздравляю!", reply_markup=kb)
            except:
                await message.answer('Я не знаю такую персону, попробуй вручную', reply_markup=kb)
            await state.finish()


@dp.message_handler(content_types=['text'], text='Статистика')
async def hfandler(message: types.Message):
    await message.answer(f"Количество админов: {len(await bot.get_chat_administrators(chat_id=message.chat.id))}\n\n"
                         f"Количество пупсов: {await bot.get_chat_member_count(chat_id=message.chat.id)}\n")


@dp.message_handler(content_types=['text'], text='Закрепить сообщение')
async def pinned(message: types.Message):
    if await login(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Назад"))
        await message.answer('Введите сообщение, которое нужно закрепить.\n\nДля отмены нажми ниже',
                             reply_markup=keyboard)
        await dialog.pinn.set()
    else:
        await message.answer('Хорошо, что ты веришь в равноправие, но прав все-таки у тебя нет', reply_markup=kb)


@dp.message_handler(state=dialog.pinn)
async def pin(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        await message.answer('Возвращаю назад.', reply_markup=kb)
        await state.finish()
    else:
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=message.message_id, disable_notification=True)
        await message.answer('Сообщение успешно закреплено!', reply_markup=kb)
        await state.finish()


@dp.message_handler(content_types=['text'], text='Открепить последнее сообщение')
async def unpinned(message: types.Message):
    if await login(message):
        await bot.unpin_chat_message(chat_id=message.chat.id, message_id=message.chat.pinned_message)
        await message.answer('Сообщение успешно откреплено!', reply_markup=kb)
    else:
        await message.answer('Хорошо, что ты веришь в равноправие, но прав все-таки у тебя нет', reply_markup=kb)


@dp.message_handler(content_types=['text'], text='Открепить все сообщения')
async def unpinned_all(message: types.Message):
    if await login(message):
        await bot.unpin_all_chat_messages(chat_id=message.chat.id)
        await message.answer('Сообщения успешно откреплены!', reply_markup=kb)
    else:
        await message.answer('Хорошо, что ты веришь в равноправие, но прав все-таки у тебя нет', reply_markup=kb)


@dp.message_handler(content_types=['text'], text='Выйти из чата')
async def off(message: types.Message):
    if await login(message):
        await message.answer('Доби свободен!')
        await bot.leave_chat(chat_id=message.chat.id)
    else:
        await message.answer('Хорошо, что ты веришь в равноправие, но прав все-таки у тебя нет', reply_markup=kb)


statistic = {}


@dp.message_handler(content_types=['text'], text='Топ активных')
async def off(message: types.Message):
    sorted_tuples = sorted(statistic.items(), key=operator.itemgetter(1), reverse=True)
    length = len(sorted_tuples)
    if (length > 5):
        await message.answer(f"Топ активных в чате:\n"
                             f"1) {sorted_tuples[0][0]}\n"
                             f"2) {sorted_tuples[1][0]}\n"
                             f"3) {sorted_tuples[2][0]}\n"
                             f"4) {sorted_tuples[3][0]}\n"
                             f"5) {sorted_tuples[4][0]}\n", reply_markup=kb)
    else:
        text = f"Топ активных в чате:\n"
        for i in range(length):
            text += f"{i + 1}) {(sorted_tuples[i][0])} ({(sorted_tuples[i][1])})\n"
        await message.answer(text=text, reply_markup=kb)


@dp.message_handler()
async def fun(message: types.Message):
    await update(message)
    statistic[idlist[message.from_user.id]] = statistic.get(idlist[message.from_user.id], 0) + 1


executor.start_polling(dp, skip_updates=True)
