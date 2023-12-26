
import calendar
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import consts


def get_calendar_markup(month_delta=0):
    keyboard = []
    now = datetime.now()
    year = now.year
    month = now.month + month_delta

    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1

    cal = calendar.monthcalendar(year, month)

    header_text = calendar.month_name[month] + ' ' + str(year)
    keyboard.append([InlineKeyboardButton(header_text, callback_data="ignore")])


    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=f"{year}-{month:02d}-{day:02d}"))
        keyboard.append(row)
        
    if month_delta == 1:
        keyboard.append([
            InlineKeyboardButton("<<", callback_data=consts.MONTH_NOW),
        ])
    elif month_delta == -1:
        keyboard.append([
            InlineKeyboardButton(">>", callback_data=consts.MONTH_NOW)
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("<<", callback_data=consts.MONTH_PREVIOUS),
            InlineKeyboardButton(">>", callback_data=consts.MONTH_NEXT)
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)