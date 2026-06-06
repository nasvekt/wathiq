"""
Wathiq — Database connection using Supabase REST API.
Lazy initialization — won't crash on import if Supabase is unavailable.
"""
from app.config import get_settings
import httpx


def _get_headers(use_admin: bool = False) -> dict:
    """Get Supabase headers lazily — not at module level."""
    settings = get_settings()
    key = settings.supabase_service_role_key if use_admin else settings.supabase_key
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


async def select(table: str, params: dict | None = None, use_admin: bool = False) -> list[dict]:
    settings = get_settings()
    headers = _get_headers(use_admin)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.supabase_url}/rest/v1/{table}",
            headers=headers, params=params, timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def insert(table: str, data: dict | list[dict], use_admin: bool = False) -> list[dict]:
    settings = get_settings()
    headers = _get_headers(use_admin)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.supabase_url}/rest/v1/{table}",
            headers=headers, json=data if isinstance(data, list) else [data], timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def update(table: str, data: dict, params: dict, use_admin: bool = False) -> list[dict]:
    settings = get_settings()
    headers = _get_headers(use_admin)
    headers["Prefer"] = "return=representation"
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.supabase_url}/rest/v1/{table}",
            headers=headers, params=params, json=data, timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def delete(table: str, params: dict, use_admin: bool = False) -> None:
    settings = get_settings()
    headers = _get_headers(use_admin)
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.supabase_url}/rest/v1/{table}",
            headers=headers, params=params, timeout=30,
        )
        response.raise_for_status()