
import calendar
import numpy as np

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler

calendar.setfirstweekday(calendar.SUNDAY)
weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
months = calendar.month_name
# states
SELECT_DATE, SHOW_CALENDAR = range(2)

# functions to build the actual keyboard
def get_calendar_keyboard(year, month):
    keyboard = [
        
        [
            InlineKeyboardButton("<<<", callback_data=f"year_{year-1}_{month}"), 
            InlineKeyboardButton(year, callback_data=f"null"), 
            InlineKeyboardButton(">>>", callback_data=f"year_{year+1}_{month}")
            ], # Year Button
        [InlineKeyboardButton(calendar.month_name[month], callback_data=f"month_{year}_{month}")], # Month Button
        [InlineKeyboardButton(weekday, callback_data="null") for weekday in weekdays], # Days of the week
    ]
    monthday_buttons = _get_monthday_buttons(year, month)
    keyboard.extend(monthday_buttons)
    return InlineKeyboardMarkup(keyboard)

def get_month_selection_keyboard(year):
    month_buttons = [
        InlineKeyboardButton(month, callback_data=f"month_{year}_{i}") for i, month in enumerate(months) if month]
    month_buttons = np.reshape(month_buttons, (4,3)).tolist()
    return InlineKeyboardMarkup(month_buttons)


#Calendar Logic


def show_calendar(update, context):
    try:
        print("not a cb query")
        year, month = get_current_year_and_month(update)
    except AttributeError:
        query = update.callback_query
        _, year, month = query.data.split("_")
        keyboard_calendar = get_calendar_keyboard(int(year), int(month))
        query.edit_message_text("Select a date", reply_markup=keyboard_calendar)
        query.answer()
    else:
        keyboard_calendar = get_calendar_keyboard(int(year), int(month)) 
        context.bot.send_message(chat_id=update.effective_chat.id, text="Select a date" ,reply_markup=keyboard_calendar)
    return SELECT_DATE

def show_month_selection(update, context):
    query = update.callback_query
    year = query.data.split("_")[1]
    reply_markup = get_month_selection_keyboard(year)
    query.edit_message_text("Select a month", reply_markup=reply_markup)
    query.answer()
    return SHOW_CALENDAR

def select_date(update, context):
    query = update.callback_query
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"date selected = {query.data}")
    query.answer()
    return SELECT_DATE

def cancel(update, _):
    user = update.message.from_user
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def _(update, context):
    update.callback_query.answer()
    return SELECT_DATE

def _get_monthday_buttons(year, month):
    monthdays= np.array(calendar.monthcalendar(year, month))
    monthday_buttons = []
    for monthday in monthdays.ravel():
        if monthday == 0:
            button = InlineKeyboardButton(" ", callback_data=f"null")
        else:
            # need to int monthday as np.int64 is not json serializable
             button = InlineKeyboardButton(int(monthday), callback_data=f"{year}_{month}_{monthday}")  
        monthday_buttons.append(button)
    monthday_buttons = np.array(monthday_buttons).reshape(monthdays.shape)
    return monthday_buttons.tolist()

def get_current_year_and_month(update):
    year = update.message.date.year
    month = update.message.date.month
    return year, month

def get_calendar(command) -> ConversationHandler:
    calendar_conv_handler = ConversationHandler(
            entry_points=[CommandHandler(command, show_calendar)],
            states={
                SELECT_DATE : [
                    CallbackQueryHandler(show_month_selection, pattern=r"^month_[\d]{4}_([\d]{2}|[\d]{1})$"),
                    CallbackQueryHandler(show_calendar, pattern=r"^year_[\d]{4}_([\d]{2}|[\d]{1})$"),
                    CallbackQueryHandler(select_date, pattern=r"^[\d]{4}_([\d]{2}|[\d]{1})_([\d]{2}|[\d]{1})$"),
                    # handling the empty buttons
                    CallbackQueryHandler(_, pattern="null")
                    ],
                SHOW_CALENDAR: [
                    CallbackQueryHandler(show_calendar)
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
    return calendar_conv_handler
    



