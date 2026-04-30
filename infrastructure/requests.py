from typing import List, Dict, Tuple
from collections import defaultdict

from fastapi import HTTPException
from sqlmodel import select, func, exists
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models import (
    User,
    Recommendation,
    UserFeedback,
    Genre,
    UserUpdate, UserPreference,
)
from services.google_books_api import get_books_by_genre


async def get_user_by_telegram_id(telegram_id: int, session: AsyncSession) -> User | None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalars().first()

async def create_user(telegram_id: int, username: str | None, session: AsyncSession) -> User:
    user = User(telegram_id=telegram_id, username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def delete_existing_user(user_id: int, session: AsyncSession) -> User:
    user = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = user.scalars().first()
    await session.delete(user)
    await session.commit()
    return user

async def get_genres(session: AsyncSession) -> List[Genre]:
    result = await session.execute(select(Genre))
    genres = result.scalars().all()

    return genres

async def get_genre_by_name(genre_name: str, session: AsyncSession) -> Genre:
    result = await session.execute(
        select(Genre).where(func.lower(Genre.name) == genre_name.lower())
    )
    genre = result.scalars().first()
    return genre

async def get_genre_by_id(genre_id: int, session: AsyncSession) -> Genre:
    result = await session.execute(select(Genre).where(Genre.id == genre_id))
    genre = result.scalars().first()

    return genre

async def create_genre(genre_name: str, session: AsyncSession) -> Genre:
    genre = Genre(name=genre_name)
    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre

async def post_feedback(
    user_id: int,
    genre_name: str,
    rating: str,
    session: AsyncSession,
    google_book_id: str | None = None,
    title: str | None = None
) -> UserFeedback:
    genre = await get_genre_by_name(genre_name, session)

    if not genre:
        genre = await create_genre(genre_name, session)

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

async def create_preference(
    user_id: int,
    genre_id: int
) -> UserPreference:
    preference = UserPreference(user_id=user_id, genre_id=genre_id)
    return preference

async def get_all_feedbacks(user_id: int, session: AsyncSession) -> List[UserFeedback]:
    result = await session.execute(
        select(UserFeedback).where(UserFeedback.user_id == user_id)
    )
    feedbacks = result.scalars().all()
    return feedbacks

async def get_user_preferences(user_id: int, session: AsyncSession) -> List[UserPreference]:
    result = await session.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    preferences = result.scalars().all()
    return preferences

async def delete_feedbacks_and_preferences(user_id: int, session: AsyncSession) -> List[UserPreference]:
    result = await session.execute(
        select(UserFeedback).where(UserFeedback.user_id == user_id)
    )
    feedbacks = result.scalars().all()

    result = await session.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    preferences = result.scalars().all()

    for feedback in feedbacks:
        await session.delete(feedback)

    for preference in preferences:
        await session.delete(preference)

    await session.commit()

    return preferences

async def get_user_profile_weights(
    user_id: int,
    session: AsyncSession
) -> Dict[int, float]:

    weights = defaultdict(float)

    pref_stmt = (
        select(UserPreference.genre_id)
        .where(UserPreference.user_id == user_id)
    )

    pref_rows = await session.execute(pref_stmt)

    for genre_id in pref_rows.scalars().all():
        weights[genre_id] += 5.0

    feedback_stmt = (
        select(
            UserFeedback.genre_id,
            func.count(UserFeedback.id)
        )
        .where(
            UserFeedback.user_id == user_id,
            UserFeedback.rating == "like",
        )
        .group_by(UserFeedback.genre_id)
    )

    feedback_rows = await session.execute(feedback_stmt)

    for genre_id, count in feedback_rows.all():
        weights[genre_id] += count * 2

    return dict(weights)

async def get_genres_popularity(session: AsyncSession) -> Dict[int, int]:
    stmt = (
        select(
            UserFeedback.genre_id,
            func.count(UserFeedback.id).label("popularity"),
        )
        .where(UserFeedback.rating == "like")
        .group_by(UserFeedback.genre_id)
    )

    rows = await session.execute(stmt)
    return {genre_id: popularity for genre_id, popularity in rows.all()}

async def update_existing_user(user_id: int, username: str, session: AsyncSession) -> User:
    user = await validate_user(user_id, session)
    new_data = UserUpdate(username=username)

    for key, value in new_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)

    return user

