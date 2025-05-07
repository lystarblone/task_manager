from pydantic import BaseModel, Field

class UserBase(BaseModel):
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль (минимум 8 символов)")

class CreateUser(UserBase):
    pass

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str = Field(..., description="Заголовок задачи")
    content: str = Field(..., description="Содержимое задачи")
    author_id: int = Field(..., ge=1, description="ID автора задачи")

class Task(TaskBase):
    id: int
    class Config:
        orm_mode = True

class TaskCreate(TaskBase):
    pass