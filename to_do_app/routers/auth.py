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
    """
    Response model for the access token.

    :param BaseModel: pydantic.BaseModel
    :type BaseModel: pydantic.BaseModel
    """

    access_token:str
    token_type:str

def get_db():
    """
    Makes a local database session available for the duration of a request.
    This function yields a database session that is closed after use.
    Yield is used to ensure that the session is closed proprerly,
    since yield maintains the state of the function between calls.
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
## Session is the type and get_db is the function that provides the session,
## Depends is used to declare that this dependency should be injected

def create_access_token(username:str, user_id:int, role:str, expires_delta:timedelta):
    """

    :param username: _description_
    :type username: str
    :param user_id: _description_
    :type user_id: int
    :param expires_delta: _description_
    :type expires_delta: timedelta
    :return: _description_
    :rtype: _type_
    """

    encode = {"sub":username, "id":user_id, "role":role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    """
    Retrieves the current user from the JWT token.

    :param token: a token string that is passed in the request header
    :type token: Annotated[str,Depends]
    :raises HTTPException: If the the user is none
    :raises HTTPException: If there is an error decoding the JWT token
    :return: _description
    :rtype: _type_
    """
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
        username:str = payload.get("sub")
        user_id:int = payload.get("id")
        user_role:str = payload.get("role")
        
        if username is None or user_id is None:
            raise HTTPException(staus_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
        return {"username":username, "id":user_id, "user_role":user_role}
    except JWTError:
        raise HTTPException(staus_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")

class CreateUserRequest(BaseModel):
    """
    Request model for creating a new user.

    :param BaseModel: Base class for Pydantic models.
    :type BaseModel: pydantic.BaseModel
    """

    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str
    phone_number:str

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependancy,
                      create_user_request:CreateUserRequest):
    """
    Creates a new user in the database.

    :param db: Database session dependency.
    :type db: db_dependancy
    :param create_user_request: It is a request model that parses the incoming JSON data
    :type create_user_request: CreateUserRequest
    """
    
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        phone_number = create_user_request.phone_nubmer
    )

    db.add(create_user_model)
    db.commit()

def authenticate_user(username:str,password:str,db) -> Users | bool:
    """
    Authenticates a user by checking the username and password against the database.

    :param username: username of the user to authenticate
    :type username: str
    :param password: password of the user to authenticate
    :type password: str
    :param db: Database session dependency.
    :type db: db_dependancy
    :return: User object if authentication is successful, False otherwise.
    :rtype: Users | bool
    """
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_dependancy):
    """
    Logs in a user and returns an access token.

    :param form_data: Form data containing username and password.
    :type form_data: Annotated[OAuth2PasswordRequestForm,Depends]
    :param db: Database session dependency.
    :type db: db_dependancy
    :raises HTTPException: If the user cannot be authenticated, a 401 error is raised.
    :return: Access token and token type.
    :rtype: dict
    """

    user = authenticate_user(form_data.username,form_data.password,db)

    if not user:
        raise HTTPException(staus_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
    
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {"access_token":token,"token_type":"bearer"}
