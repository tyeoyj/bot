from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
# from features.calendar import calendar_conv_handler
from model.keyboard_calendar import get_calendar
import os
import random

TOKEN = os.environ.get("TOKEN")
PORT = int(os.environ.get('PORT', '8443'))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
MODE = os.environ.get("MODE")

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher




def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def decide(update, context):
    text = random.choice(["Yes", "No"])
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    

start_handler = CommandHandler('start', start)
decide_handler = CommandHandler("decide", decide)
# reminder_handler = CommandHandler('reminder', reminder)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(decide_handler)
# updater.dispatcher.add_handler(CallbackQueryHandler(button))
calendar_conv_handler = get_calendar("remind")
dispatcher.add_handler(calendar_conv_handler)


if __name__ == "__main__":
    print(MODE)
    if MODE == "prod":
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN,
                            webhook_url=f"https://{HEROKU_APP_NAME}.herokuapp.com/" + TOKEN)

        updater.idle()
    else:
        updater.start_polling()