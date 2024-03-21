from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_reminder_one_or_many = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="одноразовое")],
    [KeyboardButton(text="многоразовое")],
], resize_keyboard=True, one_time_keyboard=True)

kb_state = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ПОДТВЕРДИТЬ")]
],resize_keyboard=True, one_time_keyboard=True)
