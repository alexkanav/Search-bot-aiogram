import json
from collections.abc import Awaitable, Callable
from typing import Any

import aio_pika


class RabbitMQ:
    def __init__(self, url: str) -> None:
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()

    async def consume(
            self,
            queue: str,
            callback: Callable[..., Awaitable[None]],
            *args: Any,
            **kwargs: Any,
    ) -> str:
        q = await self.channel.declare_queue(queue, durable=True)

        async def handler(message: aio_pika.IncomingMessage):
            async with message.process():
                await callback(message, *args, **kwargs)

        consumer_tag = await q.consume(handler)
        return consumer_tag

    async def publish(
            self,
            queue: str,
            body: dict,
    ) -> None:
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue,
        )

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None
            self.channel = None
