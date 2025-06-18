from datetime import datetime, timedelta

import segno
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from Api.sanaii_api import add_inbound, add_client_to_inbound
from commands import CHOOSING, END
from db.db_config import db
from models.models import User, Subscription, Transaction, Inbound, Client


def charge_wallet(user_id, amount):
    pass


async def purchase_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    subscription_id = int(update.callback_query.data)
    subscription = Subscription.get_by_id(subscription_id)
    user = User.get(tel_id=update.callback_query.from_user.id)
    if True:
        success , message , cliente = Client.create_inbound_client(subscription, user)
        if success :
                url, qr = cliente.get_url_qrcode()
                await update.callback_query.message.reply_text(text=url)
                await context.bot.send_photo(update.effective_chat.id, photo="basic_qrcode.png")

        else:
            await update.callback_query.message.reply_text(
                text="مشکلی در برنامه پیش آمده است لطفا با پشتیبانی ارتباط حاصل فرمایید")
    return CHOOSING


def buy_subscription_by_charge(subscription_id, user_id):
        user = User.get_by_id(user_id)
        subscription = Subscription.get_by_id(subscription_id)
        if user.inventory < subscription.amount:
            return False
        else:
            with db.atomic() as txn:
                try:
                    transaction = Transaction.create(user=user_id, amount=subscription.amount, status=Transaction.MINES_CHARGE)
                    transaction.save()
                    return True
                except :
                    db.rollback()
                    return False


