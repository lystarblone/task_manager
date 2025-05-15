from pydantic import BaseModel, Field

class UserBase(BaseModel):
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")

class CreateUser(UserBase):
    pass

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    content: str
    author_id: int

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    class Config:
        from_attributes = True