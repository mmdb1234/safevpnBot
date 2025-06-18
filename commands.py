from typing import Dict
import re
import segno
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, MenuButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import datetime
import jdatetime
from button_creator import create_subscription_button, create_servers_button, \
    create_clients_button
from handlers import CHOOSING, BUY_SERVER, MAKE_CONFIG, Go_FOR_PAYMENT, END, CHANGE_SERVER, CHOOSE_SERVER, \
    CHOOSE_SERVICE, EXTENSION_SERVER, EXTENSION_CLIENT
from models.models import User, Server, Subscription, Client

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat = update.message.from_user
    user1, create = User.get_or_create(username=user_chat.username, tel_id=user_chat.id)
    if create:
        user1.save()

    # اول کیبوردهای قبلی رو حذف می‌کنیم
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="♻️ در حال پاکسازی کیبوردهای قبلی...",
        reply_markup=ReplyKeyboardRemove()
    )

    # کیبورد جدید فقط با یک دکمه
    reply_keyboard = [
        ["استعلام حجم کانفیگ من"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"سلام {user_chat.first_name} عزیز 🌟\nیکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=markup
    )

    return CHOOSING

async def go_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    #just for get back to main conversation
    return CHOOSING


async def buy_service(update: Update, context: ContextTypes.DEFAULT_TYPE) :

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="لیست سرور ها به شرح  زیر است",
                                   reply_markup=create_servers_button())

    return BUY_SERVER


async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = create_subscription_button(int(update.callback_query.data))
    await update.callback_query.edit_message_text(
        text="یکی از اشتراک ها را انتخاب کنید"
    )
    await update.callback_query.edit_message_reply_markup(
                                    reply_markup=reply_markup
                                    )
    return Go_FOR_PAYMENT


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    user_clients = User.show_clients_for_userid(update.message.from_user.id)
    await update.message.reply_text(text="لیست سرویس های شما به شرح زیر است")
    if user_clients:
        for client in user_clients.clients:
            text = (f"\n"
                    f"شناسه  :{client.email}\n"
                    f"تاریخ انقضا :{client.expiryTime}\n"
                    f"حجم باقی مانده :{client.totalGB}\n"
                    f"نام سرور : {client.inbound.server}\n")
            await update.message.reply_text(text=text)
    else:
        await update.message.reply_text(text="شما هنوز سرویسی تهیه نکرده اید")
    return CHOOSING


