from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from models import Users
from database import SessionLocal
from typing import Annotated
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["users"]
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
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

class UserVerificationRequest(BaseModel):
    password:str
    new_password:str

@router.get("/info",status_code=status.HTTP_200_OK)
async def get_user_if(user:user_dependancy,db:db_dependancy):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    return user_model

@router.patch("/change_password",status_code=status.HTTP_200_OK)
async def change_user_password(user:user_dependancy,db:db_dependancy,user_verification_data:UserVerificationRequest):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    hashed_password = user_model.hashed_password
    if not bcrypt_context.verify(user_verification_data.password,hashed_password):
        raise HTTPException(status_code=401,detail="Verification failed")
    new_hashed_password = bcrypt_context.hash(user_verification_data.new_password)
    user_model.hashed_password = new_hashed_password
    db.add(user_model)
    db.commit()