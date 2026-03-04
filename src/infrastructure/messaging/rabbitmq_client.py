import os
import json
import aio_pika
from typing import Dict, Any
from src.infrastructure.utils.logs import app_log


class RabbitMQClient:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.user = os.getenv("RABBITMQ_USER", "radar")
        self.password = os.getenv("RABBITMQ_PASS", "radarapp2025")
        self.connection = None
        self.channel = None

    async def connect(self):
        """Establish connection to RabbitMQ"""
        url = f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"
        self.connection = await aio_pika.connect_robust(url)
        self.channel = await self.connection.channel()
        
        # Declare queues
        await self.channel.declare_queue("buyer_notifications", durable=True)
        await self.channel.declare_queue("seller_notifications", durable=True)
        
        app_log.info("RabbitMQ connection established")

    async def publish_buyer_notification(self, match_data: Dict[str, Any]):
        """Publish match notification for buyer"""
        await self._publish("buyer_notifications", match_data)

    async def publish_seller_notification(self, match_data: Dict[str, Any]):
        """Publish match notification for seller"""
        await self._publish("seller_notifications", match_data)

    async def _publish(self, queue_name: str, data: Dict[str, Any]):
        """Internal publish method"""
        if not self.channel:
            await self.connect()

        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=queue_name,
        )
        app_log.info(f"Published message to {queue_name}")

    async def consume_buyer_notifications(self, callback):
        """Consume buyer notifications"""
        await self._consume("buyer_notifications", callback)

    async def consume_seller_notifications(self, callback):
        """Consume seller notifications"""
        await self._consume("seller_notifications", callback)

    async def _consume(self, queue_name: str, callback):
        """Internal consume method"""
        if not self.channel:
            await self.connect()

        queue = await self.channel.declare_queue(queue_name, durable=True)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    await callback(data)

    async def close(self):
        """Close connection"""
        if self.connection:
            await self.connection.close()
            app_log.info("RabbitMQ connection closed")