"""SkillBridge Local application entry point."""

from __future__ import annotations

import streamlit as st

from modules.config import get_settings
from modules.database import get_database_status
from modules.auth import get_current_user
from modules.ui import apply_brand_styles, render_footer, render_header, status_badge


st.set_page_config(
    page_title="SkillBridge Local",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

settings = get_settings()
user = get_current_user()
apply_brand_styles()

with st.sidebar:
    st.markdown("## SkillBridge Local")
    st.caption("Connecting talent with real business opportunities")
    st.divider()
    st.markdown("**MVP status**")
    st.caption("Milestone 2 · Accounts and profiles")
    st.markdown("**Pilot location**")
    st.caption(settings.app_location)
    st.divider()
    if user:
        st.success(f"Signed in as {user.full_name}")
        st.page_link("pages/0_Account.py", label="Manage account", icon="🔐")
    else:
        st.page_link("pages/0_Account.py", label="Log in or create account", icon="🔐")

render_header(
    eyebrow="CALABAR PILOT",
    title="Practical experience for students. Digital support for businesses.",
    subtitle=(
        "SkillBridge Local connects emerging talent with verified short projects "
        "from small businesses."
    ),
)

left, middle, right = st.columns(3)
with left:
    st.metric("Student profiles", "0", help="Enabled in Milestone 2")
with middle:
    st.metric("Verified businesses", "0", help="Enabled in Milestone 3")
with right:
    st.metric("Open opportunities", "0", help="Enabled in Milestone 3")

st.markdown("### How it will work")
step_one, step_two, step_three = st.columns(3)
with step_one:
    st.markdown("#### 1. Businesses post")
    st.write("Verified businesses describe a short project, required skills, timeline, and compensation.")
with step_two:
    st.markdown("#### 2. Students apply")
    st.write("Students find relevant opportunities and apply using their skills profile and portfolio.")
with step_three:
    st.markdown("#### 3. Experience is verified")
    st.write("Completed work, feedback, and ratings become part of the student's practical record.")

st.markdown("### Platform readiness")
database_status = get_database_status(settings)
status_badge(database_status.label, database_status.is_ready)
st.caption(database_status.message)

st.markdown("### Start using SkillBridge Local")
st.write(
    "Create an account or use demo mode to complete a student or business profile. "
    "Opportunity publishing and applications will be added in the next milestones."
)

render_footer(settings.app_name)
