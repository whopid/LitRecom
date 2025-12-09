from typing import Optional, List
import datetime

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True)
    username: Optional[str] = None
    reg_date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )

class UserUpdate(SQLModel):
    username: str | None = None

class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Source(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    link: Optional[str] = None

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author_id: Optional[int] = Field(foreign_key="author.id")
    genre_id: Optional[int] = Field(foreign_key="genre.id")
    description: Optional[str] = None
    source_id: Optional[int] = Field(foreign_key="source.id")

class Recommendation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )

class UserFeedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    rating: str
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )
