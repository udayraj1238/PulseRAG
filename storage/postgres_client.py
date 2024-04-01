import asyncio
import os
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, select, func

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String, nullable=False)
    rewritten_query = Column(String)
    answer = Column(String, nullable=False)
    hallucination_risk = Column(Float, nullable=False)
    flagged = Column(Boolean, nullable=False)
    retrieval_attempts = Column(Integer, nullable=False)
    cache_hit = Column(Boolean, nullable=False)
    total_latency_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String)
    rating = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

db_url = os.getenv("DATABASE_URL")
if db_url:
    engine = create_async_engine(db_url, echo=False)
else:
    engine = create_async_engine('sqlite+aiosqlite:///pulserag.db', echo=False)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Automatically initialize db for simple testing
asyncio.run(init_db())

async def save_conversation(state: dict, latency: float):
    async with async_session() as session:
        conv = Conversation(
            id=state.get("conversation_id", str(uuid.uuid4())),
            query=state.get("query"),
            rewritten_query=state.get("rewritten_query"),
            answer=state.get("answer"),
            hallucination_risk=state.get("hallucination_risk", 0.0),
            flagged=state.get("flagged", False),
            retrieval_attempts=state.get("retrieval_attempts", 0),
            cache_hit=state.get("cache_hit", False),
            total_latency_ms=latency
        )
        session.add(conv)
        await session.commit()
        return conv.id

async def save_feedback(conversation_id: str, rating: int, comment: str = None):
    async with async_session() as session:
        fb = Feedback(
            conversation_id=conversation_id,
            rating=rating,
            comment=comment
        )
        session.add(fb)
        await session.commit()

async def get_bad_sources():
    # Placeholder logic for bad sources analytics
    # In a real system, you'd join Conversation and Feedback tables with chunk metadata
    # We will return dummy for now since chunk metadata isn't explicitly stored in SQL yet
    return [{"chunk_id": "dummy_123", "bad_count": 5}]

