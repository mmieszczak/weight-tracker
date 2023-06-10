from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..crud import users as crud
from ..dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    if await crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if await crud.get_user_by_name(db, username=user.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    db_user = await crud.create_user(db=db, user=user)
    return schemas.User.from_orm(db_user)
