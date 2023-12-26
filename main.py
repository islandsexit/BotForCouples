import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import CallbackQuery
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from keyboards.calendar import get_calendar_markup
import sqlite3
from datetime import datetime
from utils import consts, phrases
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command

logging.basicConfig(level=logging.INFO)

bot = Bot(token=consts.APP_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('events.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        event_date TEXT,
        event_description TEXT
    )
''')
conn.commit()

class AddEvent(StatesGroup):
    EnterDescription = State()

@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    await message.reply(phrases.WELCOME)

async def cmd_add_event(message: types.Message):
    await message.reply(phrases.CHOOSE_DATE, reply_markup=get_calendar_markup())

async def inline_calendar_handler(callback_query: CallbackQuery, state: FSMContext):
    selected_date = callback_query.data
    
    if selected_date == 'ignore':
        return  # Ignore the callback for "ignore" button
    
    
    if selected_date == consts.MONTH_NEXT:
        await callback_query.message.edit_reply_markup( reply_markup=get_calendar_markup(1))
    elif selected_date == consts.MONTH_PREVIOUS:
        await callback_query.message.edit_reply_markup(reply_markup=get_calendar_markup(-1))
    elif selected_date == consts.MONTH_NOW:
        await callback_query.message.edit_reply_markup(reply_markup=get_calendar_markup())
    else:
        await callback_query.message.edit_text(f"You selected date: {selected_date}. Now, enter the event description.")
        await callback_query.message.delete_reply_markup()
        await AddEvent.EnterDescription.set()
        await state.update_data(selected_date=selected_date)
        
        
async def save_event(message: types.Message, state: FSMContext):
    event_data = await state.get_data()
    event_date = event_data.get('selected_date')
    event_description = message.text

    if event_date and event_description:
        chat_id = message.chat.id
        cursor.execute('INSERT INTO events (chat_id, event_date, event_description) VALUES (?, ?, ?)', (chat_id, event_date, event_description))
        conn.commit()
        await message.reply('Event added successfully!')
        await state.finish()
    else:
        await message.reply('Error adding event. Please try again.')


async def cmd_get_events(message: types.Message):
    date = message.get_args() if message.get_args() else datetime.now().strftime('%Y-%m-%d')
    chat_id = message.chat.id

    cursor.execute('SELECT event_description FROM events WHERE chat_id=? AND event_date=?', (chat_id, date))
    events = cursor.fetchall()

    if events:
        event_list = '\n'.join([event[0] for event in events])
        await message.reply(f'Events on {date}:\n{event_list}')
    else:
        await message.reply(f'No events found on {date}.')

@dp.message_handler(state=AddEvent.EnterDescription)
async def enter_description(message: types.Message, state: FSMContext):
    await save_event(message, state)

async def unknown(message: types.Message):
    await message.reply("Sorry, I don't understand that command.")

dp.register_message_handler(cmd_add_event, commands='add_event')
# dp.register_message_handler(save_event, content_types=types.ContentTypes.TEXT, state='*')
dp.register_message_handler(cmd_get_events, commands='get_events')
dp.register_callback_query_handler(inline_calendar_handler, state='*')
dp.register_message_handler(unknown)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
