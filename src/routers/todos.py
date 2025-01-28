from fastapi import APIRouter, status, Depends, Path, HTTPException, Request
from typing import Annotated
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import TodoRequest
from ..models import Todos
from .auth import get_current_user
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(
    prefix="/todos",
    tags=['todos']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory='templates')

def redirect_to_login():
    # redirect 是一种 response
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    # RedirectResponse 还能附着着 delete_cookie
    redirect_response.delete_cookie(key='access_token')
    return redirect_response

### Pages ###
@router.get('/todo-page', response_class=HTMLResponse)
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if not user:
            return redirect_to_login()
        
        todos = db.query(Todos).filter(Todos.owner_id == user['id']).all()
        return templates.TemplateResponse(request=request, name="todo.html", context={"todos": todos, "user": user})
    except:
        return redirect_to_login()
    
@router.get('/add-todo-page')
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if not user:
            return redirect_to_login()
        
        return templates.TemplateResponse(request=request, name="add-todo.html", context={"user": user})
    
    except:
        return redirect_to_login()
    
@router.get('/edit-todo/{todo_id}')
async def render_edit_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if not user:
            return redirect_to_login()
        
        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse(request=request, name="edit-todo.html", context={"user": user, "todo": todo})
    except:
        return redirect_to_login()

### Endpoints ###
@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todos).filter(Todos.owner_id == user['id']).all()

@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_one_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['id']).first()
    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return todo_model

@router.post('/create-todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    # 用户通过填写表单创建新的 todo，对表单的一次验证由 pydantic 执行
    # model_dump() 将 TodoRequest 对象转化成一个字典，找到对应的 key 来填充对应的 value
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id'))
    
    db.add(todo_model)
    db.commit()

@router.put('/update-todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['id']).first()
    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete('/delete-todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['id']).first()
    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['id']).delete()

    db.commit()