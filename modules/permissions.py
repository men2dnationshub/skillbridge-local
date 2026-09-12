"""Role based page protection."""

from __future__ import annotations

from collections.abc import Iterable

import streamlit as st

from modules.auth import AuthUser, get_current_user


def require_user(allowed_roles: Iterable[str] | None = None) -> AuthUser:
    user = get_current_user()
    if user is None:
        st.warning("Please sign in from the Account page to view this area.")
        st.info("Select Account from the page menu to continue.")
        st.stop()

    roles = set(allowed_roles or ())
    if roles and user.role not in roles:
        st.error("This page is not available for your account role.")
        st.info("Choose your dashboard or Home from the page menu.")
        st.stop()

    return user
