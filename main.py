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

from telegram import Message, Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

from scrapper import scrapper
from functions import convert_first_letter_of_each_word_to_capital

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
    "start": "starts the bot",
    "news": "Gets the current news from the stock market",
    "price": "Gets the price of the stock asked",
    "rules": "reminds you of the channel rules",
    "delete": "delete the message that violates group rules",
}

rulesArray = [
    "No Shit Posting",
    "No Hate Words Allowed",
    "No Form of Advertisement Is Allowed",
    "No Spamming",
    "Stay On topic",
    'No meta question e.g "Can i ask a question?"',
]


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("List Of commands Available")
    for key in commands:
        text = "/" + key + ": " + commands[key]
        await update.message.reply_text(text)


async def get_post_every_two_hours(context: ContextTypes.DEFAULT_TYPE) -> None:
    post = scrapper()
    job = context.job
    for i in range(0, len(post)):
        await context.bot.send_message(job.chat_id, text=post[i])  # type: ignore


async def callback_minute(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id="@examplechannel", text="One message every minute"
    )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for i in range(0, len(rulesArray)):
        rulesText = convert_first_letter_of_each_word_to_capital(rulesArray[i])
        await update.message.reply_text(rulesText)


async def news(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def delete(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def get_stockprice(context: ContextTypes.DEFAULT_TYPE, message) -> None:
    pass


def main():
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # runs every two hours
    job_queue = JobQueue()
    job_queue.run_repeating(callback_minute, interval=60, first=10)
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
