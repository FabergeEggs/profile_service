"""Base message broker consumer utility"""

from aiokafka import AIOKafkaConsumer
import json
from typing import Callable, Awaitable, Dict, Any
import asyncio
from src.core.config import settings  

class KafkaConsumer:
    """Generic Kafka consumer wrapper (infrastructure utility)"""
    
    def __init__(self, topic: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        self.topic = topic
        self.handler = handler
        self.consumer: AIOKafkaConsumer = None  
        self._running = False
    
    async def start(self):
        """Start consuming messages"""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.redpanda_bootstrap_servers,  # Исправлено: settings (объект), не Settings (класс)
            group_id=settings.redpanda_consumer_group,              # Исправлено: settings (объект)
            value_deserializer=lambda v: json.loads(v.decode()),
            auto_offset_reset="earliest",
            enable_auto_commit=False  
        )
        await self.consumer.start()
        self._running = True
        
        # Start consumption loop
        asyncio.create_task(self._consume())
        print(f"Started consumer for topic: {self.topic}")
    
    async def _consume(self):
        """Main consumption loop"""
        try:
            async for msg in self.consumer:
                if not self._running:
                    break
                try:
                    await self.handler(msg.value)
                    await self.consumer.commit()
                except Exception as e:
                    print(f"Error handling message: {e}")
        except asyncio.CancelledError:
            print(f"Consumer task cancelled for topic: {self.topic}")
        except Exception as e:
            print(f"Consumer error for topic {self.topic}: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop consumer"""
        self._running = False
        if self.consumer:
            await self.consumer.stop()
            print(f"Stopped consumer for topic: {self.topic}")