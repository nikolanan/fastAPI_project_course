from fastapi import FastAPI, Body

app = FastAPI()


BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"}
]

@app.get("/books")
async def first_api():
    return BOOKS

@app.get("/books/{book_title}")
async def read_book(book_title:str):
    for book in BOOKS:
        if book["title"].lower() == book_title.lower():
            return book
        
@app.get("/books/")
async def read_category_by_query(category:str):
    match_categories = []
    for book in BOOKS:
        if book["category"].lower() == category.lower():
            match_categories.append(book)
    return match_categories

@app.get("/books/{author_name}/")
async def read_author_category_by_query(author_name:str,category:str):
    matched_books = []
    for book in BOOKS:
        if book["author"].lower() == author_name.lower() and \
        book["category"].lower() == category.lower():
            matched_books.append(book)
    return matched_books
            
@app.post("/books/create_book")
async def create_book(new_book = Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(updated_book = Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").lower() == updated_book.get("title").lower():
            BOOKS[i] = updated_book

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title:str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").lower() == book_title.lower():
            BOOKS.pop(i)
            break

@app.get("/books/authors/{author_name}")
async def get_book_by_author(author_name:str):
    matched_books_by_author = []
    for book in BOOKS:
        if book.get("author").lower() == author_name.lower():
            matched_books_by_author.append(book)
    return matched_books_by_author

@app.get("/books/authors/query/")
async def get_book_by_author_query(author_name:str):
    matched_books_by_author = []
    for book in BOOKS:
        if book.get("author").lower() == author_name.lower():
            matched_books_by_author.append(book)
    return matched_books_by_author