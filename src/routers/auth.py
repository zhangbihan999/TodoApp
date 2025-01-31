from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, Depends, Path, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from ..schemas import CreateUserRequest
from ..models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from ..utils import read_env_file
import os

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

# 加载 .env 文件
read_env_file('.env')

db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')

templates = Jinja2Templates(directory="templates")

### Pages ###
@router.get('/login-page', response_class=HTMLResponse)
async def render_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get('/register-page', response_class=HTMLResponse)
async def render_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

### Endpoints ###
@router.get('/find-user/{user_id}', status_code=status.HTTP_200_OK)
async def find_user(db: db_dependency, user_id: int = Path(gt=0)):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user_model

@router.post('/create-user', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    try:
        user_model = Users(
            username = create_user_request.username,
            email = create_user_request.email,
            hashed_password = bcrypt_context.hash(create_user_request.password),
            role = create_user_request.role,
            phone_number = create_user_request.phone_number
        )

        db.add(user_model)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete('/delete-user/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user_id: int = Path(gt=0)):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": username, "id": user_id, "role": role, "exp": expires}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post('/token', status_code=status.HTTP_201_CREATED)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码不正确！")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))
    return {"access_token": token, "type": "bearer"}

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        id: int = payload.get('id')
        role: str = payload.get('role')
        if not username or not id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return {"username": username, "id": id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)