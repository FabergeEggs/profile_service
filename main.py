# Замените содержимое main.py на это:
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.handlers import router
from src.infrastructure.database.session import engine
from src.infrastructure.database.models import Base
from src.infrastructure.message_broker.producer import KafkaEventProducer
from src.infrastructure.message_broker.consumer import KafkaConsumer
from src.consumers.register_consumer import handle_user_registered
import uvicorn
import os

from fastapi.middleware.cors import CORSMiddleware

# Global instances
event_producer = KafkaEventProducer()
user_consumer = KafkaConsumer("user.created", handle_user_registered)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Profile Service...")
    
    # Initialize producer (only if Kafka enabled)
    if os.getenv("DISABLE_KAFKA", "false").lower() != "true":
        await event_producer.start()
        await user_consumer.start()
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if os.getenv("DISABLE_KAFKA", "false").lower() != "true":
        await event_producer.stop()
        await user_consumer.stop()

app = FastAPI(
    title="Profile Service",
    description="User profile management service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "profile-service",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "Profile Service is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)