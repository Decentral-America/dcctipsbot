"""
    Telegram event handlers
"""
import sys
import logging
from typing import Dict

import telegram.error
from telegram import Bot, Update, BotCommand
from telegram.ext import (Updater, Dispatcher, CommandHandler, CallbackQueryHandler, )

from dtb.settings import TELEGRAM_TOKEN, DEBUG
from tgbot.handlers.utils import error
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.blockchain import handlers as blockchain_handlers

def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # onboarding
    dp.add_handler(CommandHandler("start", onboarding_handlers.start))
    dp.add_handler(CommandHandler("help", onboarding_handlers.start))

    # blockchain
    dp.add_handler(CommandHandler("address", blockchain_handlers.address))
    dp.add_handler(CommandHandler("seed", blockchain_handlers.seed))
    dp.add_handler(CommandHandler("dcc_balance", blockchain_handlers.dcc_balance))
    dp.add_handler(CommandHandler("all_balances", blockchain_handlers.all_balances))
    dp.add_handler(CommandHandler("tipping", blockchain_handlers.tipping))
    dp.add_handler(CommandHandler("withdraw", blockchain_handlers.withdraw))
    dp.add_handler(CommandHandler("stats", blockchain_handlers.stats))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp

def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")

    updater.start_polling()
    updater.idle()

# Global variable - best way I found to init Telegram bot
bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)

def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'help': static_text.help_desc,
            'address': static_text.address_desc,
            'seed': static_text.seed_desc,
            'dcc_balance': static_text.dcc_balance_desc,
            'all_balances': static_text.all_balances_desc,
            'tipping': static_text.tipping,
            'withdraw': static_text.withdraw,
            'stats': static_text.stats_desc,
        },
        'es': {
            'help': static_text.help_desc,
            'address': static_text.address_desc,
            'seed': static_text.seed_desc,
            'dcc_balance': static_text.dcc_balance_desc,
            'all_balances': static_text.all_balances_desc,
            'tipping': static_text.tipping,
            'withdraw': static_text.withdraw,
            'stats': static_text.stats_desc,
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )

# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
set_up_commands(bot)

n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))