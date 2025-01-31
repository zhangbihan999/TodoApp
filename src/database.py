from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'   # 本地的用于测试的 sqlite3 数据库
SQLALCHEMY_DATABASE_URL = 'postgresql://bcholchu:kcaxyioicagxywkdjoza@alpha.india.mkdb.sh:5432/hagctuuq'

# 创建与数据库的连接
#engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  # sqlite3
engine = create_engine(SQLALCHEMY_DATABASE_URL)

"""
创建与数据库的会话。每次与数据库进行交互都是通过 session 来实现。
autocommit=False 表示会话不自动提交，需要显式调用 session.commit() 来提交更改。
"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()