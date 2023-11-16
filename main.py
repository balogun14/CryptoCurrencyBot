#!/usr/bin/env python
# pylint: disable=unused-argument

"""
First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import os
from typing import Optional, Tuple
from telegram import (
    Bot,
    ChatMember,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
    Update,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
    ChatMemberHandler,
)
from scrapper import news_scrapper, price_list_scrapper
from functions import garbage_collector, image_handler

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
    "/rules": "reminds you of the channel rules admin only",
    "/delete": "delete the message that violates group rules (admin only)",
    "/ban!": "bans the user that violates group rules (admin only)",
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


# Define a few command handlers. These usually take the two arguments update and
bot = Bot(BOT_TOKEN)  # type:ignore


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.effective_chat.send_action(action=ChatAction.TYPING)  # type: ignore
    chat_id = update.message.chat_id  # type: ignore
    context.job_queue.run_repeating(fetch_news_every_2_hrs, interval=2 * 60 * 60, first=0, chat_id=chat_id)  # type: ignore
    await update.message.reply_text("I will send news every two hours")  # type: ignore


# welcomes new members
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.effective_chat.send_action(action=ChatAction.TYPING)  # type: ignore
    await update.message.reply_text("List Of commands Available")  # type: ignore
    string_map = "\n".join([f"{key}: {value}" for key, value in commands.items()])
    await update.message.reply_text(string_map)  # type: ignore


def extract_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None)
    )

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def fetch_news_every_2_hrs(context: ContextTypes.DEFAULT_TYPE) -> None:
    """daemon function that fetches news every two hours.

    Args:
        context (ContextTypes.DEFAULT_TYPE): The context
    """
    news_content = news_scrapper()
    text_message: str = f"<b>{news_content[0]}</b>\n{news_content[2]}"
    file_name: str = news_content[1]
    photo: str = await image_handler(file_name)
    await context.bot.send_photo(  # type:ignore
        photo=open(photo, "rb"),
        caption=text_message,
        parse_mode="Html",
        chat_id=context._chat_id,  # type:ignore
    )
    garbage_collector(
        list=news_content, photo=photo
    )  # Garbage collector :This clears the content of the list for new entries


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the rules when the command `/rules` is issued."""
    await update.effective_chat.send_action(action=ChatAction.TYPING)  # type: ignore
    message = "\n".join(rulesArray)
    await update.message.reply_text(message, parse_mode="Html")  # type: ignore


async def greet_chat_members(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Greets new users in chats and announces when someone leaves"""
    result = extract_status_change(update.chat_member)  # type:ignore
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()  # type:ignore
    member_name = update.chat_member.new_chat_member.user.mention_html()  # type:ignore

    if not was_member and is_member:
        await update.effective_chat.send_message(  # type:ignore
            f"{member_name} was added by {cause_name}. Welcome! to The Channel",
            parse_mode="Html",
        )
    elif was_member and not is_member:
        await update.effective_chat.send_message(  # type:ignore
            f"{member_name} is no longer with us. Thanks a lot, {cause_name} ...",
            parse_mode="Html",
        )


async def filter_non_admin_messages(update: Update):
    """This filters messages and checks if not sent by an admin
    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_

    Returns:
        _type_: `True`
    """
    message = update.message
    if not message.from_user.name == ChatMember.ADMINISTRATOR:  # type:ignore
        return False

    return True


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends the recent news  when the command `/news` is issued.
    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_
    """
    news_content = news_scrapper()
    await update.effective_chat.send_action(  # type:ignore
        action=ChatAction.TYPING
    )
    text_message: str = f"<b>{news_content[0]}</b>\n{news_content[2]}"
    file_name: str = news_content[1]
    photo: str = await image_handler(file_name)
    await update.effective_chat.send_photo(  # type:ignore
        photo=open(photo, "rb"), caption=text_message, parse_mode="Html"
    )
    garbage_collector(
        list=news_content, photo=photo
    )  # Garbage collector :This clears the content of the list for new entries


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if filter_non_admin_messages is False:
        replied_message = (
            update.effective_message.reply_to_message.message_id
        )  # type:ignore
        await context.bot.delete_message(
            chat_id=context._chat_id, message_id=replied_message
        )  # type:ignore
    else:
        await update.message.reply_text(
            text="Unauthorized Access You have to be an admin to use this"
        )  # type:ignore


async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if filter_non_admin_messages is False:
       await update.message.reply_text("Unauthorised ascess") # type:ignore
       return
    await update.effective_chat.ban_member(user_id=context._user_id)  # type:ignore


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()  # type:ignore

    await query.edit_message_text(text=f"Selected option: {query.data}")  # type:ignore


async def get_priceList(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """This sends a list of stock price

    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_
    """
    res = price_list_scrapper()
    await update.effective_chat.send_action(action=ChatAction.TYPING)  # type: ignore
    string_map = "\n".join([f"{key}: {value}" for key, value in res.items()])
    await update.message.reply_text(  # type:ignore
        text="Current crypto price list for top 100"
    )  # type:ignore
    await update.message.reply_text(text=string_map)  # type:ignore


async def get_stockprice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """in progress

    Args:
        update (Update): _description_
        context (ContextTypes.DEFAULT_TYPE): _description_
    """
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


async def ban_users_that_sends_link(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if filter_non_admin_messages is False:
        await update.effective_chat.ban_member(user_id=context._user_id)  # type:ignore


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
    application.add_handler(CommandHandler("ban!", ban))

    application.add_handler(
        MessageHandler(
            filters.TEXT & (filters.Entity(MessageEntity.URL)),
            ban_users_that_sends_link,
        )
    )
    application.add_handler(
        ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER)
    )

    # application.add_handler(CallbackQueryHandler(button))
    # runs every two hours
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    # app.run()
    main()
