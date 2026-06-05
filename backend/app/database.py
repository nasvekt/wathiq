"""
Wathiq — Database connection using Supabase REST API.
Provides async database helpers for API routes.
"""
from app.config import get_settings
import httpx

settings = get_settings()

supabase_rest_url = f"{settings.supabase_url}/rest/v1"
supabase_headers = {
    "apikey": settings.supabase_key,
    "Authorization": f"Bearer {settings.supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

admin_headers = {
    "apikey": settings.supabase_service_role_key,
    "Authorization": f"Bearer {settings.supabase_service_role_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


async def select(table: str, params: dict | None = None, use_admin: bool = False) -> list[dict]:
    """Query rows from a Supabase table."""
    headers = admin_headers if use_admin else supabase_headers
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{supabase_rest_url}/{table}",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def insert(table: str, data: dict | list[dict], use_admin: bool = False) -> list[dict]:
    """Insert rows into a Supabase table."""
    headers = admin_headers if use_admin else supabase_headers
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{supabase_rest_url}/{table}",
            headers=headers,
            json=data if isinstance(data, list) else [data],
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def update(table: str, data: dict, params: dict, use_admin: bool = False) -> list[dict]:
    """Update rows in a Supabase table."""
    headers = admin_headers if use_admin else supabase_headers
    headers["Prefer"] = "return=representation"
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{supabase_rest_url}/{table}",
            headers=headers,
            params=params,
            json=data,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def delete(table: str, params: dict, use_admin: bool = False) -> None:
    """Delete rows from a Supabase table."""
    headers = admin_headers if use_admin else supabase_headers
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{supabase_rest_url}/{table}",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()


async def rpc(function_name: str, params: dict | None = None) -> dict:
    """Call a Supabase RPC function."""
    headers = admin_headers
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.supabase_url}/rest/v1/rpc/{function_name}",
            headers=headers,
            json=params or {},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()


async def execute_sql(sql: str) -> dict:
    """Execute raw SQL via Supabase's pg_query RPC."""
    return await rpc("pg_query", {"query": sql})