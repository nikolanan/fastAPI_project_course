from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from typing import Annotated
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user


router = APIRouter()

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

class TodoRequest(BaseModel):
    """
    Request model for creating or updating a to-do item.

    :param BaseModel: Base class for Pydantic models.
    :type BaseModel: pydantic.BaseModel
    """

    title:str = Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int =Field(gt=0,lt=6)
    complete:bool

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependancy, db:db_dependancy):
    """Fetches all to-do items from the database.

    :param db: Database session dependency.
    :type db: db_dependancy
    :return: List of all to-do items.
    :rtype: list[Todos]
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failde")

    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependancy, db:db_dependancy, todo_id:int = Path(gt=0)):
    """
    Fetches a specific to-do item by its ID.

    :param db: Database session dependency.
    :type db: db_dependancy
    :param todo_id: ID of the to-do item to fetch.
    :type todo_id: int
    :raises HTTPException: If the to-do item is not found, a 404 error is raised.
    :return: The to-do item if found.
    :rtype: Todos
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failde")
    
    result = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if result is not None:
        return result
    raise HTTPException(status_code=404,detail="To do not found")

@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependancy, 
                      db:db_dependancy, 
                      todo_request:TodoRequest):
    """
    Creates a new to-do item in the database.

    :param user: Current user information extracted from the JWT token.
    :type user: user_dependancy
    :param db: Database session dependency.
    :type db: db_dependancy
    :param todo_request: Request model containing the details of the to-do item.
    :type todo_request: TodoRequest
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failde")

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id")) ## model_dump() coverts it to a dictionary
    ## and then unpacks it into keyword arguments then passed for the Todos model
    db.add(todo_model) ## Adds the todo_model instance to the current database session (in memory)
    db.commit() ## Commits the changes to the database

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependancy, 
                      db:db_dependancy,
                      todo_request:TodoRequest,
                      todo_id:int = Path(gt=0)
                      ):
    """
    Updates an existing to-do item in the database.

    :param db: Database session dependency.
    :type db: db_dependancy
    :param todo_request: Request model containing the updated details of the to-do item.
    :type todo_request: TodoRequest
    :param todo_id: ID of the to-do item to update.
    :type todo_id: int
    :raises HTTPException: If the to-do item is not found, a 404 error is raised.
    """

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failde")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependancy, db:db_dependancy, todo_id:int = Path(gt=0)):
    """
    Deletes a specific to-do item by its ID.

    :param db: Database session dependency.
    :type db: db_dependancy
    :param todo_id: ID of the to-do item to delete.
    :type todo_id: int
    :raises HTTPException: If the to-do item is not found, a 404 error is raised.
    """

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failde")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
    db.commit()
