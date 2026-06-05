"""
Wathiq — Supabase Client Initialization
Provides a singleton Supabase client for database operations.
"""

from supabase import create_client, Client
from app.config import get_settings

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """
    Get or create the Supabase client singleton.

    Returns:
        Supabase Client instance

    Raises:
        RuntimeError: If SUPABASE_URL or SUPABASE_KEY is not configured
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY in .env"
        )

    _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client


def get_supabase_admin() -> Client:
    """
    Get a Supabase client with service role key for admin operations.
    Bypasses RLS policies. Use with caution.

    Returns:
        Supabase Client instance with service role privileges

    Raises:
        RuntimeError: If SUPABASE_SERVICE_ROLE_KEY is not configured
    """
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError(
            "Supabase admin is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
        )

    return create_client(settings.supabase_url, settings.supabase_service_role_key)
