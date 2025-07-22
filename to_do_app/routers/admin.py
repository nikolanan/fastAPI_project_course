from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from typing import Annotated
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    """
    Makes a local database session available for the duration of a request.
    Yield is used to ensure that the session is closed after use.
    If return was used instead of yield,
    the session would not be closed properly.

    :yield: Session
    :rtype: Session
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session,Depends(get_db)]
## Dependency to the database session for use in route handlers
user_dependancy = Annotated[dict, Depends(get_current_user)]
## Dependency to the current user, which is fetched from the JWT token


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user:user_dependancy, db:db_dependancy):

    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependancy, db:db_dependancy, todo_id:int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
