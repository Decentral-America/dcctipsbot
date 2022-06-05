import decimal
import math
from telegram import Update, ParseMode
from tgbot.models import User
from datetime import timedelta
from django.utils.timezone import now
from telegram.ext import CallbackContext
from dtb.settings import pw, pw2, GENERATOR 
from tgbot.handlers.blockchain import static_text
from tgbot.handlers.utils.encryption import encrypt, decrypt

def address(update: Update, context: CallbackContext) -> None:
    user, _ = User.get_user(update, context)
    if(update.message.chat.type != "private"):
        update.message.reply_text(text=static_text.user_address)
    else:
        context.bot.send_message(chat_id=user.user_id, text=static_text.user_address)
    context.bot.send_message(chat_id=update.message.chat_id, text=user.address)

def seed(update: Update, context: CallbackContext) -> None:
    user, _ = User.get_user(update, context)
    if(update.message.chat.type != "private"):
        update.message.reply_text(static_text.private.format(bot_name=context.bot.name))
    context.bot.sendMessage(chat_id=user.user_id, text=static_text.user_seed)
    context.bot.sendMessage(chat_id=user.user_id, text=decrypt(user.seed))
    context.bot.sendMessage(chat_id=user.user_id, text=static_text.secret)
    
def dcc_balance(update: Update, context: CallbackContext) -> None:
    if(update.message.chat.type != "private"):
        msg = update.message.reply_text(text=static_text.processing)
    else:
        msg = context.bot.sendMessage(chat_id=update.message.chat_id, text=static_text.processing)
    user, _ = User.get_user(update, context)
    user_address = pw.Address(address = user.address, pywaves = pw2)
    dcc_balance = user_address.balance() / int(math.pow(10, pw2.DCC_DECIMALS))
    decimals = abs(decimal.Decimal(str(dcc_balance)).as_tuple().exponent)
    text = static_text.dcc_balance + f"{dcc_balance:.{decimals}f}"
    if(update.message.chat.type != "private"):
        msg.edit_text(text=static_text.private.format(bot_name=context.bot.name))
        context.bot.sendMessage(chat_id=user.user_id, text=text)
    else:
        msg.edit_text(text=text)

def all_balances(update: Update, context: CallbackContext) -> None:
    if(update.message.chat.type != "private"):
        msg = update.message.reply_text(text=static_text.processing)
    else:
        msg = context.bot.sendMessage(chat_id=update.message.chat_id, text=static_text.processing)
    user, _ = User.get_user(update, context)
    user_address = pw.Address(address = user.address, pywaves = pw2)
    dcc_balance = user_address.balance() / int(math.pow(10, pw2.DCC_DECIMALS))
    decimals = abs(decimal.Decimal(str(dcc_balance)).as_tuple().exponent)
    text =  pw2.DEFAULT_CURRENCY + ": " + f"{dcc_balance:.{decimals}f}" + "\n"
    assets = user_address.assets()
    for asset_id in assets:
        asset = pw.Asset(asset_id, pywaves = pw2)
        asset_name = asset.name.decode('utf8')  + ": "
        text += asset_name
        asset_balance = user_address.balance(asset_id) / int(math.pow(10, asset.decimals))
        decimals = abs(decimal.Decimal(str(asset_balance)).as_tuple().exponent)
        text += f"{asset_balance:.{decimals}f}" + "\n"
    if(update.message.chat.type != "private"):
        msg.edit_text(text=static_text.private.format(bot_name=context.bot.name))
        context.bot.sendMessage(chat_id=user.user_id, text=text)
    else:
        msg.edit_text(text=text)

