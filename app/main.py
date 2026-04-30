from fastapi import FastAPI, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from typing import List, Dict
from sqlmodel import select, Session

from infrastructure.db import create_db, get_session
from infrastructure.models import User, Genre, UserFeedback, UserUpdate, UserPreference
from infrastructure.requests import get_user_by_telegram_id, get_recommendations, \
    post_feedback, delete_existing_user, update_existing_user, get_all_feedbacks, \
    get_user_preferences, delete_feedbacks_and_preferences, get_genres, create_genre, create_user, get_genre_by_id, create_preference
from services.google_books_api import search_books, get_random_book_by_genre


app = FastAPI(title="LitRecom API")

@app.on_event("startup")
async def on_startup():
    await create_db()

@app.post("/genres/", response_model=Genre)
async def post_genre(genre_name: str, session: Session = Depends(get_session)):
    genre = await create_genre(genre_name, session)
    return genre

@app.get("/genres/", response_model=List[Genre])
async def list_genres(session: Session = Depends(get_session)):
    genres = await get_genres(session)
    return genres

@app.get("/genres/", response_model=Genre)
async def get_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = await get_genre_by_id(genre_id, session)
    return genre

@app.get("/books/random/{genre_id}", response_model=Dict[str, Genre])
async def get_random_book(genre_id: int, session: Session = Depends(get_session)):
    genre = await get_genre_by_id(genre_id, session)
    recommendation = await get_random_book_by_genre(genre=genre.name)

    if not recommendation:
        raise HTTPException(status_code=404, detail="No books found")
    return recommendation

@app.post("/users/", response_model=User)
async def post_user(user_telegram_id: int, username: str, session: Session = Depends(get_session)):
    user = await create_user(telegram_id=user_telegram_id, username=username, session=session)
    return user

@app.get("/users/{telegram_id}", response_model=User)
async def get_user_by_tg(telegram_id: int, session: Session = Depends(get_session)):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{telegram_id}/recommend", response_model=List[Dict])
async def recommend_for_user(
        telegram_id: int,
        session: Session = Depends(get_session),
        amount_of_recommendations: int = Query(3, ge=1)
):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recommendations = await get_recommendations(session=session, user_id=user.id, amount=amount_of_recommendations)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return recommendations

@app.post("/feedback/", response_model=UserFeedback)
async def create_feedback(
        telegram_id: int,
        genre_name: str,
        rating: str,
        google_book_id: str | None = None,
        title: str | None = None,
        session: Session = Depends(get_session)
):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    feedback = await post_feedback(
        user_id=user.id,
        google_book_id=google_book_id,
        title=title,
        genre_name=genre_name,
        rating=rating,
        session=session
    )
    return feedback

@app.get("/users/{telegram_id}/feedback/", response_model=List[UserFeedback])
async def get_feedbacks(telegram_id: int, session: Session = Depends(get_session)):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    feedbacks = await get_all_feedbacks(user.id, session)
    return feedbacks

@app.post("/users/{telegram_id}/preference", response_model=UserPreference)
async def post_preferences(
        telegram_id: int,
        genre_id: int,
        session: Session = Depends(get_session)):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    preference = await create_preference(user.id, genre_id)
    return preference

@app.get("/users/{telegram_id}/preferences", response_model=List[UserPreference])
async def get_preferences(telegram_id: int, session: Session = Depends(get_session)):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    preferences = await get_user_preferences(user.id, session)
    return preferences

@app.delete("/users/{telegram_id}", response_model=User)
async def delete_user(telegram_id: int, session: Session = Depends(get_session)):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = await delete_existing_user(user.id, session)
    return deleted_user

@app.put("/users/{telegram_id}", response_model=User)
async def update_user(telegram_id: int, new_data: UserUpdate, session: Session = Depends(get_session)):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await update_existing_user(user.id, new_data, session)
    return updated_user

@app.get("/books/search/", response_model=List)
async def search_query(query: str, max_results: int = 5):
    result = await search_books(query, max_results)
    return result

@app.delete("/users/{telegram_id}/reset", response_model=List[UserPreference])
async def reset_feedbacks_and_preferences(telegram_id: int, session: Session = Depends(get_session)):
    user = await get_user_by_telegram_id(telegram_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_preferences = await delete_feedbacks_and_preferences(user.id, session)
    return deleted_preferences
