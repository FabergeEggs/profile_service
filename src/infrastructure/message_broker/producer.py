from aiokafka import AIOKafkaProducer
import json
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from src.domain.interfaces import EventProducer
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

_event_producer: Optional["KafkaEventProducer"] = None


def get_event_producer() -> "KafkaEventProducer":
    global _event_producer
    if _event_producer is None:
        _event_producer = KafkaEventProducer()
    return _event_producer


class KafkaEventProducer(EventProducer):
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self._started = False

    async def start(self):
        for i in range(10):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.redpanda_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode(),
                )
                await self.producer.start()
                self._started = True
                logger.info("Kafka producer started (attempt %s)", i + 1)
                return
            except Exception as e:
                logger.warning("Waiting for Kafka (%s/10): %s", i + 1, e)
                await asyncio.sleep(3)
        logger.error("Kafka unavailable, continuing without producer")
        self._started = False

    async def stop(self):
        if self.producer and self._started:
            await self.producer.stop()
            self._started = False

    async def send_event(
        self,
        *,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:
        if not self._started or self.producer is None:
            logger.warning("Producer not started, skipping event")
            return

        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data,
        }
        await self.producer.send_and_wait(topic, event)
