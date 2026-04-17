# src/infrastructure/message_broker/producer.py
from aiokafka import AIOKafkaProducer
import json
import asyncio
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any
from src.domain.interfaces import EventProducer
from src.core.config import settings

class KafkaEventProducer(EventProducer):
    def __init__(self):
        self.producer = None
        self._started = False
    
    async def start(self):
        for i in range(10):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.redpanda_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode()
                )
                await self.producer.start()
                self._started = True
                print(f"Kafka producer started (attempt {i+1})")
                return
            except Exception as e:
                print(f"⏳ Waiting for Kafka... ({i+1}/10): {e}")
                await asyncio.sleep(3)
        print("Kafka unavailable, continuing without producer")
        self._started = False
    
    async def stop(self):
        if self.producer and self._started:
            await self.producer.stop()
    
    async def send_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if not self._started:
            print(f"Producer not started, skipping event")
            return  # НЕ падать!
        
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        await self.producer.send("profile_service.profile.changed", event)