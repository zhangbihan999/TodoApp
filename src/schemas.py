from pydantic import BaseModel, Field

# 你想让用户填的表单长什么样，这里的类就怎么定义
# 若用户填写的表单数据不满足 pydantic 定义的格式则会自动抛出错误
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=3)