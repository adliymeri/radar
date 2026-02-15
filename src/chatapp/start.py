import asyncio
import os
from telegram.ext import ApplicationBuilder
from src.chatapp.handlers.buyer.buyer_profile_handler import get_buyer_profile_handler
from src.chatapp.handlers.seller.seller_car_listing_handler import get_seller_car_listing_conv
from src.chatapp.handlers.registration_handler import get_registration_conv
from src.chatapp.handlers.buyer.buyer_car_request_handler import get_car_request_conv
from src.infrastructure.db.postgres import shutdown_db
from src.infrastructure.utils.logs import setup_logging, app_log

setup_logging("chat_logs")


def main():
    app_log.info("Starting Telegram Bot...")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        app_log.critical("Missing TELEGRAM_BOT_TOKEN!")
        return

    application = ApplicationBuilder().token(token).build()

    application.add_handler(get_registration_conv())
    application.add_handler(get_car_request_conv())
    application.add_handler(get_seller_car_listing_conv())
    
    for handler in get_buyer_profile_handler():
        application.add_handler(handler)

    try:
        application.run_polling()
    except (KeyboardInterrupt, SystemExit):
        app_log.info("Bot interrupted by user.")
    finally:
        app_log.info("Bot offline.")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(shutdown_db())
        app_log.info("Database connections closed.")
        loop.close()


if __name__ == "__main__":
    main()
