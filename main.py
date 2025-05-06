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

tasks = [
    {
        'id': 1,
        'title': 'Micropenis',
        'content': 'Yohoho',
    },
    {
        'id': 2,
        'title': 'Aiaiai',
        'content': 'Sisi',
    }
]

@app.get('/')
def home() -> str:
    return 'Hello pidor)'

@app.get('/tasks')
def get_all_tasks() -> List[Task]:
    return [Task(**task) for task in tasks]

@app.get('/tasks/{id}')
def get_task(id: int) -> Task:
    for task in tasks:
        if task['id'] == id:
            return Task(**task)
    raise HTTPException(status_code=404, detail='Task not found')