def tipping(update: Update, context: CallbackContext) -> None: # receives the parameters <username> <amount> <token>
    if(update.message.chat.type != "private"):
        msg = update.message.reply_text(text=static_text.processing)
    else:
        msg = context.bot.sendMessage(chat_id=update.message.chat_id, text=static_text.processing)
    try:
        count = 0 # in case there are no arguments
        recipients = []
        for count, username in enumerate(context.args): # get all the usernames of the recipients (usernames must contain @)
            if username[0] == '@':
                recipients.append(username.replace("@", "").strip().lower())
            else: # if username has no @ it could either be a mistake made by the user or the value represents <amount>
                if(not recipients): # if we have no recipients so far then it was a mistake made by the user
                    msg.edit_text(text=static_text.missing_username.format(bot_name=context.bot.name))
                    return
                else: # there are recipients already so the missing @ could mean the value represents <amount> and not a username
                    break
        amount = float(context.args[count])
        count+=1
        token = " ".join(str(x) for x in context.args[count:]).strip().lower() # after getting <username> and <amount> all the remaining values represent <token>
        send_tokens = {"send": False, "dcc": False}
        sender_user, _ = User.get_user(update, context)
        sender_address = pw.Address(seed = decrypt(sender_user.seed), pywaves = pw2)
        if(token == pw2.DEFAULT_CURRENCY.strip().lower()): # DCC
            dcc_balance = sender_address.balance() / math.pow(10, pw2.DCC_DECIMALS)
            if(dcc_balance >= amount):
                amount = int(amount * math.pow(10, pw2.DCC_DECIMALS))
                send_tokens["send"] = True
                send_tokens["dcc"] = True
            else:
                msg.edit_text(text=static_text.missing_amount)
                return
        else: # Other coin
            sender_assets = sender_address.assets()
            if(sender_assets):
                for asset_id in sender_assets:
                    asset = pw.Asset(asset_id, pywaves = pw2)
                    asset_name = asset.name.decode('utf8').strip().lower()
                    if(token == asset_name):
                        asset_balance = sender_address.balance(asset_id) / int(math.pow(10, asset.decimals))
                        if(asset_balance >= amount):
                            amount = amount if asset.decimals == 0 else int(amount * math.pow(10, asset.decimals))
                            send_tokens["send"] = True
                        else:
                            msg.edit_text(text=static_text.missing_amount)
                            return
            else:
                msg.edit_text(text=static_text.missing_token)
                return
        #At this point we have determined which token is being send and if the user has the required amount
        if(send_tokens["send"] == True):
            count = 0
            for count, recipient_username in enumerate(recipients):
                recipient_user = User.get_user_by_username(recipient_username)
                if str(recipient_user) != 'None':
                    recipient = pw.Address(seed = decrypt(recipient_user.seed), pywaves = pw2)
                else:
                    recipient = pw.Address(GENERATOR, pywaves=pw2)
                    recipient._generate()
                    User.create_by_seed(recipient.address, encrypt(recipient.seed.encode('utf8')), recipient_username)
                if(send_tokens["dcc"] == True): #DCC is being sent                
                    tip = sender_address.sendWaves(recipient = recipient, amount = amount)
                else: #A different token is being sent
                    tip = sender_address.sendAsset(recipient = recipient, asset = asset, amount = amount)
                if count == 0:
                    if(update.message.chat.type != "private"):
                        text = static_text.sent_tokens.format(bot_name=context.bot.name) if len(recipients) == 1 else static_text.multi_sent_tokens.format(bot_name=context.bot.name)
                        msg.edit_text(text=text)
                        context.bot.sendMessage(chat_id=sender_user.user_id, parse_mode=ParseMode.HTML, text=static_text.sent_tokens_receipt.format(recipient_username=recipient_username, transaction_id=tip["id"]))
                    else:
                        msg.edit_text(text=static_text.sent_tokens_receipt.format(recipient_username=recipient_username, transaction_id=tip["id"]), parse_mode=ParseMode.HTML)
                else:
                    context.bot.sendMessage(chat_id=sender_user.user_id, parse_mode=ParseMode.HTML, text=static_text.sent_tokens_receipt.format(recipient_username=recipient_username, transaction_id=tip["id"]))
        else:
            msg.edit_text(text=static_text.missing_token)
    except IndexError as e:
        msg.edit_text(text=static_text.sent_missing_parameters)
    except ValueError as e:
        if str(e) in ['Insufficient Waves balance', 'Insufficient asset balance']:
            msg.edit_text(text=static_text.missing_amount)
        elif str(e) == 'Amount must be > 0':
            msg.edit_text(text=static_text.negative_amount)
        else:
            msg.edit_text(text=static_text.missing_username.format(bot_name=context.bot.name)+static_text.sent_missing_parameters)

