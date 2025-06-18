
from telegram.ext import MessageHandler, filters, CallbackQueryHandler, ConversationHandler, CommandHandler

TYPING_REPL, END,GET_BACK = range(3)
CHOOSING = "CHOOSING"
BUY_SERVER = "BUY_SERVER"
MAKE_CONFIG = "MAKE_CONFIG"
Go_FOR_PAYMENT = "Go_FOR_PAYMENT"
CHANGE_SERVER = "CHANGE_SERVER"
CHOOSE_SERVER = "CHOOSE_SERVER"
CHOOSE_SERVICE = "CHOOSE_SERVICE"
EXTENSION_SERVER = "EXTENSION_SERVER"
EXTENSION_CLIENT = "EXTENSION_CLIENT",
CHECK_USAGE = "CHECK_USAGE"

from commands import contact_with_us, extension_service, config_maker, wallet, info_show, \
    help_for_connect, show_services, buy_service, start, buy_subscription, show_config, \
    go_to_main_menu, choose_service, choose_server, change_server, extension_client,get_value,handle_vless_link
from patment.payment_action import purchase_subscription

start_command = CommandHandler("start", start)
main_menu_handler = [
    start_command,
    MessageHandler(filters.Regex("^استعلام حجم کانفیگ من$"), get_value, ),
    MessageHandler(filters.Regex("vless://([a-fA-F0-9\-]+)@([\w\.\-]+):\d+"), handle_vless_link, ),
    #MessageHandler(filters.Regex("^تماس با ما$"), contact_with_us, ),
    #MessageHandler(filters.Regex("^تمدید سرویس$"), extension_service, ),
    #MessageHandler(filters.Regex("^تغییر سرورها$"), choose_service, ),
    #MessageHandler(filters.Regex("^کیف پول$"), wallet, ),
    #MessageHandler(filters.Regex("^تعرفه ها$"), info_show, ),
    #MessageHandler(filters.Regex("^راهنما$"), help_for_connect, ),
    #MessageHandler(filters.Regex("^سرور های من$"), show_services, ),
    #MessageHandler(filters.Regex("^خرید سرویس$"), buy_service, ),
    #MessageHandler(filters.Regex("^دریافت کانفیگ$"), config_maker, ),

]

buy_service_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(buy_subscription, pattern='^[0-9]*$')],
        states={
            BUY_SERVER: [CallbackQueryHandler(buy_subscription, pattern='^[0-9]*$')],
            Go_FOR_PAYMENT: [CallbackQueryHandler(purchase_subscription, pattern='^[0-9]*$')],
        },
        fallbacks=[CommandHandler("go_to_main_menu",go_to_main_menu)],
        map_to_parent={
            CHOOSING:CHOOSING
        }
    )

make_service_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_config, pattern='^[0-9]*$')],
        states={
            MAKE_CONFIG: [CallbackQueryHandler(show_config, pattern='^[0-9]*$')],
        },
        fallbacks=[CommandHandler("go_to_main_menu",go_to_main_menu)],
        map_to_parent={
            CHOOSING:CHOOSING
        }
    )

change_service_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(choose_server, pattern='^[0-9]*$')],
        states={
            CHOOSE_SERVICE: [CallbackQueryHandler(choose_service, pattern='^[0-9]*$')],
            CHOOSE_SERVER: [CallbackQueryHandler(choose_server, pattern='^[0-9]*$')],
            CHANGE_SERVER: [CallbackQueryHandler(change_server, pattern='^[0-9]*$')],

        },
        fallbacks=[CommandHandler("go_to_main_menu",go_to_main_menu)],
        map_to_parent={
            CHOOSING:CHOOSING
        }
    )


extension_service_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(extension_client, pattern='^[0-9]*$')],
        states={
            EXTENSION_SERVER:[CallbackQueryHandler(extension_client, pattern='^[0-9]*$')]
        },
        fallbacks=[CommandHandler("go_to_main_menu",go_to_main_menu)],
        map_to_parent={
            CHOOSING:CHOOSING
        }
)


main_conversation_handler = ConversationHandler(
        entry_points=main_menu_handler,
        states={
            CHOOSING: main_menu_handler,
            BUY_SERVER:[buy_service_handler],
            MAKE_CONFIG:[make_service_handler],
            CHOOSE_SERVICE:[change_service_handler],
            EXTENSION_SERVER: [extension_service_handler],

        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
)