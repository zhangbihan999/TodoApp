from fastapi import APIRouter, Depends, status, HTTPException, Request
from typing import Annotated
from sqlalchemy.orm import Session
from ..database import get_db
from .auth import get_current_user
from ..models import Users
from ..schemas import UserVerification, BasicInfoRequest
from .auth import bcrypt_context
from ..utils import redirect_to_login
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/user",
    tags=['user']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory="templates")

### Pages ###
@router.get('/user-info', status_code=status.HTTP_200_OK)
async def user_info_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if not user:
            return redirect_to_login()
        
        user_info = db.query(Users).filter(Users.id == user['id']).first()
        return templates.TemplateResponse(request=request, name="user.html", context={"user": user, "user_info": user_info})
    except:
        return redirect_to_login()


### Endpoints ###
@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model = db.query(Users).filter(Users.id == user['id']).first()
    return user_model

@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verfication: UserVerification):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model = db.query(Users).filter(Users.id == user['id']).first()

    if not bcrypt_context.verify(user_verfication.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_model.hashed_password = bcrypt_context.hash(user_verfication.new_password)

    db.add(user_model)
    db.commit()

@router.put('/change-basic-info', status_code=status.HTTP_204_NO_CONTENT)
async def change_basic_info(user: user_dependency, db: db_dependency, request: BasicInfoRequest):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model = db.query(Users).filter(Users.id == user['id']).first()

    user_model.email = request.email
    user_model.username = request.username
    user_model.role = request.role
    user_model.phone_number = request.phone_number

    db.add(user_model)
    db.commit()