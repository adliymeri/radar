import asyncio
import os
from uuid import UUID
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.postgres import async_session
from src.infrastructure.repositories.postgres_buyer_repository import PostgresBuyerRepository
from src.infrastructure.repositories.postgres_seller_repository import PostgresSellerRepository
from src.infrastructure.repositories.postgres_listing_repository import PostgresListingRepository
from src.infrastructure.repositories.postgres_car_listing_repository import PostgresCarListingRepository
from src.infrastructure.messaging.rabbitmq_client import RabbitMQClient
from src.infrastructure.utils.logs import setup_logging, app_log

setup_logging("notification_consumer_logs")

# Telegram rate limiting
RATE_LIMIT_DELAY = 0.034  # ~30 messages/second


async def send_buyer_notification(data: dict):
    """Send match notification to buyer"""
    app_log.info(f"Processing buyer notification: {data['match_id']}")

    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

    async with async_session() as session:
        buyer_repo = PostgresBuyerRepository(session)
        listing_repo = PostgresListingRepository(session)
        car_listing_repo = PostgresCarListingRepository(session)

        # Fetch data
        buyer = await buyer_repo.get_buyer_by_id(UUID(data["buyer_id"]))
        listing = await listing_repo.get_listing_by_id(UUID(data["listing_id"]))
        car_listing = await car_listing_repo.get_car_listing_by_id(UUID(data["listing_id"]))

        if not buyer or not listing or not car_listing:
            app_log.error(f"Missing data for match {data['match_id']}")
            return

        chat_id = buyer.details["chat_id"]

        # Build message
        message = (
            f"🎉 New Match Found!\n\n"
            f"🚗 {car_listing.make} {car_listing.model} ({car_listing.year})\n"
            f"💶 €{car_listing.price:,.0f}\n"
            f"🛣 {car_listing.mileage:,} km\n"
            f"⚙️ {car_listing.transmission} | {car_listing.fuel_type} | {car_listing.drivetrain}\n"
            f"📍 {car_listing.location or 'Location not specified'}\n"
        )

        if car_listing.description:
            # Truncate if too long
            desc = car_listing.description[:200] + "..." if len(car_listing.description) > 200 else car_listing.description
            message += f"\n📝 {desc}\n"

        # Inline button to contact seller
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Contact Seller", callback_data=f"contact_seller:{data['match_id']}")]
        ])

        # Send message
        await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)

        # Send photos if available
        if car_listing.photos and len(car_listing.photos) > 0:
            media_group = [InputMediaPhoto(photo_id) for photo_id in car_listing.photos[:10]]  # Max 10
            await bot.send_media_group(chat_id=chat_id, media=media_group)

        app_log.info(f"Buyer notification sent for match {data['match_id']}")

    # Rate limiting
    await asyncio.sleep(RATE_LIMIT_DELAY)


async def send_seller_notification(data: dict):
    """Send interest notification to seller"""
    app_log.info(f"Processing seller notification: {data['match_id']}")

    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

    async with async_session() as session:
        seller_repo = PostgresSellerRepository(session)
        car_listing_repo = PostgresCarListingRepository(session)

        seller = await seller_repo.get_seller_by_id(UUID(data["seller_id"]))
        car_listing = await car_listing_repo.get_car_listing_by_id(UUID(data["listing_id"]))

        if not seller or not car_listing:
            app_log.error(f"Missing data for match {data['match_id']}")
            return

        chat_id = seller.details["chat_id"]

        message = (
            f"👀 Interest in Your Listing!\n\n"
            f"Someone is interested in your:\n"
            f"🚗 {car_listing.make} {car_listing.model} ({car_listing.year})\n\n"
            f"They may contact you soon!"
        )

        await bot.send_message(chat_id=chat_id, text=message)
        app_log.info(f"Seller notification sent for match {data['match_id']}")

    # Rate limiting
    await asyncio.sleep(RATE_LIMIT_DELAY)


async def main():
    rabbitmq = RabbitMQClient()
    await rabbitmq.connect()

    app_log.info("Notification consumer started")

    # Start both consumers concurrently
    await asyncio.gather(
        rabbitmq.consume_buyer_notifications(send_buyer_notification),
        rabbitmq.consume_seller_notifications(send_seller_notification),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        app_log.info("Consumer stopped by user")