async def get_recommendations(
    user_id: int,
    session: AsyncSession,
    amount: int = 3
) -> List[Dict]:
    await validate_user(user_id, session)

    genre_weights = await get_user_profile_weights(user_id, session)

    genre_popularity = await get_genres_popularity(session)

    shown_ids = await get_shown_books(user_id, session)

    genres = await get_top_genres(
        genre_weights=genre_weights,
        genre_popularity=genre_popularity,
        session=session
    )
    all_books = []
    for genre in genres:
        books = await get_books_by_genre(genre, max_results=40)
        all_books.extend(books)

    unique_books = {}

    for book in all_books:

        google_id = book["google_book_id"]

        if google_id not in unique_books:
            unique_books[google_id] = book

    books = list(unique_books.values())

    scored_books = await score_books(
        books=books,
        session=session,
        shown_ids=shown_ids,
        genre_weights=genre_weights,
        genre_popularity=genre_popularity,
    )

    result = pick_best_books(scored_books, amount)

    if not result:
        books = await get_books_by_genre(
            "fiction",
            max_results=20
        )

        return books[:amount]

    await save_recommendations(
        user_id,
        result,
        session
    )

    return [book for book, _ in result]

async def validate_user(
    user_id: int,
    session: AsyncSession
) -> User:
    user = await session.execute(
        select(User).where(User.id == user_id)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.scalar_one_or_none()

async def get_top_genres(
    session: AsyncSession,
    genre_weights: Dict[int, float],
    genre_popularity: Dict[int, int],
    limit: int = 3
) -> List[str]:

    if not genre_weights:
        if genre_popularity:
            sorted_popular = sorted(
                genre_popularity.items(),
                key=lambda x: x[1],
                reverse=True
            )
            genre_ids = [
                genre_id
                for genre_id, _ in sorted_popular[:limit]
            ]
        else:
            return ["fiction"]
    else:
        sorted_weights = sorted(
            genre_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        genre_ids = [
            genre_id
            for genre_id, _ in sorted_weights[:limit]
        ]

    genres = []

    for genre_id in genre_ids:
        genre = await get_genre_by_id(
            genre_id,
            session
        )
        if genre:
            genres.append(genre.name)

    return genres

async def get_shown_books(
    user_id: int,
    session: AsyncSession
) -> set:
    stmt = (
        select(Recommendation.google_book_id)
        .where(Recommendation.user_id == user_id)
        .order_by(Recommendation.id.desc())
        .limit(30)
    )

    rows = await session.execute(stmt)

    return set(rows.scalars().all())

async def score_books(
    books: List[Dict],
    shown_ids: set,
    genre_weights: Dict[int, float],
    genre_popularity: Dict[int, int],
    session: AsyncSession,
) -> List[Dict]:

    scored_books = []

    for book in books:
        google_id = book["google_book_id"]
        if google_id in shown_ids:
            continue

        genre_name = book.get("genre", "")
        genre = await get_genre_by_name(
            genre_name,
            session
        )

        if not genre:
            genre = await create_genre(
                genre_name,
                session
            )

        user_weight = genre_weights.get(genre.id, 0)
        popularity = genre_popularity.get(genre.id, 0)

        score = user_weight * 0.7 + popularity * 0.3

        scored_books.append((book, genre, score))

    scored_books.sort(
        key=lambda x: x[2],
        reverse=True
    )

    return scored_books

def pick_best_books(
    scored_books,
    amount: int
) -> List[Tuple]:

    result = []
    genre_streak = defaultdict(int)

    for book, genre, score in scored_books:

        if genre_streak[genre.id] < 2:

            result.append((book, genre))

            genre_streak[genre.id] += 1

        for g in genre_streak:

            if g != genre.id:
                genre_streak[g] = 0

        if len(result) >= amount:
            break

    return result

async def save_recommendations(
    user_id: int,
    result,
    session: AsyncSession
):

    for book, genre in result:

        rec = Recommendation(
            user_id=user_id,
            google_book_id=book["google_book_id"],
            genre_id=genre.id,
        )

        session.add(rec)

    await session.commit()
