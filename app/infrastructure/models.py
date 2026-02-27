import datetime

from sqlmodel import SQLModel, Field


# tables
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
    google_book_id: str
    title: str
    genre_id: int = Field(foreign_key="genre.id")
    rating: str #like/dislike
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# response models
# TODO: посмотреть что в итоге окажется нужным, а ненужное убрать
class UserRead(SQLModel):
    id: int
    telegram_id: int
    username: str | None
    reg_date: datetime.datetime

class GenreRead(SQLModel):
    id: int
    name: str

class RecommendationRead(SQLModel):
    id: int | None
    user_id: int
    google_book_id: str
    genre_id: int
    timestamp: datetime.datetime

class UserFeedbackRead(SQLModel, table=True):
    id: int | None
    user_id: int
    google_book_id: str
    title: str
    genre_id: int
    rating: str
    timestamp: datetime.datetime
