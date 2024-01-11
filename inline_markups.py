from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



#  INLINE
inline = InlineKeyboardMarkup()
inline.row(InlineKeyboardButton(text = "button_1", callback_data = "button_1"))
inline.row(InlineKeyboardButton(text = "button_2", callback_data = "button_2"))
inline.row(InlineKeyboardButton(text = "button_3", callback_data = "button_3"))



#  ADD GROUP

add_group = InlineKeyboardMarkup()
add_group.add(InlineKeyboardButton(text = "Добавить бота в группу", url = "https://t.me/kawaii_ai_bot?startgroup=true"))