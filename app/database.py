import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/urlshortener")

# The engine is the low-level connection to PostgreSQL.
# echo=True prints every SQL query to the console — great for learning, turn off in production.

engine = create_async_engine(DATABASE_URL, echo=True) # async engine

# A session is a "unit of work" — you open one, make changes, then commit or roll back.
# async_sessionmaker creates a factory that produces new sessions on demand.
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# All SQLAlchemy models inherit from this base class.
class Base(DeclarativeBase):
    pass

# FastAPI dependency — routes declare `db: AsyncSession = Depends(get_db)`
# and FastAPI automatically opens a session, passes it in, then closes it when done.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
