#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
from enum import Flag
import logging,config,requests
import time
from urllib import request
from database import Database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

from database import Database

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND, THIRD = range(3)
# Callback data
ONE, TWO, THREE, FOUR = range(4)


def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸", callback_data=str(187)),
            InlineKeyboardButton("🇮🇩", callback_data=str(6)),
            InlineKeyboardButton("🇷🇺", callback_data=str(0)),
            InlineKeyboardButton("🇨🇦", callback_data=str(36)),
            InlineKeyboardButton("🇬🇧", callback_data=str(16)),
            InlineKeyboardButton("🇩🇪", callback_data=str(43)),
            InlineKeyboardButton("🇹🇭", callback_data=str(52)),
            InlineKeyboardButton("🇹🇷", callback_data=str(62)),
        ],
        [
            InlineKeyboardButton("🇦🇪", callback_data=str(95)),
            InlineKeyboardButton("🇮🇳", callback_data=str(22)),
            InlineKeyboardButton("🇳🇱", callback_data=str(48)),
            InlineKeyboardButton("🇫🇷", callback_data=str(78)),
            InlineKeyboardButton("🇮🇹🍕", callback_data=str(86)),
            InlineKeyboardButton("🇪🇸", callback_data=str(56)),
            InlineKeyboardButton("🇲🇽🌮", callback_data=str(54)),
            InlineKeyboardButton("🇸🇻₿", callback_data=str(62)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Hi! Please choose a country:", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST
def refund(update: Update, context: CallbackContext):
    try:
        payment_hash = context.args[0]
        check_payment = requests.get("https://legend.lnbits.com/api/v1/payments/"+str(payment_hash), headers = {"X-Api-Key": config.APIKEY_LN,"Content-type": "application/json"}).json()
        sms_id = Database().get_sms_by_hash(payment_hash)
        amount = sms_id[1]
        if check_payment["paid"] == True and sms_id[2]:
            get_status = requests.get("http://api.sms-man.com/stubs/handler_api.php?action=getStatus&api_key="+config.APIKEY_SMS+"&id="+str(sms_id[0])).text
            if "STATUS_OK" in get_status:
                update.effective_message.reply_text("You have the code already! code:" + get_status.split(":")[1])
            else:
                set_status = requests.get("http://api.sms-man.com/stubs/handler_api.php?action=setStatus&api_key="+config.APIKEY_SMS+"&id="+str(sms_id[0])+"&status=-1")
                lnurlw = requests.post("https://legend.lnbits.com/withdraw/api/v1/links", data = '{"title": "refund'+str(update.effective_message.message_id)+'", "min_withdrawable": '+str(amount)+', "max_withdrawable": '+str(amount)+', "uses": 1, "wait_time": 1, "is_unique": true}', headers = {"X-Api-Key": config.APIKEY_LN_ADMIN,"Content-type": "application/json"}).json()
                update.effective_message.reply_text("Here is your lnurl withdraw:\n `"+lnurlw["lnurl"]+"`", parse_mode= ParseMode.MARKDOWN)
                Database().set_ispaid(False, payment_hash)
        else:
            update.effective_message.reply_text("This invoice has not been paid.")
    except:
        update.effective_message.reply_text("Please use the command like this: \n/refund <payment hash>")


def start_over(update: Update, context: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
    return FIRST


def select_service(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Telegram", callback_data=query.data+"-tg"),
            InlineKeyboardButton("Instagram", callback_data=query.data+"-ig"),
            InlineKeyboardButton("Whatsapp", callback_data=query.data+"-wa"),
            InlineKeyboardButton("Twitter", callback_data=query.data+"-tw"),
        ],
        [
            InlineKeyboardButton("WeChat", callback_data=query.data+"-wb"),
            InlineKeyboardButton("Viber", callback_data=query.data+"-vi"),
            InlineKeyboardButton("Facebook", callback_data=query.data+"-fb"),
            InlineKeyboardButton("Discord", callback_data=query.data+"-ds"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Please choose a service:", reply_markup=reply_markup
    )
    return SECOND


def create_payment(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    data = query.data.split("-")
    price = requests.get("http://api.sms-man.com/stubs/handler_api.php?action=getPrices&api_key="+config.APIKEY_SMS+"&country="+data[0]+"&service="+data[1]).json()
    if price[data[1]]["count"] > 0: 
        sat_to_rub = config.SAT_RUB
        cost = int(float(price[data[1]]["cost"])/sat_to_rub) + 100
        invoice = requests.post("https://legend.lnbits.com/api/v1/payments", data = '{"out": false,"amount":'+str(cost)+', "webhook":"'+config.WEBHOOK+query.id+'"}', headers = {"X-Api-Key": config.APIKEY_LN,"Content-type": "application/json"}).json()
        query.edit_message_text(
            text="Please pay this invoice for "+str(cost)+"sats : `"+invoice["payment_request"] +"`"
                "\n\n or start over /start" 
            ,parse_mode=ParseMode.MARKDOWN
        )
        Database().add_user(query.id, query.message.message_id, query.from_user.id, 0,invoice["payment_hash"],invoice["payment_request"],cost,False,time.time(),data[1],data[0])
    else:
        query.edit_message_text(
            text="This service for This country is not available for now!" +
                "\n\n start over /start"
        )
    return THIRD


def show_code(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    #query.answer()
    sms_id = Database().get_sms(query.from_user.id, query.message.message_id)
    print(str(sms_id))
    code = requests.get("http://api.sms-man.com/stubs/handler_api.php?action=getStatus&api_key="+config.APIKEY_SMS+"&id="+str(sms_id)).text
    if "STATUS_WAIT_CODE" in code:
        query.answer("sms not yet received!", show_alert = True)
    elif "STATUS_OK" in code:
        query.answer()
        query.edit_message_text(
        text="Here is your code: "+str(code.split(":")[1])
        )
        Database().set_ispaid2(False, query.from_user.id, query.message.message_id)
    elif "STATUS_CANCEL" in code:
        query.answer()
        amount = Database().get_cost2(query.from_user.id, query.message.message_id)
        lnurlw = requests.post("https://legend.lnbits.com/withdraw/api/v1/links", data = '{"title": "'+query.id+'", "min_withdrawable": '+str(amount)+', "max_withdrawable": '+str(amount)+', "uses": 1, "wait_time": 1, "is_unique": true}', headers = {"X-Api-Key": config.APIKEY_LN_ADMIN,"Content-type": "application/json"}).json()
        query.edit_message_text(text= "Sorry something went wrong here is your lnurl withdraw:\n`"+lnurlw["lnurl"]+"`", parse_mode = ParseMode.MARKDOWN )


    # Transfer to conversation state `SECOND`
    return THIRD


def four(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("2", callback_data=str(TWO)),
            InlineKeyboardButton("3", callback_data=str(THREE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Fourth CallbackQueryHandler, Choose a route", reply_markup=reply_markup
    )
    return FIRST


def end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(select_service, pattern='\d'),
                #CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                #CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
            ],
            SECOND: [
                CallbackQueryHandler(create_payment, pattern='\d'),
                #CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
                #CallbackQueryHandler(end, pattern='^' + str(TWO) + '$'),
            ],
            THIRD:[
                CallbackQueryHandler(show_code, pattern='^check_sms$'),

            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('refund', refund))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
