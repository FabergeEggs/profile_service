from aiokafka import AIOKafkaProducer
import json
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any
from src.domain.interfaces import EventProducer
from src.core.config import settings

class KafkaEventProducer(EventProducer):
    def __init__(self):
        self.producer = None
    
    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.redpanda_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()
    
    async def stop(self):
        if self.producer:
            await self.producer.stop()
    
    async def send_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if not self.producer:
            raise RuntimeError("Producer not started")
        
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        await self.producer.send("profile_service.profile.changed", event)