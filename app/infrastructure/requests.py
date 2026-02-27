from http.client import HTTPException
from typing import List
from collections import defaultdict

from sqlmodel import select, func

from app.infrastructure.db import get_session, add_to_db, delete_from_db
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

def post_genre(genre_name: str) -> Genre:
    with get_session() as session:
        genre = Genre(name=genre_name)
        add_to_db(session, genre)
        return genre

def get_genres() -> List[Genre]:
    with get_session() as session:
        stmt = select(Genre)
        genres = session.exec(stmt).all()
        return genres

def post_author(author_name: str) -> Author:
    with get_session() as session:
        author = Author(name=author_name)
        add_to_db(session, author)
        return author

def get_authors() -> List[Author]:
    with get_session() as session:
        stmt = select(Author)
        authors = session.exec(stmt).all()
        return authors

def post_source(source_name: str) -> Source:
    with get_session() as session:
        source = Source(name=source_name)
        add_to_db(session, source)
        return source

def get_sources() -> List[Source]:
    with get_session() as session:
        stmt = select(Source)
        sources = session.exec(stmt).all()
        return sources

def post_book(book: Book) -> Book:
    with get_session() as session:
        add_to_db(session, book)
        return book

def post_user(
        user_telegram_id: int,
        username: str
) -> User:
    with get_session() as session:
        user = User(
            telegram_id=user_telegram_id,
            username=username
        )
        add_to_db(session, user)
        return user

def get_recommendations(user_id: int, amount_of_recommendations: int = 3) -> List[Book]:
    with get_session() as session:

        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        liked_genres_stmt = (
            select(
                Book.genre_id,
                func.count(UserFeedback.id).label("weight")
            )
            .join(UserFeedback, UserFeedback.book_id == Book.id)
            .where(
                UserFeedback.user_id == user_id,
                UserFeedback.rating == "like",
                Book.genre_id.is_not(None)
            )
            .group_by(Book.genre_id)
        )

        genre_weights = {
            genre_id: weight
            for genre_id, weight in session.exec(liked_genres_stmt).all()
        }

        seen_books_stmt = (
            select(UserFeedback.book_id)
            .where(UserFeedback.user_id == user_id)
        )

        seen_books = set(session.exec(seen_books_stmt).all())

        popularity_subq = (
            select(
                UserFeedback.book_id,
                func.count(UserFeedback.id).label("popularity")
            )
            .where(UserFeedback.rating == "like")
            .group_by(UserFeedback.book_id)
        ).subquery()

        stmt = ( #TODO: тут не stmt, а запрос к api
            select(
                Book,
                func.coalesce(popularity_subq.c.popularity, 0).label("popularity")
            )
            .join(
                popularity_subq,
                popularity_subq.c.book_id == Book.id,
                isouter=True
            )
            .where(Book.id.notin_(seen_books))
        )

        books_with_popularity = session.exec(stmt).all()

        if not genre_weights:
            popular_books = sorted(
                books_with_popularity,
                key=lambda x: x[1],
                reverse=True
            )
            result_books = [book for book, _ in popular_books[:amount_of_recommendations]]

        else:
            scored_books = []

            for book, popularity in books_with_popularity:
                genre_weight = genre_weights.get(book.genre_id, 0)
                score = genre_weight * 0.7 + popularity * 0.3 #TODO: подумать над коэффициентами
                scored_books.append((book, score))

            scored_books.sort(key=lambda x: x[1], reverse=True)

            sorted_books = [book for book, _ in scored_books]

            result_books = []
            genre_streak = defaultdict(int)

            for book in sorted_books:
                genre = book.genre_id

                if genre_streak[genre] < 2:
                    result_books.append(book)
                    genre_streak[genre] += 1

                for g in genre_streak:
                    if g != genre:
                        genre_streak[g] = 0

                if len(result_books) >= amount_of_recommendations:
                    break

            if len(result_books) < amount_of_recommendations:
                for book in sorted_books:
                    if book not in result_books:
                        result_books.append(book)
                    if len(result_books) >= amount_of_recommendations:
                        break

        for book in result_books:
            session.add(Recommendation(user_id=user_id, book_id=book.id))

        session.commit()

        return [book.model_dump() for book in result_books]

def post_feedback(
        user_id: int,
        book_id: int,
        rating: str
) -> UserFeedback:
    with get_session() as session:
        feedback = UserFeedback(user_id=user_id, book_id=book_id, rating=rating)
        if not session.get(User, feedback.user_id):
            raise HTTPException(status_code=400, detail="User not found")
        if not session.get(Book, feedback.book_id):
            raise HTTPException(status_code=400, detail="Book not found")

        add_to_db(session, feedback)
        return feedback

def delete_existing_user(user_id: int) -> User:
    with get_session() as session:
        user = session.get(User, user_id)
        delete_from_db(session, user)
        return user

def delete_existing_book(book_id: int) -> Book:
    with get_session() as session:
        book = session.get(Book, book_id)
        delete_from_db(session, book)
        return book

def update_existing_user(user_id: int, new_data: UserUpdate) -> User:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = new_data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        add_to_db(session, user)
        return user
