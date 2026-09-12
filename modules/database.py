"""Database client creation and non-sensitive health reporting."""

from __future__ import annotations

from dataclasses import dataclass

from modules.config import Settings


@dataclass(frozen=True)
class DatabaseStatus:
    label: str
    message: str
    is_ready: bool


def create_supabase_client(url: str, anon_key: str):
    """Create an isolated Supabase client for the current operation."""

    from supabase import create_client

    return create_client(url, anon_key)


def get_database_status(settings: Settings) -> DatabaseStatus:
    """Return a safe status without exposing credentials or making data writes."""

    if not settings.has_supabase_credentials:
        return DatabaseStatus(
            label="Offline demo mode",
            message=(
                "The interface is ready. Add Supabase credentials to enable the "
                "development database connection."
            ),
            is_ready=False,
        )

    try:
        create_supabase_client(settings.supabase_url or "", settings.supabase_anon_key or "")
    except Exception:
        return DatabaseStatus(
            label="Database configuration needs attention",
            message="Credentials were detected, but a client could not be created.",
            is_ready=False,
        )

    return DatabaseStatus(
        label="Database client configured",
        message="Supabase credentials were detected and the client was created successfully.",
        is_ready=True,
    )
