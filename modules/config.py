"""Application configuration with safe environment handling."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Non-secret application settings and optional connection credentials."""

    app_env: str
    app_name: str
    app_location: str
    supabase_url: str | None
    supabase_anon_key: str | None

    @property
    def has_supabase_credentials(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once without logging or displaying secrets."""

    return Settings(
        app_env=os.getenv("APP_ENV", "development").strip(),
        app_name=os.getenv("APP_NAME", "SkillBridge Local").strip(),
        app_location=os.getenv(
            "APP_LOCATION", "Calabar, Cross River State"
        ).strip(),
        supabase_url=_clean_optional(os.getenv("SUPABASE_URL")),
        supabase_anon_key=_clean_optional(os.getenv("SUPABASE_ANON_KEY")),
    )

