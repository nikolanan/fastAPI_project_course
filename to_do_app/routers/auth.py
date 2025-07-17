from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Users
from sqlalchemy.orm import Session
from database import SessionLocal
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "5f4dcc3b5aa765d61d8327deb882cf99cfe9abec345123871cde891273abcdef"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class Token(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session,Depends(get_db)]


def create_access_token(username:str,user_id:int,expires_delta:timedelta):

    encode = {"sub":username, "id":user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
        username:str = payload.get("sub")
        user_id:int = payload.get("id")
        
        if username is None or user_id is None:
            raise HTTPException(staus_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
        return {"username":username,"id":user_id}
    except JWTError:
        raise HTTPException(staus_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")

class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependancy,
                      create_user_request:CreateUserRequest):
    
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )

    db.add(create_user_model)
    db.commit()

def authenticate_user(username:str,password:str,db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_dependancy):
    user = authenticate_user(form_data.username,form_data.password,db)

    if not user:
        raise HTTPException(staus_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
    
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token":token,"token_type":"bearer"}
