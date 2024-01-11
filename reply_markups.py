from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove



#  MENU
menu_reply = ReplyKeyboardMarkup(resize_keyboard = True)
menu_reply.row("button_1")
menu_reply.row("button_2", "button_3")
menu_reply.row("button_4")