from contextlib import asynccontextmanager
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.handlers import router
from src.consumers.register_consumer import handle_user_registered
from src.core.config import settings
from src.core.logging import setup_logging
from src.infrastructure.message_broker.consumer import KafkaConsumer
from src.infrastructure.message_broker.producer import get_event_producer
from src.kafka_topics import USER_REGISTERED
from src.migrations import migrate

logger = setup_logging()

event_producer = get_event_producer()
user_consumer = KafkaConsumer(USER_REGISTERED, handle_user_registered)


def _get_migrations_dsn() -> str:
    if settings.migrations_database_url:
        return settings.migrations_database_url
    return settings.database_url.replace("postgresql+asyncpg://", "postgresql://")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Profile Service")
    await event_producer.start()
    logger.info("Kafka producer started")
    await user_consumer.start()
    logger.info("Kafka consumer started on topic %s", USER_REGISTERED)

    if settings.run_db_migrations_on_startup:
        try:
            migrate.up(_get_migrations_dsn())
            logger.info("Database migrations applied")
        except Exception as exc:
            logger.error("Failed to apply database migrations: %s", exc)

    yield

    logger.info("Shutting down Profile Service")
    await user_consumer.stop()
    await event_producer.stop()


app = FastAPI(title="Profile Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
