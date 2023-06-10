from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, database
from .dependencies import SECRET_KEY, get_db, get_templates
from .routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
        yield
    await database.engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(users.router)


@app.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    if not await crud.users.validate_user_password(db, form_data):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    data = {
        "sub": form_data.username,
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }
    access_token = jwt.encode(data, SECRET_KEY, "HS256")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
async def root(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
