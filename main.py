from fastapi import FastAPI, HTTPException, Path, Depends
from typing import List, Annotated
from sqlalchemy.orm import session
from models import Base, User, Task
from database import engine, session_local, get_db
from schemas import CreateUser, TaskCreate, Task as TaskResponse, User as DbUser

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post('/add_new_user', response_model=DbUser)
async def create_user(user: CreateUser, db: session = Depends(get_db)) -> DbUser:
    db_user = User(
        username=user.username,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post('/add_new_task', response_model=TaskResponse)
async def create_task(task: TaskCreate, db: session = Depends(get_db)) -> TaskResponse:
    db_user = db.query(User).filter(User.id == task.author_id).first()

    if not db_user:
        raise HTTPException(404, 'нахуй иди')

    db_task = Task(
        title=task.title,
        content=task.content,
        author_id=task.author_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@app.get('/tasks', response_model=List[TaskResponse])
async def get_all_tasks(db: session = Depends(get_db)):
    return db.query(Task).all()







"""
@app.get('/')
async def home() -> str:
    return 'Hello pidor)'

@app.get('/tasks')
async def get_all_tasks() -> List[Task]:
    return [Task(**task) for task in tasks]

@app.get('/tasks/{id}')
async def get_task(id: Annotated[int, Path(..., title='Current task id', ge=1)]) -> Task:
    for task in tasks:
        if task['id'] == id:
            return Task(**task)
    raise HTTPException(status_code=404, detail='Task not found')

@app.post('/tasks/add')
async def add_task(task: TaskCreate) -> Task:
    author = next((user for user in users if user['id'] == task.author_id), None)
    if not author:
        raise HTTPException(404, 'User not found')
    
    new_task = {
        'id': len(tasks)+1,
        'title': task.title,
        'content': task.content,
        'author': author,
    }
    tasks.append(new_task)

    return Task(**new_task)"""