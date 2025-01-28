from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from ..database import get_db
from .auth import get_current_user
from ..models import Users
from ..schemas import UserVerification
from .auth import bcrypt_context

router = APIRouter(
    prefix="/user",
    tags=['user']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

### Pages ###


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
    
    user_model.hashed_password = bcrypt_context.hash(user_verfication.password)

    db.add(user_model)
    db.commit()

@router.put('/change-phone-number/{phone_number}', status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_model = db.query(Users).filter(Users.id == user['id']).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()