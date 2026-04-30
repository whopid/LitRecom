import asyncio
import random

import httpx
from typing import List, Dict, Any

from env import GOOGLE_BOOKS_API_KEY


BASE_URL = "https://www.googleapis.com/books/v1/volumes"

async def search_books(query: str, max_results: int = 40) -> List[Dict[str, Any]]:
    url = f"{BASE_URL}?q=intitle:{query}&maxResults={max_results}&langRestrict=ru&key={GOOGLE_BOOKS_API_KEY}"
    books_info = await get_info_from_url(url)
    return books_info

async def get_books_by_genre(genre: str, max_results: int = 40)-> List[Dict[str, Any]]:
    url = f"{BASE_URL}?q=subject:{genre}&maxResults={max_results}&langRestrict=ru&key={GOOGLE_BOOKS_API_KEY}"

    books_info = await get_info_from_url(url)
    return books_info

async def get_random_book_by_genre(genre: str) -> Dict[str, Any] | None:
    books = await get_books_by_genre(genre)

    if not books:
        return None

    return random.choice(books)

async def get_book_by_id(google_book_id: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/{google_book_id}?key={GOOGLE_BOOKS_API_KEY}"
    book_info = await get_info_from_url(url)
    return book_info[0]

async def get_info_from_url(
        url: str,
        retries: int = 3,
        delay: float = 1.5
) -> List[Dict[str, Any]]:
    for attempt in range(retries):

        try:
            async with httpx.AsyncClient(timeout=10) as client:

                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            books_info = []

            items = data.get("items", [data])

            for item in items:

                volume = item.get("volumeInfo", {})

                thumbnail = (
                    volume.get("imageLinks", {})
                    .get("thumbnail")
                )

                if thumbnail:
                    thumbnail = thumbnail.replace(
                        "http://",
                        "https://"
                    )

                description = volume.get("description")

                if description:
                    description = description[:800]

                books_info.append(
                    {
                        "google_book_id": item.get("id"),
                        "title": volume.get("title", "Без названия"),
                        "author": volume.get("authors", []),
                        "genre": volume.get("categories", ["Unknown"])[0],
                        "description": description,
                        "thumbnail": thumbnail,
                    }
                )
            return books_info
        except(
            httpx.RequestError,
            httpx.HTTPStatusError,
        ) as e:
            if attempt == retries - 1:
                raise e

            await asyncio.sleep(delay)

    return []
