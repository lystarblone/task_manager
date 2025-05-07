from fastapi import FastAPI, HTTPException, Path, Depends, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
from authx import AuthX, AuthXConfig
import uvicorn
from passlib.context import CryptContext
from models import Base, User, Task
from database import engine, get_db
from schemas import CreateUser, TaskCreate, Task as TaskResponse, User as DbUser, UserBase
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка Jinja2
templates = Jinja2Templates(directory="templates")

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not config.JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY не указан в .env файле")
config.JWT_ACCESS_COOKIE_NAME = 'my_access_token'
config.JWT_TOKEN_LOCATION = ['cookies']

security = AuthX(config=config)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not hashed_password.startswith(('$2b$', '$2a$', '$2y$')):
            return False
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, AttributeError):
        return False

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/add_new_user', response_model=DbUser, tags=["Users"], summary="Создать нового пользователя")
async def create_user(user: CreateUser, db: Session = Depends(get_db)) -> DbUser:
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    db_user = User(
        username=user.username,
        password=hash_password(user.password)
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка базы данных")

@app.get('/users', response_model=List[DbUser], tags=["Users"], summary="Получить всех пользователей")
async def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post('/add_new_task', response_model=TaskResponse, tags=["Tasks"], summary="Создать новую задачу")
async def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_subject)
):
    db_user = db.query(User).filter(User.id == task.author_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if db_user.username != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Нет прав для создания задачи от имени другого пользователя")

    db_task = Task(
        title=task.title,
        content=task.content,
        author_id=task.author_id,
    )
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка базы данных")

@app.get('/tasks', response_model=List[TaskResponse], tags=["Tasks"], summary="Получить список задач")
async def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get('/tasks/{id}', response_model=TaskResponse, tags=["Tasks"], summary="Получить задачу по ID")
async def get_current_task(id: int = Path(..., title='Task ID', ge=1), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@app.post('/login', tags=["Auth"], summary="Аутентификация пользователя")
async def login(credentials: UserBase, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    token = security.create_access_token(
    uid=user.username,
    )
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}

@app.get("/protected", tags=["Auth"], summary="Доступ к защищенным данным")
async def protected(current_user: dict = Depends(security.get_current_subject)):
    return {"data": "TOP SECRET", "user": current_user["sub"]}

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)