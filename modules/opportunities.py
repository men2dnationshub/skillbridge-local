"""Business verification and opportunity workflows for Milestone 3."""

from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from modules.auth import AuthUser, get_authenticated_client
from modules.config import Settings


WORK_ARRANGEMENTS = ("On-site", "Remote", "Hybrid")
COMPENSATION_TYPES = ("Paid", "Stipend", "Unpaid")


def _demo_opportunities() -> list[dict[str, Any]]:
    return st.session_state.setdefault("demo_opportunities", [])


def validate_opportunity(values: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    """Validate and normalise an opportunity before storage."""

    clean = {
        "title": str(values.get("title", "")).strip(),
        "description": str(values.get("description", "")).strip(),
        "skills_required": [
            item.strip() for item in values.get("skills_required", []) if str(item).strip()
        ],
        "location": str(values.get("location", "")).strip(),
        "work_arrangement": str(values.get("work_arrangement", "On-site")).strip(),
        "compensation_type": str(values.get("compensation_type", "Unpaid")).strip(),
        "compensation_amount": values.get("compensation_amount"),
        "duration_weeks": int(values.get("duration_weeks") or 0),
        "application_deadline": values.get("application_deadline"),
    }
    if len(clean["title"]) < 5:
        return False, "Enter a clear opportunity title of at least five characters.", clean
    if len(clean["description"]) < 30:
        return False, "Describe the project in at least 30 characters.", clean
    if not clean["skills_required"]:
        return False, "Add at least one required skill.", clean
    if not clean["location"]:
        return False, "Enter the project location.", clean
    if clean["work_arrangement"] not in WORK_ARRANGEMENTS:
        return False, "Choose a valid work arrangement.", clean
    if clean["compensation_type"] not in COMPENSATION_TYPES:
        return False, "Choose a valid compensation type.", clean
    if clean["duration_weeks"] < 1 or clean["duration_weeks"] > 52:
        return False, "Duration must be between 1 and 52 weeks.", clean
    deadline = clean["application_deadline"]
    if not isinstance(deadline, date) or deadline < date.today():
        return False, "Choose today or a future application deadline.", clean
    if clean["compensation_type"] in {"Paid", "Stipend"}:
        try:
            clean["compensation_amount"] = float(clean["compensation_amount"])
        except (TypeError, ValueError):
            return False, "Enter the compensation amount.", clean
        if clean["compensation_amount"] <= 0:
            return False, "Compensation must be greater than zero.", clean
    else:
        clean["compensation_amount"] = None
    return True, "", clean


def create_opportunity(
    settings: Settings, user: AuthUser, values: dict[str, Any], submit: bool = False
) -> tuple[bool, str]:
    valid, message, clean = validate_opportunity(values)
    if not valid:
        return False, message

    status = "pending_review" if submit else "draft"
    record = {
        **clean,
        "business_id": user.id,
        "status": status,
        "application_deadline": clean["application_deadline"].isoformat(),
        "work_arrangement": clean["work_arrangement"].lower().replace("-", "_"),
        "compensation_type": clean["compensation_type"].lower(),
    }
    if user.mode == "demo":
        record["id"] = f"demo-opportunity-{len(_demo_opportunities()) + 1}"
        _demo_opportunities().append(record)
        return True, "Demo opportunity submitted for review." if submit else "Demo draft saved."

    try:
        get_authenticated_client(settings).table("opportunities").insert(record).execute()
    except Exception:
        return False, "The opportunity could not be saved. Confirm that your business is verified."
    return True, "Opportunity submitted for review." if submit else "Opportunity saved as a draft."


def list_business_opportunities(settings: Settings, user: AuthUser) -> list[dict[str, Any]]:
    if user.mode == "demo":
        return [item for item in _demo_opportunities() if item["business_id"] == user.id]
    try:
        result = (
            get_authenticated_client(settings)
            .table("opportunities")
            .select("*")
            .eq("business_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def list_published_opportunities(
    settings: Settings, user: AuthUser | None = None
) -> list[dict[str, Any]]:
    if user and user.mode == "demo":
        demo = [item for item in _demo_opportunities() if item.get("status") == "published"]
        return demo or _sample_opportunities()
    if not settings.has_supabase_credentials:
        return _sample_opportunities()
    try:
        client = get_authenticated_client(settings) if user else None
        if client is None:
            from modules.database import create_supabase_client

            client = create_supabase_client(settings.supabase_url or "", settings.supabase_anon_key or "")
        result = (
            client.table("opportunities")
            .select("id,title,description,skills_required,location,work_arrangement,compensation_type,compensation_amount,duration_weeks,application_deadline,created_at")
            .eq("status", "published")
            .gte("application_deadline", date.today().isoformat())
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def _sample_opportunities() -> list[dict[str, Any]]:
    return [
        {
            "id": "sample-1",
            "title": "Sales Data Cleanup and Dashboard",
            "description": "Clean a local retailer's sales records and prepare a simple Excel dashboard.",
            "skills_required": ["Excel", "Data cleaning", "Dashboard design"],
            "location": "Calabar",
            "work_arrangement": "hybrid",
            "compensation_type": "stipend",
            "compensation_amount": 25000,
            "duration_weeks": 3,
            "application_deadline": "2027-01-31",
        }
    ]


def list_verification_queue(settings: Settings, user: AuthUser) -> list[dict[str, Any]]:
    if user.mode == "demo":
        return []
    try:
        result = (
            get_authenticated_client(settings)
            .table("business_profiles")
            .select("user_id,business_name,industry,description,address,verification_status")
            .eq("verification_status", "pending")
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def review_business(
    settings: Settings, user: AuthUser, business_id: str, decision: str, note: str
) -> tuple[bool, str]:
    if decision not in {"verified", "rejected"}:
        return False, "Choose a valid verification decision."
    if user.mode == "demo":
        return True, f"Demo business marked as {decision}."
    try:
        get_authenticated_client(settings).rpc(
            "review_business", {"target_business_id": business_id, "decision": decision, "p_review_note": note.strip() or None}
        ).execute()
    except Exception:
        return False, "The verification decision could not be saved."
    return True, f"Business marked as {decision}."


def list_opportunity_review_queue(settings: Settings, user: AuthUser) -> list[dict[str, Any]]:
    if user.mode == "demo":
        return [item for item in _demo_opportunities() if item.get("status") == "pending_review"]
    try:
        result = (
            get_authenticated_client(settings)
            .table("opportunities")
            .select("id,title,description,location,work_arrangement,compensation_type,business_id,status")
            .eq("status", "pending_review")
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def review_opportunity(
    settings: Settings, user: AuthUser, opportunity_id: str, decision: str, note: str
) -> tuple[bool, str]:
    if decision not in {"published", "rejected"}:
        return False, "Choose a valid opportunity decision."
    if user.mode == "demo":
        return True, f"Demo opportunity marked as {decision}."
    try:
        get_authenticated_client(settings).rpc(
            "review_opportunity", {"target_opportunity_id": opportunity_id, "decision": decision, "p_review_note": note.strip() or None}
        ).execute()
    except Exception:
        return False, "The opportunity decision could not be saved."
    return True, f"Opportunity marked as {decision}."
