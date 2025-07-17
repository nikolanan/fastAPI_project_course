from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book():
    def __init__(self,id:int,title:str,author:str,description:str,rating:int,published_date:int):
        self.id = id
        self.title = title 
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id:Optional[int] = Field(description="id is not needed for create",default=None)
    title:str = Field(min_length=3)
    author:str = Field(min_length=1)
    description:str = Field(min_length=1,max_length=100)
    rating:int = Field(gt=-1,lt=6)
    published_date:int = Field(gt=1999,lt=2031)

    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"New book",
                "author":"Joe Doe",
                "description": "Book description",
                "rating":5,
                "published_date":2025
            }
        }
    }




BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]

@app.get("/books",status_code=status.HTTP_200_OK)
async def return_all_books():
    return BOOKS

@app.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id:int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404,detail="Item not found")

@app.get("/books/",status_code=status.HTTP_200_OK)
async def get_books_by_rating(book_rating:int = Query(gt=0,lt=6)):
    matched_books = []
    for book in BOOKS:
        if book.rating == book_rating:
            matched_books.append(book)
    return matched_books

@app.get("/books_date/{published_date}",status_code=status.HTTP_200_OK)
async def get_books_by_date(published_date:int = Path(gt=1999,lt=2031)):
    matched_books = []
    for i in range(len(BOOKS)):
        if published_date == BOOKS[i].published_date:
            matched_books.append(BOOKS[i])
    return matched_books

@app.post("/create_book",status_code=status.HTTP_201_CREATED)
async def create_book(book_request:BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book:Book):
    if len(BOOKS)>0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book

@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book:BookRequest):
    updated_book = Book(**book.model_dump())
    book_changed = False
    for i in range(len(BOOKS)):
        if updated_book.id == BOOKS[i].id:
            BOOKS[i] =  updated_book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404,detail="Item not found")

@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(book_id:int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if book_id == BOOKS[i].id:
            book_changed = True
            BOOKS.pop(i)
            break
    if not book_changed:
        raise HTTPException(status_code=404,detail="Item not found")
