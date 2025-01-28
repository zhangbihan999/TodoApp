from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean)
    owner_id = Column(Integer, ForeignKey("users.id"))

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)  # 检查邮箱，每个邮箱只能注册一次
    username = Column(String, unique=True)  # 每个用户名只能注册一次
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    phone_number = Column(String)