"""Student and business profile storage for live and demo modes."""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.auth import AuthUser, get_authenticated_client
from modules.config import Settings


def _client(settings: Settings):
    return get_authenticated_client(settings)


def _demo_store() -> dict[str, dict[str, Any]]:
    return st.session_state.setdefault("demo_profiles", {})


def get_profile(settings: Settings, user: AuthUser) -> dict[str, Any]:
    if user.mode == "demo":
        return _demo_store().get(user.id, {})

    table = "student_profiles" if user.role == "student" else "business_profiles"
    key = "user_id"
    try:
        base_result = (
            _client(settings).table("profiles").select("full_name,phone,location").eq("id", user.id).maybe_single().execute()
        )
        detail_result = (
            _client(settings).table(table).select("*").eq(key, user.id).maybe_single().execute()
        )
        return {**(base_result.data or {}), **(detail_result.data or {})}
    except Exception:
        return {}


def save_student_profile(
    settings: Settings, user: AuthUser, values: dict[str, Any]
) -> tuple[bool, str]:
    clean = {
        "full_name": values.get("full_name", "").strip(),
        "phone": values.get("phone", "").strip() or None,
        "location": values.get("location", "").strip() or None,
        "education": values.get("education", "").strip() or None,
        "skills": values.get("skills", []),
        "tools": values.get("tools", []),
        "experience_level": values.get("experience_level") or None,
        "bio": values.get("bio", "").strip() or None,
        "portfolio_url": values.get("portfolio_url", "").strip() or None,
        "linkedin_url": values.get("linkedin_url", "").strip() or None,
        "availability": values.get("availability", "").strip() or None,
    }
    if len(clean["full_name"]) < 2:
        return False, "Enter your full name."

    if user.mode == "demo":
        _demo_store()[user.id] = clean
        return True, "Demo profile saved for this browser session."

    try:
        client = _client(settings)
        client.table("profiles").update(
            {
                "full_name": clean["full_name"],
                "phone": clean["phone"],
                "location": clean["location"],
            }
        ).eq("id", user.id).execute()
        client.table("student_profiles").upsert(
            {
                "user_id": user.id,
                **{k: v for k, v in clean.items() if k not in {"full_name", "phone", "location"}},
            },
            on_conflict="user_id",
        ).execute()
    except Exception:
        return False, "The profile could not be saved. Please try again."
    return True, "Student profile saved successfully."


def save_business_profile(
    settings: Settings, user: AuthUser, values: dict[str, Any]
) -> tuple[bool, str]:
    clean = {
        "full_name": values.get("full_name", "").strip(),
        "phone": values.get("phone", "").strip() or None,
        "location": values.get("location", "").strip() or None,
        "business_name": values.get("business_name", "").strip(),
        "industry": values.get("industry", "").strip() or None,
        "description": values.get("description", "").strip() or None,
        "address": values.get("address", "").strip() or None,
    }
    if len(clean["full_name"]) < 2 or len(clean["business_name"]) < 2:
        return False, "Enter the contact person's name and business name."

    if user.mode == "demo":
        _demo_store()[user.id] = {**clean, "verification_status": "pending"}
        return True, "Demo business profile saved for this browser session."

    try:
        client = _client(settings)
        client.table("profiles").update(
            {
                "full_name": clean["full_name"],
                "phone": clean["phone"],
                "location": clean["location"],
            }
        ).eq("id", user.id).execute()
        client.table("business_profiles").upsert(
            {
                "user_id": user.id,
                **{k: v for k, v in clean.items() if k not in {"full_name", "phone", "location"}},
            },
            on_conflict="user_id",
        ).execute()
    except Exception:
        return False, "The business profile could not be saved. Please try again."
    return True, "Business profile saved and submitted for verification."


def profile_completion(user: AuthUser, profile: dict[str, Any]) -> int:
    if user.role == "student":
        fields = ("full_name", "location", "education", "skills", "tools", "bio", "availability")
    else:
        fields = ("full_name", "location", "business_name", "industry", "description", "address")
    completed = sum(bool(profile.get(field)) for field in fields)
    return round(completed / len(fields) * 100)
