from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
##This defines the location of the SQLite database file:

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
## Creates a database engine, which is how SQLAlchemy communicates with your actual database.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
## A factory that will create new Session objects, which are used to interact with the database
## (e.g., insert, query, update).

Base = declarative_base()
## Used to create a base class for your ORM models (tables).
