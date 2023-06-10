from sqlalchemy import QueuePool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./sqlite.db"
engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    connect_args={"check_same_thread": False},
)
AsyncSessionMaker = async_sessionmaker(
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
