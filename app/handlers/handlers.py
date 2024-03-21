import datetime
from aiogram.types import Message
from app.scripts.data import Data
from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandStart
from app.settings import settings
from aiogram.fsm.context import FSMContext
from app.utils.reminder_class import Reminder
from aiogram.enums import ParseMode
from app.keyboards.kb_for_reminder import kb_reminder_one_or_many, kb_state

router = Router()
db = Data('app/database/database.db')


@router.message(CommandStart())
async def start(message: Message):
    """
    Команда /start
    """
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await message.answer(f'Привет, {message.from_user.first_name}.\n'
                             f'Данный бот был предназначен для того что бы вы получали'
                             f' напоминание о выполнение домашнего задания.\n'
                             f'Так-же я хочу выкладывать сюда всю организационную информацию.')


@router.message(Command('sendall'))
async def send_all(message: Message, bot: Bot):
    """
    Рассылка сообщения от админа всем пользователям.
    """
    if message.chat.type == 'private':
        if message.from_user.id == settings.bots.admin_id:
            text = message.text[9:]
            users = db.get_users()
            for user in users:
                try:
                    await bot.send_message(user[0], f'Рассылка: {message.from_user.first_name} - {text}')
                    if int(user[1]) != 1:
                        db.set_active_user(user[0], 1)
                except RuntimeError:
                    db.set_active_user(user[0], 0)
                    print('Рассылка была не отправлена!')
            await bot.send_message(message.from_user.id, 'Рассылка была отправлена!')


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    """
    Передает фотку от админа ко всем пользователям.
    """
    if message.chat.type == 'private':
        if message.from_user.id == settings.bots.admin_id:
            users = db.get_users()
            for user in users:
                try:
                    await bot.send_photo(user[0], message.photo[-1].file_id)
                    if int(user[1]) != 1:
                        db.set_active_user(user[0], 1)
                except ValueError as e:
                    db.set_active_user(user[0], 0)
                    print(f'Скрин(Фото) не было отправлено! Ошибка: {e}')


@router.message(Command('reminder'))
async def handle_reminder(message: Message, state: FSMContext):
    await state.set_state(Reminder.name)
    await message.answer('Отправь мне название <b>напоминания</b>', parse_mode=ParseMode.HTML)


@router.message(Reminder.name)
async def handle_reminder_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reminder.time)
    await message.answer('Отправь время <b>напоминалки в форме мин:сек</b>', parse_mode=ParseMode.HTML)


@router.message(Reminder.time)
async def handle_reminder_time(message: Message, state: FSMContext):
    try:
        if datetime.time.fromisoformat(message.text):
            await state.update_data(time=message.text)
            await state.set_state(Reminder.one_time)
            await message.answer('Теперь ответьте: <b>Ваше напоминание одноразовое или нет?</b>',
                                 parse_mode=ParseMode.HTML, reply_markup=kb_reminder_one_or_many)
    except ValueError:
        await message.answer('Вы ввели некорректное время!')


@router.message(Reminder.one_time)
async def handle_reminder_one_time(message: Message, state: FSMContext):
    if message.text.lower() == 'одноразовое':
        await state.update_data(one_time=1)
        await state.set_state(Reminder.result)
        await message.answer('Вы успешно создали одноразовое напоминание!\nНажмите кнопку подтвердить',
                             reply_markup=kb_state)
    elif message.text.lower() == 'многоразовое':
        await state.update_data(one_time=0)
        await state.set_state(Reminder.result)
        await message.answer("Вы успешно создали многоразовое напоминание!\nНажмите кнопку подтвердить",
                             reply_markup=kb_state)
    else:
        await message.answer("Вы неправильно ответили!")


@router.message(Reminder.result)
async def handle_result(message: Message, state: FSMContext):
    context_data = await state.get_data()
    reminder_data = f'Вы успешно создали напоминание\nНазвание: {context_data["name"]}\nВремя: {context_data["time"]}\nТип: {"Одноразовое" if context_data.get("one_time") else "Многоразовое"}'
    await message.answer(reminder_data)
    await state.clear()

