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

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

from scrapper import scrapper
from functions import cfl

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
    "no shit posting",
    "no hate words allowed",
    "no form of advertisement is allowed",
    "no spamming",
    "stay on topic",
    'no meta question e.g "Can i ask a question?"',
    "no promotions allowed",
]


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi!")  # type: ignore


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("List Of commands Available")  # type: ignore
    for key in commands:
        text = "/" + key + ": " + commands[key]
        await update.message.reply_text(text)  # type: ignore


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
    message = f"<b>Rules</b>\n1.{cfl(rulesArray[0])}\n2.{cfl(rulesArray[1])}\n3.{cfl(rulesArray[2])}\n4.{cfl(rulesArray[3])}\n5.{cfl(rulesArray[4])}\n6.{cfl(rulesArray[5])}\n{cfl(rulesArray[6])}"
    await update.message.reply_text(message,parse_mode="Html")  # type: ignore


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    news = scrapper()
    await update.message.reply_text(f"<b>{news[0]}</b> \n{news[1]}\nAuthor: {news[2]}\n{news[3]}", parse_mode="Html")  # type:ignore


async def delete(context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def get_stockprice(context: ContextTypes.DEFAULT_TYPE, message) -> None:
    pass


def main():
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()  # type: ignore

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("news", news))

    # runs every two hours
    job_queue = JobQueue()
    job_queue.run_repeating(callback_minute, interval=60, first=10)
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
