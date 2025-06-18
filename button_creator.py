from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from models.models import Server, User, Subscription


def create_servers_button() -> InlineKeyboardMarkup:
    servers = Server.show_servers()
    keyboard = []
    for server in servers:
        keyboard.append([InlineKeyboardButton(text=str(server), callback_data=server.id)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup



def create_subscription_button(server_id) -> InlineKeyboardMarkup:
    subscriptions = Subscription.show_subscriptions_by_server_id(server_id=server_id)
    keyboard = []
    for subscription in subscriptions:
        keyboard.append([InlineKeyboardButton(text=subscription.plan, callback_data=subscription.id)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def create_clients_button(user_id) -> InlineKeyboardMarkup:
    user_clients = User.show_clients_for_userid(user_id)
    keyboard = []
    for client in user_clients.clients:
        keyboard.append([InlineKeyboardButton(text=client.email, callback_data=client.id)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
