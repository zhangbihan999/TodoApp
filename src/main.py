from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from .routers import todos, auth, admin, users
from .database import engine, Base

app = FastAPI()

# 把 /static 路径与 src/static 目录相绑定，使得用户可以通过访问 /static 路径来访问静态文件
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# 在指定数据库中创建 models.py 中定义的数据表
Base.metadata.create_all(bind=engine)

# 让用户访问 / 时直接尝试访问 todos/todo-page，如果有 cookies 就能直接访问到，没有的话就会回到登录界面
@app.get('/')
def redict_to_login(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)