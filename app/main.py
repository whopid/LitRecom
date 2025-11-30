from db import get_session, create_db
from app.models import Genre, Author, Source, Book


def fill_minimal_data():
    with get_session() as session:
        genre_fantasy = Genre(name="Фантастика")
        genre_detective = Genre(name="Детектив")
        author = Author(name="Айзек Азимов")
        api_source = Source(name="Google Books", link="https://books.google.com")

        session.add_all([genre_fantasy, genre_detective, author, api_source])
        session.commit()

        book = Book(
            title="Основание",
            author_id=author.id,
            genre_id=genre_fantasy.id,
            description="...",
            source_id=api_source.id,
        )

        session.add(book)
        session.commit()

if __name__ == "__main__":
    create_db()
    fill_minimal_data()
    print("Успешно")