async def extension_service(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    reply_markup = create_clients_button(update.message.from_user.id)

    await update.message.reply_text(
        text="برای تمدید روی یکی از سرویس های خود کلیک کنید", reply_markup=reply_markup
    )

    return EXTENSION_SERVER


async def extension_client(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    payment = True
    client = Client.get_by_id(update.callback_query.data)
    if payment:
        success , message = client.extension_client()
        if success:
            await update.callback_query.message.reply_text(
                text="کانفیگ شما با موفقیت تمدید شد" )
            url, photo = client.get_url_qrcode()
            await update.callback_query.message.reply_text(text=url)
            await context.bot.send_photo(update.effective_chat.id, photo="basic_qrcode.png")
        else:
            await update.callback_query.message.reply_text(
                text="مشکلی در تمدید شما وجود دارد با پشتیبانی تماس برقرار کنید")
    else:
        await update.callback_query.message.reply_text(
            text="پرداخت شما موفق نبود دوباره امتحان کنید")

    return CHOOSING


async def config_maker(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    reply_markup = create_clients_button(update.message.from_user.id)

    await update.message.reply_text(
        text="برای ایجاد کانفیگ روی یکی از سرویس های خود کلیک کنید", reply_markup=reply_markup
    )

    return MAKE_CONFIG

async def show_config(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    client = Client.get_by_id(pk=update.callback_query.data)
    url , photo = client.get_url_qrcode()
    await update.callback_query.message.reply_text(text=url)
    await context.bot.send_photo(update.effective_chat.id, photo="basic_qrcode.png")

    return CHOOSING


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tel_id = update.message.from_user.id
    wallet_value = User.get(User.tel_id == user_tel_id).inventory
    keyboard = [[InlineKeyboardButton(text="افزایش موجودی", callback_data=user_tel_id)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=f"موجودی کیف پول شما {wallet_value} تومان است برای افزایش موجودی دکمه زیر را بزنید ", reply_markup=reply_markup
    )
    return CHOOSING



async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = create_clients_button(update.message.from_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id,
        text="برای تغییر کانفیگ روی یکی از سرویس های خود کلیک کنید", reply_markup=reply_markup
    )
    return CHOOSE_SERVICE

async def choose_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = create_servers_button()
    context.bot_data["client"] = Client.get_by_id(update.callback_query.data)
    await update.callback_query.edit_message_text(
        text="سروری که میخواهید به آن تغییر پیدا کند را انتخاب کنید", reply_markup=reply_markup
    )
    return CHANGE_SERVER

async def change_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = context.bot_data["client"]
    server = Server.get_by_id(update.callback_query.data)
    inbound = client.inbound
    last_server = inbound.server
    success , message, new_client = server.change_server_inbound_client(inbound=inbound, client=client, server=last_server)
    if success:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="سرور کانفیگ شما با موفقیت تغییر کرد"
                                       )
        url, photo = new_client.get_url_qrcode()
        await update.callback_query.message.reply_text(text=url)
        await context.bot.send_photo(update.effective_chat.id, photo="basic_qrcode.png")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="مشکلی در تغییر سرویس به این سرور وجود دارد از سرور دیگری استفاده نمایید"
                                       )
    return CHOOSING


async def contact_with_us(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(f"راه های ارتباط با ما \n کانال تلگرام \n  ادمین ربات")
    return CHOOSING

async def info_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass


async def help_for_connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pass

async def get_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text("لطفا لینک کانفیگ خود را ارسال کنید ")
    return CHOOSING

async def handle_vless_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    uuid, domain = extract_uuid_and_domain(link)

    if not uuid or not domain:
        await update.message.reply_text("❌ لینک نامعتبر است. لطفاً دوباره امتحان کنید.")
        return CHOOSING

    try:
        server = Server.select().where(Server.server_address == domain).first()
        if not server:
            await update.message.reply_text("❌ سروری با این دامنه یافت نشد.")
            return CHOOSING

        api_result = server.get_value_user_server(uuid=uuid)

        if api_result:
            message = calculate_remaining_traffic({"obj": [api_result]})
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ کاربر یافت نشد یا اطلاعات ناقص است.")

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در پردازش: {e}")

    return CHOOSING

def extract_uuid_and_domain(vless_link: str):
    
    match = re.match(r"vless://([a-fA-F0-9\-]+)@([\w\.\-]+):\d+", vless_link)
    if match:
        uuid = match.group(1)
        domain = match.group(2)
        return uuid, domain
    return None, None

def bytes_to_gb(b):
        return round(b / (1024**3), 2)

def timestamp_to_persian(timestamp_ms):
    """تبدیل timestamp میلی‌ثانیه به تاریخ شمسی"""
    timestamp_seconds = timestamp_ms / 1000
    persian_date = jdatetime.datetime.fromtimestamp(timestamp_seconds)
    return persian_date.strftime('%Y/%m/%d %H:%M:%S')   
 
def calculate_remaining_traffic(data: dict) -> str:
        client = data["obj"][0]
        used = client["up"] + client["down"]
        total = client["total"]
        expiretime = client["expiryTime"]
        remaining = max(total - used, 0)
        return f"""
            🧾 نام کاربری: {client['email']}
            ⬆️ آپلود: {bytes_to_gb(client['up'])} GB
            ⬇️ دانلود: {bytes_to_gb(client['down'])} GB
            📦 حجم کل: {bytes_to_gb(total)} GB
            💾 حجم باقی‌مانده: {bytes_to_gb(remaining)} GB
            💾 تاریخ انقضا: {timestamp_to_persian(expiretime)}
        """    
