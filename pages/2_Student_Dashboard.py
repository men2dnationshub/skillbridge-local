import streamlit as st

from modules.config import get_settings
from modules.permissions import require_user
from modules.profiles import get_profile, profile_completion, save_student_profile
from modules.ui import apply_brand_styles, render_footer


st.set_page_config(page_title="Student Dashboard | SkillBridge Local", page_icon="🎓", layout="wide")
settings = get_settings()
apply_brand_styles()
user = require_user({"student"})
profile = get_profile(settings, user)

st.title("Student dashboard")
st.caption(f"Welcome, {profile.get('full_name') or user.full_name}")
if user.mode == "demo":
    st.warning("Demo mode: your changes remain only in this browser session.")

completion = profile_completion(user, profile)
metric_one, metric_two, metric_three = st.columns(3)
metric_one.metric("Profile completion", f"{completion}%")
metric_two.metric("Applications", "0", help="Enabled in Milestone 4")
metric_three.metric("Active projects", "0", help="Enabled in Milestone 5")
st.progress(completion / 100)

st.markdown("### My profile")
skill_options = ["Excel", "Power BI", "SQL", "Python", "Data Entry", "Record Management", "Digital Marketing"]
tool_options = ["Microsoft Excel", "Power BI Desktop", "MySQL", "Python", "Google Sheets", "Canva"]

with st.form("student_profile_form"):
    full_name = st.text_input("Full name", value=profile.get("full_name") or user.full_name)
    first, second = st.columns(2)
    with first:
        phone = st.text_input("Phone number", value=profile.get("phone") or "")
        location = st.text_input("Location", value=profile.get("location") or settings.app_location)
        education = st.text_input("Education or training", value=profile.get("education") or "")
        experience = st.selectbox(
            "Experience level",
            ["Beginner", "Developing", "Intermediate"],
            index=["Beginner", "Developing", "Intermediate"].index(profile.get("experience_level"))
            if profile.get("experience_level") in ["Beginner", "Developing", "Intermediate"]
            else 0,
        )
    with second:
        skills = st.multiselect("Skills", skill_options, default=[v for v in profile.get("skills", []) if v in skill_options])
        tools = st.multiselect("Tools", tool_options, default=[v for v in profile.get("tools", []) if v in tool_options])
        portfolio_url = st.text_input("Portfolio URL", value=profile.get("portfolio_url") or "")
        linkedin_url = st.text_input("LinkedIn URL", value=profile.get("linkedin_url") or "")
    bio = st.text_area("Short biography", value=profile.get("bio") or "", max_chars=500)
    availability = st.text_input("Availability", value=profile.get("availability") or "", placeholder="Example: 10 hours per week")
    save = st.form_submit_button("Save student profile", type="primary")

if save:
    success, message = save_student_profile(
        settings,
        user,
        {
            "full_name": full_name,
            "phone": phone,
            "location": location,
            "education": education,
            "skills": skills,
            "tools": tools,
            "experience_level": experience,
            "portfolio_url": portfolio_url,
            "linkedin_url": linkedin_url,
            "bio": bio,
            "availability": availability,
        },
    )
    (st.success if success else st.error)(message)
    if success:
        st.rerun()

render_footer("SkillBridge Local")
