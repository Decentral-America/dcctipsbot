from tgbot.models import User
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from tgbot.handlers.onboarding import static_text

def start(update: Update, context: CallbackContext) -> None:
    user, _ = User.get_user(update, context)
    if(update.message.chat.type != "private"):
        update.message.reply_text(parse_mode=ParseMode.HTML, text=static_text.private.format(bot_username=context.bot.name, bot_name=context.bot.name.replace("@", "")))
    context.bot.sendMessage(chat_id=user.user_id, parse_mode=ParseMode.HTML, text=static_text.help.format(bot_username=context.bot.name, bot_name=context.bot.name.replace("@", "")))