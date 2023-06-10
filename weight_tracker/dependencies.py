import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, templates
from .database import AsyncSessionMaker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


SECRET_KEY = "CHANGE_ME"


async def get_db():
    async with AsyncSessionMaker() as session:
        yield session


async def get_templates():
    return Jinja2Templates(directory=os.path.dirname(templates.__file__))


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as ex:
        raise credentials_exception from ex

    user = await crud.users.get_user_by_name(db, username)
    if not user:
        raise credentials_exception
    return user
