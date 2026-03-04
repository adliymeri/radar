import asyncio
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.postgres import async_session
from src.infrastructure.repositories.postgres_match_repository import PostgresMatchRepository
from src.application.services.matching_service import MatchingService
from src.infrastructure.messaging.rabbitmq_client import RabbitMQClient
from src.infrastructure.utils.logs import setup_logging, app_log

setup_logging("daemon_logs")


async def run_matching_cycle():
    """Single matching cycle - finds matches and publishes to RabbitMQ"""
    app_log.info("Starting matching cycle")
    
    rabbitmq = RabbitMQClient()
    await rabbitmq.connect()

    async with async_session() as session:
        match_repo = PostgresMatchRepository(session)
        matching_service = MatchingService(session, match_repo)

        # Find all matches
        matches = await matching_service.find_matches()

        if not matches:
            app_log.info("No new matches found")
            await rabbitmq.close()
            return

        # Save matches to DB and publish notifications
        for match in matches:
            # Save match
            created_match = await matching_service.create_match(match)

            # Publish to RabbitMQ queues
            match_data = {
                "match_id": str(created_match.id),
                "buyer_id": str(created_match.buyer_id),
                "seller_id": str(created_match.seller_id),
                "listing_id": str(created_match.listing_id),
                "request_id": str(created_match.request_id),
            }

            await rabbitmq.publish_buyer_notification(match_data)
            await rabbitmq.publish_seller_notification(match_data)

        app_log.info(f"Published {len(matches)} matches to RabbitMQ")

    await rabbitmq.close()
    app_log.info("Matching cycle complete")


async def daemon_loop():
    """Main daemon loop"""
    interval_minutes = int(os.getenv("DAEMON_INTERVAL_MINUTES", "15"))
    app_log.info(f"Daemon started with {interval_minutes} minute interval")

    while True:
        try:
            await run_matching_cycle()
        except Exception as e:
            app_log.error(f"Error in matching cycle: {e}", exc_info=True)

        # Wait for next cycle
        app_log.info(f"Sleeping for {interval_minutes} minutes")
        await asyncio.sleep(interval_minutes * 60)


def main():
    try:
        asyncio.run(daemon_loop())
    except KeyboardInterrupt:
        app_log.info("Daemon stopped by user")


if __name__ == "__main__":
    main()