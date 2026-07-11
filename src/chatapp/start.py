import os
from telegram.ext import ApplicationBuilder, PicklePersistence, MessageHandler, CommandHandler, filters
from src.chatapp.handlers.switch_role_handler import get_switch_role_handlers
from src.chatapp.handlers.seller.seller_real_estate_listing_handler import get_seller_real_estate_listing_conv
from src.chatapp.handlers.fallback_handler import handle_lost_user
from src.chatapp.handlers.buyer.buyer_real_estate_handler import get_real_estate_request_conv
from src.chatapp.handlers.help_handler import get_help_handler
from src.chatapp.handlers.seller.seller_settings_handler import get_seller_settings_conv
from src.chatapp.handlers.seller.seller_listings_handler import get_seller_listings_handler
from src.chatapp.handlers.buyer.pause_resume_handler import get_pause_resume_handlers
from src.chatapp.handlers.buyer.contact_seller_handler import get_contact_seller_handler
from src.chatapp.handlers.buyer.buyer_profile_handler import get_buyer_profile_handler
from src.chatapp.handlers.seller.seller_car_listing_handler import get_seller_car_listing_conv
from src.chatapp.handlers.registration_handler import get_registration_conv
from src.chatapp.handlers.buyer.buyer_car_request_handler import get_car_request_conv
from src.infrastructure.utils.logs import setup_logging, app_log

setup_logging("chat_logs")


def main():
    app_log.info("Starting Telegram Bot...")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        app_log.critical("Missing TELEGRAM_BOT_TOKEN!")
        return

    persistence = PicklePersistence(filepath="bot_data.pickle")
    application = ApplicationBuilder().token(token).persistence(persistence).build()

    application.add_handler(get_registration_conv())
    application.add_handler(get_car_request_conv())
    application.add_handler(get_seller_car_listing_conv())
    application.add_handler(get_contact_seller_handler())
    application.add_handler(get_seller_settings_conv())
    application.add_handler(get_help_handler())
    application.add_handler(get_real_estate_request_conv())
    application.add_handler(get_seller_real_estate_listing_conv())

    
    for handler in get_buyer_profile_handler():
        application.add_handler(handler)

    for handler in get_pause_resume_handlers():
        application.add_handler(handler)

    for handler in get_seller_listings_handler():
        application.add_handler(handler)
    
    for handler in get_switch_role_handlers():
        application.add_handler(handler)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_lost_user))

    try:
        application.run_polling()
    except (KeyboardInterrupt, SystemExit):
        app_log.info("Bot interrupted by user.")
    finally:
        app_log.info("Bot offline.")
        
if __name__ == "__main__":
    main()
