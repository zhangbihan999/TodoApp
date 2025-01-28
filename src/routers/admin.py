from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from ..database import get_db
from .auth import get_current_user
from ..models import Todos

router = APIRouter(
    prefix="/admin",
    tags=['admin']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

### Pages ###


### Endpoints ###
@router.get('/todos', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todos).all()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user or user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()