"""Authentication and session management for live and demo modes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import streamlit as st

from modules.config import Settings
from modules.database import create_supabase_client


ALLOWED_PUBLIC_ROLES = {"student", "business"}
SESSION_KEY = "auth_user"
TOKEN_KEY = "auth_tokens"


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str
    role: str
    full_name: str
    mode: str = "live"


@dataclass(frozen=True)
class AuthResult:
    success: bool
    message: str
    user: AuthUser | None = None
    requires_email_confirmation: bool = False


def _safe_role(value: str | None) -> str:
    role = (value or "").strip().lower()
    return role if role in ALLOWED_PUBLIC_ROLES else "student"


def _user_from_supabase(raw_user: Any, fallback_role: str = "student") -> AuthUser:
    metadata = getattr(raw_user, "user_metadata", None) or {}
    return AuthUser(
        id=str(raw_user.id),
        email=str(raw_user.email or ""),
        role=_safe_role(metadata.get("role") or fallback_role),
        full_name=str(metadata.get("full_name") or "User"),
        mode="live",
    )


def set_current_user(user: AuthUser, session: Any | None = None) -> None:
    st.session_state[SESSION_KEY] = asdict(user)
    if session is not None:
        st.session_state[TOKEN_KEY] = {
            "access_token": str(session.access_token),
            "refresh_token": str(session.refresh_token),
        }


def get_current_user() -> AuthUser | None:
    value = st.session_state.get(SESSION_KEY)
    if not isinstance(value, dict):
        return None
    try:
        return AuthUser(**value)
    except TypeError:
        st.session_state.pop(SESSION_KEY, None)
        return None


def logout(settings: Settings) -> None:
    user = get_current_user()
    if user and user.mode == "live" and settings.has_supabase_credentials:
        try:
            client = create_supabase_client(
                settings.supabase_url or "", settings.supabase_anon_key or ""
            )
            tokens = st.session_state.get(TOKEN_KEY, {})
            if tokens.get("access_token") and tokens.get("refresh_token"):
                client.auth.set_session(tokens["access_token"], tokens["refresh_token"])
            client.auth.sign_out()
        except Exception:
            pass
    st.session_state.pop(SESSION_KEY, None)
    st.session_state.pop(TOKEN_KEY, None)
    st.session_state.pop("demo_profiles", None)


def get_authenticated_client(settings: Settings):
    """Create a Supabase client bound only to the current browser session."""

    if not settings.has_supabase_credentials:
        raise RuntimeError("Supabase is not configured")
    tokens = st.session_state.get(TOKEN_KEY, {})
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    if not access_token or not refresh_token:
        raise RuntimeError("No authenticated Supabase session")

    client = create_supabase_client(
        settings.supabase_url or "", settings.supabase_anon_key or ""
    )
    response = client.auth.set_session(access_token, refresh_token)
    if response and getattr(response, "session", None):
        st.session_state[TOKEN_KEY] = {
            "access_token": str(response.session.access_token),
            "refresh_token": str(response.session.refresh_token),
        }
    return client


def register(
    settings: Settings,
    full_name: str,
    email: str,
    password: str,
    role: str,
) -> AuthResult:
    clean_role = _safe_role(role)
    if role.lower() not in ALLOWED_PUBLIC_ROLES:
        return AuthResult(False, "Choose either Student or Business.")
    if len(full_name.strip()) < 2:
        return AuthResult(False, "Enter your full name.")
    if "@" not in email:
        return AuthResult(False, "Enter a valid email address.")
    if len(password) < 8:
        return AuthResult(False, "Password must contain at least eight characters.")
    if not settings.has_supabase_credentials:
        return AuthResult(
            False,
            "Account registration needs a connected Supabase project. Use a demo login to preview the dashboards.",
        )

    try:
        client = create_supabase_client(
            settings.supabase_url or "", settings.supabase_anon_key or ""
        )
        response = client.auth.sign_up(
            {
                "email": email.strip().lower(),
                "password": password,
                "options": {
                    "data": {"full_name": full_name.strip(), "role": clean_role}
                },
            }
        )
    except Exception:
        return AuthResult(False, "Registration could not be completed. Check the details or try again.")

    if not response.user:
        return AuthResult(False, "Registration did not return a user account.")

    user = _user_from_supabase(response.user, clean_role)
    if response.session:
        set_current_user(user, response.session)
        return AuthResult(True, "Account created successfully.", user=user)

    return AuthResult(
        True,
        "Account created. Check your email to confirm it before signing in.",
        user=user,
        requires_email_confirmation=True,
    )


def login(settings: Settings, email: str, password: str) -> AuthResult:
    if not settings.has_supabase_credentials:
        return AuthResult(False, "Live login needs a connected Supabase project.")
    if not email.strip() or not password:
        return AuthResult(False, "Enter your email address and password.")

    try:
        client = create_supabase_client(
            settings.supabase_url or "", settings.supabase_anon_key or ""
        )
        response = client.auth.sign_in_with_password(
            {"email": email.strip().lower(), "password": password}
        )
    except Exception:
        return AuthResult(False, "Login failed. Check your email address and password.")

    if not response.user or not response.session:
        return AuthResult(False, "Login did not create an active session.")

    user = _user_from_supabase(response.user)
    set_current_user(user, response.session)
    return AuthResult(True, "Welcome back.", user=user)


def start_demo_session(role: str) -> AuthUser:
    clean_role = _safe_role(role)
    user = AuthUser(
        id=f"demo-{clean_role}",
        email=f"demo.{clean_role}@skillbridge.local",
        role=clean_role,
        full_name="Demo Student" if clean_role == "student" else "Demo Business Owner",
        mode="demo",
    )
    set_current_user(user)
    return user
