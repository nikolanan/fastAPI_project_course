from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book():
    """
    A class that represents a book.
    """

    def __init__(self,id:int,title:str,author:str,description:str,rating:int,published_date:int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    """
    A request model for creating or updating a book.

    :param BaseModel: BaseModel is a Pydantic model that provides data validation and serialization.
    :type BaseModel: BaseModel
    """

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
async def return_all_books() -> list[Book]:
    """
    A get method that returns all books.
    If successful it gives a 200 OK status code.

    :return: A list of all books.
    :rtype: list[Book]
    """

    return BOOKS

@app.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id:int = Path(gt=0)) -> Book:
    """
    A get method that return a book by its ID.
    book_id is a path paremeter. Upon success it returns a 200 OK status code.
    Path is used to validate the book_id (path is only used for path parameters).

    :param book_id: The ID of the book to be searched.
    :type book_id: int
    :raises HTTPException: If the book is not found, it raises a 404 Not Found error.
    :return: The book with the specified ID.
    :rtype: Book
    """

    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404,detail="Item not found")

@app.get("/books/",status_code=status.HTTP_200_OK)
async def get_books_by_rating(book_rating:int = Query(gt=0,lt=6)) -> list[Book]:
    """
    A get method that return a list of books by rating.
    book_rating is a query parameter.
    Query is used to validate the book_rating (query is only used for query parameters).

    :param book_rating: The rating of the books to be searched.
    :type book_rating: int
    :return: A list of books that match the rating.
    :rtype: list[Book]
    """

    matched_books = []
    for book in BOOKS:
        if book.rating == book_rating:
            matched_books.append(book)
    return matched_books

@app.get("/books_date/{published_date}",status_code=status.HTTP_200_OK)
async def get_books_by_date(published_date:int = Path(gt=1999,lt=2031)) -> list[Book]:
    """
    A get method that returns a list of books by published date.
    published_date is a path parameter. It is validated using Path.

    :param published_date: The published date of the books to be searched.
    :type published_date: int
    :return: A list of books that match the published date.
    :rtype: list[Book]
    """

    matched_books = []
    for i in range(len(BOOKS)):
        if published_date == BOOKS[i].published_date:
            matched_books.append(BOOKS[i])
    return matched_books

@app.post("/create_book",status_code=status.HTTP_201_CREATED)
async def create_book(book_request:BookRequest):
    """
    A POST method that creates a new book.

    The book_request parameter is expected in the request 
    body and is validated using Pydantic's BaseModel.
    The data comes as a JSON object. FastAPI automatically converts it to a Python dictionary,
    and then into a BookRequest object for validation and use in the function.
    Response status code is 201 created if successful.

    :param book_request: The book to be created.
    :type book_request: BookRequest
    """

    new_book = Book(**book_request.model_dump()) ## Makes BookRequest a dictionary
    ## and then unpacks it into keyword arguments for the Books class to be initialized.
    BOOKS.append(find_book_id(new_book))

def find_book_id(book:Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book

@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book:BookRequest):
    """
    A put method that updates a book.

    The book is a body parameter.
    Body converts the request body from JSON to a Python dictionary
    and then into a BookRequest object for validation and use.
    Response status code is 204 no content if successful.

    :param book: The book to be updated.
    :type book: BookRequest
    :raises HTTPException: If the book is not found, it raises a 404 Not Found error.
    """

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
    """
    A delete method that deletes a book by its ID.
    book_id is a path parameter. It is validated using Path.
    Response status code is 204 no content if successful.

    :param book_id: The ID of the book to be deleted.
    :type book_id: int
    :raises HTTPException: HTTPException is raised if the book is not found, resulting in a 404 Not Found error.
    """
    book_changed = False
    for i in range(len(BOOKS)):
        if book_id == BOOKS[i].id:
            book_changed = True
            BOOKS.pop(i)
            break
    if not book_changed:
        raise HTTPException(status_code=404,detail="Item not found")
