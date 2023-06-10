from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..models import User


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = argon2.hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_name(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def validate_user_password(
    db: AsyncSession,
    user: OAuth2PasswordRequestForm,
) -> bool:
    db_user = await get_user_by_name(db, user.username)
    if not db_user:
        return False
    return argon2.verify(user.password, db_user.hashed_password)
