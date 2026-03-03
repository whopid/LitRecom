from typing import List, Dict, Any
from collections import defaultdict

from fastapi import HTTPException
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db import async_session_maker
from app.infrastructure.models import (
    User,
    Recommendation,
    UserFeedback,
    Genre,
    UserUpdate,
)

from services.api import get_random_book, search_books


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    async with async_session_maker() as session:
        result = await session.exec(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.first()

async def create_user(telegram_id: int, username: str | None) -> User:
    async with async_session_maker() as session:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def delete_existing_user(user_id: int) -> User:
    async with async_session_maker() as session:
        user = session.get(User, user_id)
        await session.delete(user)
        await session.commit()
        return user

async def get_or_create_genre(genre_name: str) -> Genre:
    async with async_session_maker() as session:
        result = await session.exec(
            select(Genre).where(Genre.name == genre_name)
        )
        genre = result.first()

        if genre:
            return genre

        genre = Genre(name=genre_name)
        session.add(genre)
        await session.commit()
        await session.refresh(genre)
        return genre

async def post_feedback(
    user_id: int,
    google_book_id: str,
    title: str,
    genre_name: str,
    rating: str,
) -> UserFeedback:
    async with async_session_maker() as session:

        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        genre = await get_or_create_genre(genre_name)

        feedback = UserFeedback(
            user_id=user_id,
            google_book_id=google_book_id,
            title=title,
            genre_id=genre.id,
            rating=rating,
        )

        session.add(feedback)
        await session.commit()
        await session.refresh(feedback)

        return feedback

async def get_user_genre_weights(user_id: int) -> Dict[int, int]:
    async with async_session_maker() as session:
        stmt = (
            select(
                UserFeedback.genre_id,
                func.count(UserFeedback.id).label("weight"),
            )
            .where(
                UserFeedback.user_id == user_id,
                UserFeedback.rating == "like",
            )
            .group_by(UserFeedback.genre_id)
        )

        rows = await session.exec(stmt)

        return {genre_id: weight for genre_id, weight in rows.all()}

async def get_genres_popularity() -> Dict[int, int]:
    async with async_session_maker() as session:
        stmt = (
            select(
                UserFeedback.genre_id,
                func.count(UserFeedback.id).label("popularity"),
            )
            .where(UserFeedback.rating == "like")
            .group_by(UserFeedback.genre_id)
        )

        rows = await session.exec(stmt)
        return {genre_id: popularity for genre_id, popularity in rows.all()}

async def get_recommendations(
    user_id: int,
    amount: int = 3,
) -> List[Dict]:
    async with async_session_maker() as session:

        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        genre_weights = await get_user_genre_weights(user_id)

        genre_popularity = await get_genres_popularity()

        shown_stmt = select(Recommendation.google_book_id).where(
            Recommendation.user_id == user_id
        )
        shown_rows = await session.exec(shown_stmt)
        shown_ids = set(shown_rows.all())

        if not genre_weights:
            if genre_popularity:
                top_genre_id = max(
                    genre_popularity, key=genre_popularity.get
                )
                genre = await session.get(Genre, top_genre_id)
                query = genre.name
            else:
                query = "fiction"
        else:
            top_genre_id = max(genre_weights, key=genre_weights.get)
            genre = await session.get(Genre, top_genre_id)
            query = genre.name

        books = await search_books(query, max_results=20)

        scored_books = []

        for book in books:
            google_id = book["google_id"]

            if google_id in shown_ids:
                continue

            genre_name = book["genres"][0]
            genre = await get_or_create_genre(genre_name)

            user_weight = genre_weights.get(genre.id, 0)
            popularity = genre_popularity.get(genre.id, 0)

            score = user_weight * 0.7 + popularity * 0.3

            scored_books.append((book, genre, score))

        scored_books.sort(key=lambda x: x[2], reverse=True)

        result = []
        genre_streak = defaultdict(int)

        for book, genre, _ in scored_books:
            if genre_streak[genre.id] < 2:
                result.append((book, genre))
                genre_streak[genre.id] += 1

            for g in genre_streak:
                if g != genre.id:
                    genre_streak[g] = 0

            if len(result) >= amount:
                break

        if len(result) < amount:
            for book, genre, _ in scored_books:
                if (book, genre) not in result:
                    result.append((book, genre))
                if len(result) >= amount:
                    break

        for book, genre in result:
            rec = Recommendation(
                user_id=user_id,
                google_book_id=book["google_id"],
                genre_id=genre.id,
            )
            session.add(rec)

        await session.commit()

        return [book for book, _ in result]

async def update_existing_user(user_id: int, new_data: UserUpdate) -> User:
    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        for key, value in new_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user

async def get_random_book_by_genre(user_id: int, genre_id: int) -> Recommendation | None:
    async with async_session_maker() as session:

        genre = await session.get(Genre, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        book = await get_random_book(genre.name)

        if not book:
            return None

        recommendation = Recommendation(
            user_id=user_id,
            google_book_id=book["google_book_id"],
            genre_id=genre_id,
        )

        await session.add(recommendation)
        await session.commit()
        await session.refresh(recommendation)

        return recommendation  #TODO: что-то покрасивее вернуть надо наверное
