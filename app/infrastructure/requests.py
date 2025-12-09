from http.client import HTTPException
from typing import List

from sqlmodel import select

from app.infrastructure.db import get_session
from app.infrastructure.models import User, Book, Recommendation, UserFeedback, Genre, Author, Source, UserUpdate


def get_user_by_telegram_id(tg_id: int) -> User:
    with get_session() as session:
        statement = select(User).where(User.telegram_id == tg_id)
        return session.exec(statement).first()

def get_books() -> List[Book]:
    with get_session() as session:
        stmt = select(Book)
        books = session.exec(stmt).all()
        return books

def get_books_by_genre(genre_id: int) -> List[Book]:
    with get_session() as session:
        stmt = select(Book).where(Book.genre_id == genre_id)
        return session.exec(stmt).all()

def get_books_by_author(author_id: int) -> List[Book]:
    with get_session() as session:
        stmt = select(Book).where(Book.author_id == author_id)
        return session.exec(stmt).all()

def get_books_by_author_and_genre(author_id: int, genre_id: int) -> List[Book]:
    with get_session() as session:
        stmt = select(Book).where(Book.author_id == author_id, Book.genre_id == genre_id)
        return session.exec(stmt).all()

def get_random_book_by_genre(genre_id: int) -> Book:
    with get_session() as session:
        stmt = select(Book).where(Book.genre_id == genre_id)
        books = session.exec(stmt).all()

        if not books:
            return None

        import random
        random_book = random.choice(books)
        return random_book

def get_book_by_id(book_id: int) -> Book:
    with get_session() as session:
        stmt = select(Book).where(Book.id == book_id)
        return session.exec(stmt).first()

def get_user_recommendations(user_id: int) -> List[Recommendation]:
    with get_session() as session:
        stmt = select(Recommendation).where(Recommendation.user_id == user_id)
        return session.exec(stmt).all()

def get_feedback_for_book(book_id: int) -> List[UserFeedback]:
    with get_session() as session:
        stmt = select(UserFeedback).where(UserFeedback.book_id == book_id)
        return session.exec(stmt).all()

def post_genre(genre_id: int, genre_name: str) -> Genre:
    with get_session() as session:
        genre = Genre(id=genre_id, name=genre_name)
        session.add(genre)
        session.commit()
        session.refresh(genre)
        return genre

def get_genres() -> List[Genre]:
    with get_session() as session:
        stmt = select(Genre)
        genres = session.exec(stmt).all()
        return genres

def post_author(author_id: int, author_name: str) -> Author:
    with get_session() as session:
        author = Author(id=author_id, name=author_name)
        session.add(author)
        session.commit()
        session.refresh(author)
        return author

def get_authors() -> List[Author]:
    with get_session() as session:
        stmt = select(Author)
        authors = session.exec(stmt).all()
        return authors

def post_source(source_id: int, source_name: str) -> Source:
    with get_session() as session:
        source = Source(id=source_id, name=source_name)
        session.add(source)
        session.commit()
        session.refresh(source)
        return source

def get_sources() -> List[Source]:
    with get_session() as session:
        stmt = select(Source)
        sources = session.exec(stmt).all()
        return sources

def post_book(book: Book) -> Book:
    with get_session() as session:
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

def post_user(
        user_id: int,
        user_telegram_id: int,
        username: str
) -> User:
    with get_session() as session:
        user = User(
            id=user_id,
            telegram_id=user_telegram_id,
            username=username
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_recommendations(user_id: int, amount_of_recommendations: int = 3) -> List[Book]:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        liked = session.exec(
            select(UserFeedback).where(
                UserFeedback.user_id == user_id,
                UserFeedback.rating == "like"
            )
        ).all()

        books_candidates = []
        for fb in liked:
            book = session.get(Book, fb.book_id)
            if book:
                same_genre = session.exec(
                    select(Book).where(Book.genre_id == book.genre_id)
                ).all()
                books_candidates.extend(same_genre)

        unique_books = list({b.id: b for b in books_candidates}.values())

        result = unique_books[:amount_of_recommendations]

        for book in result:
            session.add(Recommendation(user_id=user_id, book_id=book.id))
        session.commit()

        return result

def post_feedback(
        feedback_id: int,
        user_id: int,
        book_id: int,
        rating: str
) -> UserFeedback:
    with get_session() as session:
        feedback = UserFeedback(id=feedback_id, user_id=user_id, book_id=book_id, rating=rating)
        if not session.get(User, feedback.user_id):
            raise HTTPException(status_code=400, detail="User not found")
        if not session.get(Book, feedback.book_id):
            raise HTTPException(status_code=400, detail="Book not found")

        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        return feedback

def delete_existing_user(user_id: int) -> User:
    with get_session() as session:
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        session.refresh(user)
        return user

def delete_existing_book(book_id: int) -> Book:
    with get_session() as session:
        book = session.get(Book, book_id)
        session.delete(book)
        session.commit()
        session.refresh(book)
        return book

def update_existing_user(user_id: int, new_data: UserUpdate) -> User:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = new_data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
