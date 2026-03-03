import random

import httpx
from typing import List, Dict, Any

from env import GOOGLE_BOOKS_API_KEY


BASE_URL = "https://www.googleapis.com/books/v1/volumes"

async def search_books(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    params = {
        "q": query,
        "maxResults": max_results,
    }

    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL, params=params)
        data = r.json()

    books = []

    for item in data.get("items", []):
        volume = item["volumeInfo"]

        books.append(
            {
                "google_id": item["id"],
                "title": volume.get("title"),
                "authors": volume.get("authors", []),
                "genres": volume.get("categories", ["Unknown"]),
                "description": volume.get("description"),
            }
        )

    return books

async def get_books_by_genre(genre: str, max_results: int = 20)-> List[Dict[str, Any]]:
    params = {
        "q": f"subject:{genre}",
        "maxResults": max_results,
        "printType": "books",
        "langRestrict": "ru",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        data = response.json()

    books = []

    for item in data.get("items", []):
        volume = item.get("volumeInfo", {})

        books.append(
            {
                "google_book_id": item.get("id"),
                "title": volume.get("title"),
                "genre": genre,
            }
        )

    return books


async def get_random_book(genre: str) -> Dict[str, Any] | None:
    books = await get_books_by_genre(genre)

    if not books:
        return None

    return random.choice(books)
