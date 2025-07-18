from fastapi import FastAPI, Body

app = FastAPI() #instance of the FastAPI app


BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"}
]

@app.get("/books")
async def first_api() -> list[dict]:
    """
    A simple API that get method that returns a list of books.

    :return: list of books
    :rtype: list[dict]
    """

    return BOOKS

@app.get("/books/{book_title}")
async def read_book(book_title:str) -> dict | None:
    """
    A get method that returns a book by its title.
    book_title is a path parameter.

    :param book_title: The title of the book to be searched.
    :type book_title: str
    :return: dictionary of the book if found, else None.
    :rtype: dict or None
    """

    for book in BOOKS:
        if book["title"].lower() == book_title.lower():
            return book

@app.get("/books/")
async def read_category_by_query(category:str) ->list[dict]:
    """
    A get method that returns a list of books by category.
    category is a query parameter.That is indicated by the / after the endpoint
    /books.

    :param category: The category of the books to be searched.
    :type category: str
    :return: a list of books that match the category.
    :rtype: list[dict]
    """
    match_categories = []
    for book in BOOKS:
        if book["category"].lower() == category.lower():
            match_categories.append(book)
    return match_categories

@app.get("/books/{author_name}/")
async def read_author_category_by_query(author_name:str,category:str) -> list[dict]:
    """
    A get method that return a list of books by author and category.
    author_name is a path paramethimer and category is a query parameter
    (after the slash).

    :param author_name: The name of the author as a path parameter.
    :type author_name: str
    :param category: The category of the books as a query parameter.
    :type category: str
    :return: a list of books that match the author and category.
    :rtype: list[dict]
    """

    matched_books = []
    for book in BOOKS:
        if book["author"].lower() == author_name.lower() and \
        book["category"].lower() == category.lower():
            matched_books.append(book)
    return matched_books

@app.post("/books/create_book")
async def create_book(new_book:dict = Body()):
    """
    A post method that creates a new book.
    The book is passed as a body parameter.
    Body converts the request body from JSON to a Python dictionary.

    :param new_book: The book object to be inserted.
    :type new_book: dict
    """

    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(updated_book:dict = Body()):
    """
    A put method (overwrites data, unlike patch which updates data)
    that updates a book. Body converts the request body from JSON
    to a Python dictionary.

    :param updated_book: Dictionary of the book to be updated.
    :type updated_book: dict
    """

    for i, book in enumerate(BOOKS):
        if book.get("title", "").lower() == updated_book.get("title", "").lower():
            BOOKS[i] = updated_book

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title:str):
    """
    A delete method that deletes a book by a book title
    book_title is a path parameter.

    :param book_title: The title of the book to be deleted.
    :type book_title: str
    """

    for i, book in enumerate(BOOKS):
        if book.get("title").lower() == book_title.lower():
            BOOKS.pop(i)
            break

@app.get("/books/authors/{author_name}")
async def get_book_by_author(author_name:str) -> list[dict]:
    """
    A get method that returns a list of books by author.
    author_name is a path parameter.

    :param author_name: The name of the author to be searched.
    :type author_name: str
    :return: a list of books that match the author.
    :rtype: list[dict]
    """

    matched_books_by_author = []
    for book in BOOKS:
        if book.get("author").lower() == author_name.lower():
            matched_books_by_author.append(book)
    return matched_books_by_author

@app.get("/books/authors/query/")
async def get_book_by_author_query(author_name:str) -> list[dict]:
    """Returns a list of books by author using query parameter.
    author_name is a query parameter.

    :param author_name: The name of the author to be searched.
    :type author_name: str
    :return: A list of books that match the author.
    :rtype: list[dict]
    """
    matched_books_by_author = []
    for book in BOOKS:
        if book.get("author").lower() == author_name.lower():
            matched_books_by_author.append(book)
    return matched_books_by_author
