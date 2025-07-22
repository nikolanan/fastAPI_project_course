from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users

app = FastAPI() ## Instatiate the FastAPI application

models.Base.metadata.create_all(bind=engine) ## Create the database tables based on the models defined, when the application starts

app.include_router(auth.router) ## Include the auth router for authentication endpoints
app.include_router(todos.router) ## Include the todos router for to-do item management endpoints
app.include_router(admin.router)
app.include_router(users.router)