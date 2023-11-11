#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Don't forget to enable inline mode with @BotFather

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from scrapper import news_scrapper, price_list_scrapper
from functions import cfl, image_handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# bot list of commands
commands = {
    "/start": "starts the bot",
    "/news": "Gets the current news from the stock market",
    "/price": "Gets the price of the stock asked",
    "/rules": "reminds you of the channel rules",
    "/delete": "delete the message that violates group rules",
}

rulesArray = [
    "No shit posting",
    "No hate words allowed",
    "No form of advertisement is allowed",
    "No spamming",
    "Stay on topic",
    'No meta question e.g "Can i ask a question?"',
    "No promotions allowed",
]


# app = Flask(__name__)


# bot = Bot(token=BOT_TOKEN) # type: ignore
# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.effective_chat.send_action(action=ChatAction.TYPING ) # type: ignore
    chat_id = update.message.chat_id  # type: ignore
    context.job_queue.run_repeating(fetch_news_every_2_hrs, interval=2 * 60 * 60, first=0, chat_id=chat_id)  # type: ignore
    await update.message.reply_text("I will send news every two hours")  # type: ignore


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.effective_chat.send_action(action=ChatAction.TYPING ) # type: ignore
    await update.message.reply_text("List Of commands Available")  # type: ignore
    string_map = '\n'.join([f'{key}: {value}' for key,value in commands.items()])
    await update.message.reply_text(string_map)  # type: ignore


async def fetch_news_every_2_hrs(context: ContextTypes.DEFAULT_TYPE) -> None:
    news_fetched = news_scrapper()
    chat_id = context._chat_id
    await context.bot.send_message(
        chat_id=chat_id,  # type: ignore
        text=f"<b>{news_fetched[0]}</b> \n{news_fetched[1]}\nAuthor: {news_fetched[2]}\n{news_fetched[3]}",
        parse_mode="Html",
    )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_action(action=ChatAction.TYPING ) # type: ignore
    message = '\n'.join(rulesArray)
    await update.message.reply_text(message, parse_mode="Html")  # type: ignore




async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    news = news_scrapper()
    await update.effective_chat.send_action(  # type:ignore
        action=ChatAction.TYPING
    )
    text_message = f"<b>{news[0]}</b> \nAuthor: {news[2]}\n{news[3][:300]}"
    file_name = news[1]
    photo = await image_handler(file_name)
    await update.effective_chat.send_photo(  # type:ignore
        photo=open(photo, "rb"), caption=text_message, parse_mode="Html"
    )
    os.remove(photo)  # Garbage collector


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()  # type:ignore

    await query.edit_message_text(text=f"Selected option: {query.data}")  # type:ignore


async def get_priceList(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    res = price_list_scrapper()
    await update.effective_chat.send_action(action=ChatAction.TYPING ) # type: ignore
    string_map = '\n'.join([f'{key}: {value}' for key,value in res.items()])
    await update.message.reply_text(text="Current crypto price list for top 100") # type:ignore
    await update.message.reply_text(text=string_map) # type:ignore


async def get_stockprice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(  # type:ignore
        "Please choose:", reply_markup=reply_markup
    )  # type:ignore


def main():
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()  # type: ignore

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("price", get_stockprice))
    application.add_handler(CommandHandler("pricelist", get_priceList))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CallbackQueryHandler(button))
    # runs every two hours
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


# @app.route("/")
# def index():
#     return "Hello World Are you there"

if __name__ == "__main__":
    # app.run()
    main()
