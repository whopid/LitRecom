from sqlmodel import select

from db import get_session
from models import User, Book, Recommendation, UserFeedback


def get_user_by_telegram_id(tg_id: int):
    with get_session() as session:
        statement = select(User).where(User.telegram_id == tg_id)
        return session.exec(statement).first()

def get_books_by_genre(genre_id: int):
    with get_session() as session:
        stmt = select(Book).where(Book.genre_id == genre_id)
        return session.exec(stmt).all()

def get_random_book_by_genre(genre_id: int):
    with get_session() as session:
        stmt = select(Book).where(Book.genre_id == genre_id)
        books = session.exec(stmt).all()
        import random
        return random.choice(books) if books else None

def get_user_recommendations(user_id: int):
    with get_session() as session:
        stmt = select(Recommendation).where(Recommendation.user_id == user_id)
        return session.exec(stmt).all()

def get_feedback_for_book(book_id: int):
    with get_session() as session:
        stmt = select(UserFeedback).where(UserFeedback.book_id == book_id)
        return session.exec(stmt).all()

