from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from typing import Annotated
from starlette import status
from pydantic import BaseModel, Field


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session,Depends(get_db)]

class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int =Field(gt=0,lt=6)
    complete:bool

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(db:db_dependancy):
    return db.query(Todos).all()

@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(db:db_dependancy,todo_id:int = Path(gt=0)):
    result = db.query(Todos).filter(Todos.id == todo_id).first()
    if result is not None:
        return result
    raise HTTPException(status_code=404,detail="To do not found")

@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(db:db_dependancy,todo_request:TodoRequest):
    todo_model = Todos(**todo_request.model_dump()) 
    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependancy,
                      todo_request:TodoRequest,
                      todo_id:int = Path(gt=0)
                      ):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependancy,todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    
