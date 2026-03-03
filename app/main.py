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
from typing import List, Dict
from sqlmodel import select, Session

from app.infrastructure.db import create_db
from app.infrastructure.models import User, Genre, Recommendation, UserFeedback, UserUpdate
from app.infrastructure.requests import get_or_create_genre, get_user_by_telegram_id, get_recommendations, \
    post_feedback, delete_existing_user, update_existing_user, get_random_book_by_genre

app = FastAPI(title="LitRecom API")

@app.on_event("startup")
def on_startup():
    create_db()

@app.post("/genres/", response_model=Genre)
async def create_genre(genre_name: str):
    genre = await get_or_create_genre(genre_name)
    return genre

@app.get("/genres/", response_model=List[Genre])
async def get_genre(genre_name: str):
    genre = await get_or_create_genre(genre_name)
    return genre

@app.get("/books/random/{genre_id}", response_model=Recommendation)
async def get_random_book(telegram_id: int, genre_id: int):
    user = await get_user_by_telegram_id(telegram_id)
    recommendation = get_random_book_by_genre(user_id=user.id, genre_id=genre_id)

    if not recommendation:
        raise HTTPException(status_code=404, detail="No books found")
    return recommendation

@app.post("/users/", response_model=User)
async def create_user(user_telegram_id: int, username: str):
    user = await create_user(telegram_id=user_telegram_id, username=username)
    return user

@app.get("/users/{telegram_id}", response_model=User)
async def get_user_by_tg(telegram_id: int):
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/{telegram_id}/recommend", response_model=List[Dict])
async def recommend_for_user(
        telegram_id: int,
        amount_of_recommendations: int = Query(3, ge=1)
):
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recommendations = await get_recommendations(user.id, amount_of_recommendations)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return recommendations

@app.post("/feedback/", response_model=UserFeedback)
async def create_feedback(
        telegram_id: int,
        google_book_id: str,
        title: str,
        genre_name: str,
        rating: str
):
    user = await get_user_by_telegram_id(telegram_id)
    feedback = await post_feedback(
        user_id=user.id,
        google_book_id=google_book_id,
        title=title,
        genre_name=genre_name,
        rating=rating
    )
    return feedback

@app.delete("/users/{telegram_id}", response_model=User)
async def delete_user(telegram_id: int):
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = await delete_existing_user(user.id)
    return deleted_user

@app.put("/users/{telegram_id}", response_model=User)
async def update_user(telegram_id: int, new_data: UserUpdate):
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await update_existing_user(user.id, new_data)
    return updated_user
