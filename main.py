from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    id: int
    username: str

class Task(BaseModel):
    id: int
    title: str
    content: str
    author: User

class TaskCreate(BaseModel):
    title: str
    content: str
    author_id: int

users = [
    {
        'id': 1,
        'username': 'Хуесос',
    },
    {
        'id': 2,
        'username': 'Пиздолиз',
    }
]

tasks = [
    {
        'id': 1,
        'title': 'Micropenis',
        'content': 'Yohoho',
        'author': users[0],
    },
    {
        'id': 2,
        'title': 'Aiaiai',
        'content': 'Sisi',
        'author': users[1]
    }
]

@app.get('/')
async def home() -> str:
    return 'Hello pidor)'

@app.get('/tasks')
async def get_all_tasks() -> List[Task]:
    return [Task(**task) for task in tasks]

@app.get('/tasks/{id}')
async def get_task(id: int) -> Task:
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

    return Task(**new_task)