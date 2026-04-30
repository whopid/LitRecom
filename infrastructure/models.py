import datetime

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True)
    username: str | None = None
    reg_date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class UserUpdate(SQLModel):
    username: str | None = None

class Genre(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Recommendation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    google_book_id: str
    genre_id: int = Field(foreign_key="genre.id")
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )

class UserFeedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    google_book_id: str | None = None
    title: str| None = None
    genre_id: int = Field(foreign_key="genre.id")
    rating: str #like/dislike
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class UserPreference(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    genre_id: int = Field(foreign_key="genre.id")
