from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    password: str

class CreateUser(UserBase):
    pass

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str
    content: str
    author_id: int

class Task(TaskBase):
    id: int
    author: User

    class Config:
        orm_mode = True

class TaskCreate(TaskBase):
    pass