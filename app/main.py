# from app.infrastructure.db import get_session, create_db
# from app.infrastructure.models import Genre, Author, Source, Book
#
#
# def fill_minimal_data():
#     with get_session() as session:
#         genre_fantasy = Genre(name="Фантастика")
#         genre_detective = Genre(name="Детектив")
#         author = Author(name="Айзек Азимов")
#         api_source = Source(name="Google Books", link="https://books.google.com")
#
#         session.add_all([genre_fantasy, genre_detective, author, api_source])
#         session.commit()
#
#         book = Book(
#             title="Основание",
#             author_id=author.id,
#             genre_id=genre_fantasy.id,
#             description="...",
#             source_id=api_source.id,
#         )
#
#         session.add(book)
#         session.commit()
#
# if __name__ == "__main__":
#     create_db()
#     fill_minimal_data()
#     print("Успешно")

from fastapi import FastAPI, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from typing import List, Optional
from sqlmodel import select, Session

from app.infrastructure.db import create_db, get_session
from app.infrastructure.models import User, Genre, Author, Source, Book, Recommendation, UserFeedback, UserUpdate
from app.infrastructure.requests import get_books_by_genre, get_books_by_author, get_book_by_id, \
    get_random_book_by_genre, post_genre, get_genres, post_author, get_authors, post_source, get_sources, post_book, \
    post_user, get_user_by_telegram_id, get_recommendations, get_books, get_books_by_author_and_genre, post_feedback, \
    delete_existing_user, delete_existing_book, update_existing_user

app = FastAPI(title="LitRecom API")

@app.on_event("startup")
def on_startup():
    create_db()

@app.post("/genres/", response_model=Genre)
def create_genre(genre_id: int, genre_name: str):
    genre = post_genre(genre_id, genre_name)
    return genre

@app.get("/genres/", response_model=List[Genre])
def list_genres():
    genres = get_genres()
    return genres

@app.post("/authors/", response_model=Author)
def create_author(author_id: int, author_name: str):
    author = post_author(author_id, author_name)
    return author

@app.get("/authors/", response_model=List[Author])
def list_authors():
    authors = get_authors()
    return authors

@app.post("/sources/", response_model=Source)
def create_source(source_id: int, source_name: str):
    source = post_source(source_id, source_name)
    return source

@app.get("/sources/", response_model=List[Source])
def list_sources():
    sources = get_sources()
    return sources

@app.post("/books/", response_model=Book)
def create_book(
        book_id: int,
        title: str,
        author_id: int | None,
        description: str | None,
        source_id: int | None,
        genre_id: int | None = None,
) -> Book:
    new_book = Book(
        book_id = book_id,
        title = title,
        author_id = author_id,
        description = description,
        source_id = source_id,
        genre_id = genre_id
    )

    book = post_book(new_book) #TODO: убрать создание доменного объекта

    return book

@app.get("/books/", response_model=List[Book])
def list_books(
    genre_id: int | None = None,
    author_id: int | None = None,
):
    if not genre_id and not author_id:
        books = get_books()
    elif genre_id and not author_id:
        books = get_books_by_genre(genre_id)
    elif author_id and not genre_id:
        books = get_books_by_author(author_id)
    else:
        books = get_books_by_author_and_genre(author_id, genre_id)
    return books


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    book = get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/books/random/{genre_id}", response_model=Book)
def get_random_book(genre_id: int):
    book = get_random_book_by_genre(genre_id)

    if not book:
        raise HTTPException(status_code=404, detail="No books found")
    return book

@app.post("/users/", response_model=User)
def create_user(user_id: int, user_telegram_id: int, username: str):
    user = post_user(user_id, user_telegram_id, username)
    return user

@app.get("/users/{telegram_id}", response_model=User)
def get_user_by_tg(telegram_id: int):
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/{telegram_id}/recommend", response_model=List[Book])
def recommend_for_user(
        telegram_id: int,
        amount_of_recommendations: int = Query(3, ge=1)
):
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recommendations = get_recommendations(user.id, amount_of_recommendations)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return recommendations

@app.post("/feedback/", response_model=UserFeedback)
def create_feedback(feedback_id: int, telegram_id: int, book_id: int, rating: str):
    user = get_user_by_telegram_id(telegram_id)
    feedback = post_feedback(feedback_id, user.id, book_id, rating)
    return feedback

@app.delete("/users/{telegram_id}", response_model=User)
def delete_user(telegram_id: int):
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = delete_existing_user(user.id)
    return deleted_user

@app.delete("/books/{book_id}", response_model=Book)
def delete_book(book_id: int):
    book = get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    deleted_book = delete_existing_book(book.id)
    return deleted_book

@app.put("/users/{telegram_id}", response_model=User)
def update_user(telegram_id: int, new_data: UserUpdate):
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_existing_user(user.id, new_data)
    return updated_user
