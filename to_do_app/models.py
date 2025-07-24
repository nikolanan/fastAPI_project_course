from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users(Base):
    """
    Model representing a user in the system.

    :param Base: Base class for SQLAlchemy models.
    :type Base: sqlalchemy.ext.declarative.DeclarativeMeta
    """

    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True)
    username = Column(String,unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    role = Column(String)
    phone_number = Column(String)

class Todos(Base):
    """
    Model representing a to-do item.

    :param Base: Base class for SQLAlchemy models.
    :type Base: sqlalchemy.ext.declarative.DeclarativeMeta
    """
    __tablename__ ='todos'

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id")) ## Name is used to reference the Users table