import os
from fastapi import Depends, FastAPI, HTTPException, Response, Request
from typing import Annotated, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from database import get_async_session, init_db
from models import User, Task
from schemas import CreateUser, TaskCreate, Task as TaskResponse, User as DbUser

from authx import AuthX, AuthXConfig
from security import hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm

# --- Жизненный цикл приложения ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# --- Настройка JWT ---
config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
security = AuthX(config=config)

# --- Инициализация приложения ---
app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --------------------- AUTH ---------------------
@app.post("/register", response_model=DbUser, tags=["auth"])
async def register_user(
    user: CreateUser,
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    hashed_pwd = hash_password(user.password)
    db_user = User(email=user.email, password=hashed_pwd)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.post("/login")
async def login(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    form_data: OAuth2PasswordRequestForm = Depends()
):
    email = form_data.username
    password = form_data.password

    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = security.create_access_token(uid=str(db_user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}



@app.get("/protected", tags=["auth"])
async def protected(user=Depends(security.access_token_required)):
    return {"data": "Very secret", "user": user}


# --------------------- USERS ---------------------
@app.get("/users", response_model=List[DbUser], tags=["users"])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    result = await db.execute(select(User))
    return result.scalars().all()


# --------------------- TASKS ---------------------
@app.post("/add_new_task", response_model=TaskResponse, tags=["tasks"])
async def create_task(
    task: TaskCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    db_task = Task(title=task.title, content=task.content, author_id=task.author_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=List[TaskResponse], tags=["tasks"])
async def get_all_tasks(
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    result = await db.execute(select(Task))
    return result.scalars().all()


@app.get("/tasks/{id}", response_model=TaskResponse, tags=["tasks"])
async def get_task_by_id(
    id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


# --------------------- RUN ---------------------
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)