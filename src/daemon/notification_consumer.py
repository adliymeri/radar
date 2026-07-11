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
from src.infrastructure.repositories.postgres_real_estate_listing_repository import PostgresRealEstateListingRepository
from src.infrastructure.messaging.rabbitmq_client import RabbitMQClient
from src.infrastructure.utils.logs import setup_logging, app_log

setup_logging("notification_consumer_logs")

RATE_LIMIT_DELAY = 0.034


async def send_buyer_notification(data: dict):
    """Send match notification to buyer"""
    app_log.info(f"Processing buyer notification: {data['match_id']}")

    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

    async with async_session() as session:
        buyer_repo = PostgresBuyerRepository(session)
        listing_repo = PostgresListingRepository(session)
        car_listing_repo = PostgresCarListingRepository(session)
        real_estate_listing_repo = PostgresRealEstateListingRepository(session)

        buyer = await buyer_repo.get_buyer_by_id(UUID(data["buyer_id"]))
        listing = await listing_repo.get_listing_by_id(UUID(data["listing_id"]))

        if not buyer or not listing:
            app_log.error(f"Missing data for match {data['match_id']}")
            return

        chat_id = buyer.details["chat_id"]

        if listing.type == "car":
            car_listing = await car_listing_repo.get_car_listing_by_id(UUID(data["listing_id"]))
            if not car_listing:
                app_log.error(f"Missing car listing for match {data['match_id']}")
                return

            message_lines = [
                "🎉 New Match Found!\n",
                f"🚗 {car_listing.make} {car_listing.model} ({car_listing.year})",
                f"💶 €{car_listing.price:,.0f}" if car_listing.price else "💶 Price: N/A",
                f"🛣 {car_listing.mileage:,} km" if car_listing.mileage else "🛣 Mileage: N/A",
                f"📍 {car_listing.location or 'Location not specified'}",
                f"⚙️ {car_listing.transmission or 'N/A'} | {car_listing.fuel_type or 'N/A'} | {car_listing.drivetrain or 'N/A'}",
                f"🎨 Color: {', '.join(car_listing.color) if car_listing.color else 'N/A'}",
            ]

            if car_listing.description:
                desc = car_listing.description[:300] + "..." if len(car_listing.description) > 300 else car_listing.description
                message_lines.append(f"📝 {desc}")

            if car_listing.link:
                message_lines.append(f"🔗 {car_listing.link}")

            photos = car_listing.photos

        elif listing.type == "real_estate":
            re_listing = await real_estate_listing_repo.get_listing_by_id(UUID(data["listing_id"]))
            if not re_listing:
                app_log.error(f"Missing real estate listing for match {data['match_id']}")
                return

            features = []
            if re_listing.parking:
                features.append("🅿️ Parking")
            if re_listing.elevator:
                features.append("🛗 Elevator")
            if re_listing.furnished:
                features.append("🛋 Furnished")
            if re_listing.balcony:
                features.append("🏞 Balcony")

            message_lines = [
                "🎉 New Match Found!\n",
                f"🏠 {re_listing.property_type} — {re_listing.listing_type}",
                f"🏗 {re_listing.condition}",
                f"📍 {re_listing.district}, {re_listing.city}",
                f"📫 {re_listing.address}",
                f"💶 €{re_listing.price:,.0f}",
                f"📐 {re_listing.area:.0f} m²",
                f"🛏 {re_listing.bedrooms} bedrooms | 🚿 {re_listing.bathrooms} bathrooms",
                f"🏢 Floor {re_listing.floor}",
            ]

            if features:
                message_lines.append(f"✅ {', '.join(features)}")

            if re_listing.description:
                desc = re_listing.description[:300] + "..." if len(re_listing.description) > 300 else re_listing.description
                message_lines.append(f"📝 {desc}")

            if re_listing.link:
                message_lines.append(f"🔗 {re_listing.link}")

            photos = re_listing.photos

        else:
            app_log.error(f"Unknown listing type for match {data['match_id']}")
            return

        message = "\n".join(message_lines)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Contact Seller", callback_data=f"contact_seller:{data['match_id']}")]
        ])

        # Send photos first, then details
        if photos and len(photos) > 0:
            try:
                if len(photos) == 1:
                    await bot.send_photo(chat_id=chat_id, photo=photos[0])
                else:
                    media_group = [InputMediaPhoto(photo_id) for photo_id in photos[:10]]
                    await bot.send_media_group(chat_id=chat_id, media=media_group)
            except Exception as e:
                app_log.error(f"Error sending photos: {e}")

        await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)

        app_log.info(f"Buyer notification sent for match {data['match_id']}")

    await asyncio.sleep(RATE_LIMIT_DELAY)


async def send_seller_notification(data: dict):
    """Send interest notification to seller"""
    app_log.info(f"Processing seller notification: {data['match_id']}")

    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

    async with async_session() as session:
        seller_repo = PostgresSellerRepository(session)
        listing_repo = PostgresListingRepository(session)
        car_listing_repo = PostgresCarListingRepository(session)
        real_estate_listing_repo = PostgresRealEstateListingRepository(session)

        seller = await seller_repo.get_seller_by_id(UUID(data["seller_id"]))
        listing = await listing_repo.get_listing_by_id(UUID(data["listing_id"]))

        if not seller or not listing:
            app_log.error(f"Missing data for match {data['match_id']}")
            return

        chat_id = seller.details["chat_id"]

        if listing.type == "car":
            car_listing = await car_listing_repo.get_car_listing_by_id(UUID(data["listing_id"]))
            if not car_listing:
                return
            message = (
                f"👀 Interest in Your Listing!\n\n"
                f"Someone is interested in your:\n"
                f"🚗 {car_listing.make} {car_listing.model} ({car_listing.year})\n\n"
                f"They may contact you soon!"
            )

        elif listing.type == "real_estate":
            re_listing = await real_estate_listing_repo.get_listing_by_id(UUID(data["listing_id"]))
            if not re_listing:
                return
            message = (
                f"👀 Interest in Your Listing!\n\n"
                f"Someone is interested in your:\n"
                f"🏠 {re_listing.property_type} in {re_listing.district}, {re_listing.city}\n"
                f"💶 €{re_listing.price:,.0f}\n\n"
                f"They may contact you soon!"
            )

        else:
            return

        await bot.send_message(chat_id=chat_id, text=message)
        app_log.info(f"Seller notification sent for match {data['match_id']}")

    await asyncio.sleep(RATE_LIMIT_DELAY)


async def main():
    rabbitmq = RabbitMQClient()
    await rabbitmq.connect()

    app_log.info("Notification consumer started")

    await asyncio.gather(
        rabbitmq.consume_buyer_notifications(send_buyer_notification),
        rabbitmq.consume_seller_notifications(send_seller_notification),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        app_log.info("Consumer stopped by user")