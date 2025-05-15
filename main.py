from fastapi import Depends, FastAPI, HTTPException
from typing import Annotated, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session, init_db
from models import User, Task
from schemas import CreateUser, TaskCreate, Task as TaskResponse, User as DbUser

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/add_new_user", response_model=DbUser, tags=["users"])
async def create_user(
    user: CreateUser, 
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")

    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.get("/users", response_model=List[DbUser], tags=["users"])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_async_session)]
):
    result = await db.execute(select(User))
    return result.scalars().all()


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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)