def withdraw(update: Update, context: CallbackContext) -> None:
    if(update.message.chat.type != "private"):
        msg = update.message.reply_text(text=static_text.processing)
    else:
        msg = context.bot.sendMessage(chat_id=update.message.chat_id, text=static_text.processing)
    try:
        recipient_address = context.args[0]
        amount = float(context.args[1])
        i = 0
        token_name = []
        for word in context.args:
            if (i > 1):
                token_name.append(word)
            i+=1
        token = " ".join(str(x) for x in token_name).strip().lower()
        send_tokens = {"send": False, "dcc": False}
        sender_user, _ = User.get_user(update, context)
        sender_address = pw.Address(seed = decrypt(sender_user.seed), pywaves = pw2)
        if(token == pw2.DEFAULT_CURRENCY.strip().lower()): # DCC
            dcc_balance = sender_address.balance() / math.pow(10, pw2.DCC_DECIMALS)
            if(dcc_balance >= amount):
                amount = int(amount * math.pow(10, pw2.DCC_DECIMALS))
                send_tokens["send"] = True
                send_tokens["dcc"] = True
            else:
                msg.edit_text(text=static_text.missing_amount)
        else: # Other coin
            sender_assets = sender_address.assets()
            if(sender_assets):
                for asset_id in sender_assets:
                    asset = pw.Asset(asset_id, pywaves = pw2)
                    asset_name = asset.name.decode('utf8').strip().lower()
                    if(token == asset_name):
                        asset_balance = sender_address.balance(asset_id) / int(math.pow(10, asset.decimals))
                        if(asset_balance >= amount):
                            amount = amount if asset.decimals == 0 else int(amount * math.pow(10, asset.decimals))
                            send_tokens["send"] = True                            
                        else:
                            msg.edit_text(text=static_text.missing_amount)
                    else:
                        msg.edit_text(text=static_text.missing_token)
            else:
                msg.edit_text(text=static_text.missing_token)
        #At this point we have determined which token is being send and if the user has the required amount
        if(send_tokens["send"] == True):
            recipient = pw.Address(recipient_address, pywaves=pw2)
            if(send_tokens["dcc"] == True): #DCC is being sent                
                withdraw = sender_address.sendWaves(recipient = recipient, amount = amount)
            else: #A different token is being sent
                withdraw = sender_address.sendAsset(recipient = recipient, asset = asset, amount = amount)
            if(update.message.chat.type != "private"):
                msg.edit_text(text=static_text.withdrawn_tokens.format(bot_name=context.bot.name))
                context.bot.sendMessage(chat_id=sender_user.user_id, parse_mode=ParseMode.HTML, text=static_text.withdrawn_tokens_receipt.format(transaction_id=withdraw["id"]))
            else:
                 msg.edit_text(text=static_text.withdrawn_tokens_receipt.format(transaction_id=withdraw["id"]), parse_mode=ParseMode.HTML)
    except IndexError as e:
        msg.edit_text(text=static_text.withdrawn_missing_parameters)
    except ValueError as e:
        if str(e) in ['Insufficient Waves balance', 'Insufficient asset balance']:
            msg.edit_text(text=static_text.missing_amount)
        elif str(e) == 'Amount must be > 0':
            msg.edit_text(text=static_text.negative_amount)
        else:
            msg.edit_text(text=static_text.withdrawn_missing_parameters)

def stats(update: Update, context: CallbackContext) -> None:
    text = static_text.stats.format(
        user_count=User.objects.count(),  # count may be ineffective if there are a lot of users.
        active_24=User.objects.filter(updated_at__gte=now() - timedelta(hours=24)).count()
    )
    context.bot.sendMessage(chat_id=update.message.chat_id, text=text)