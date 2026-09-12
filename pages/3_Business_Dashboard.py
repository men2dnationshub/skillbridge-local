import streamlit as st
from datetime import date, timedelta

from modules.config import get_settings
from modules.opportunities import (
    COMPENSATION_TYPES,
    WORK_ARRANGEMENTS,
    create_opportunity,
    list_business_opportunities,
)
from modules.permissions import require_user
from modules.profiles import get_profile, profile_completion, save_business_profile
from modules.ui import apply_brand_styles, render_footer, status_badge


st.set_page_config(page_title="Business Dashboard | SkillBridge Local", page_icon="🏪", layout="wide")
settings = get_settings()
apply_brand_styles()
user = require_user({"business"})
profile = get_profile(settings, user)
opportunities = list_business_opportunities(settings, user)

st.title("Business dashboard")
st.caption(f"Welcome, {profile.get('full_name') or user.full_name}")
if user.mode == "demo":
    st.warning("Demo mode: your changes remain only in this browser session.")

completion = profile_completion(user, profile)
verification = profile.get("verification_status", "pending")
metric_one, metric_two, metric_three = st.columns(3)
metric_one.metric("Profile completion", f"{completion}%")
metric_two.metric("Opportunities", str(len(opportunities)))
metric_three.metric("Applications", "0", help="Enabled in Milestone 4")
status_badge(f"Verification: {verification.title()}", verification == "verified")

st.markdown("### Business profile")
with st.form("business_profile_form"):
    full_name = st.text_input("Contact person's full name", value=profile.get("full_name") or user.full_name)
    business_name = st.text_input("Business name", value=profile.get("business_name") or "")
    first, second = st.columns(2)
    with first:
        phone = st.text_input("Phone number", value=profile.get("phone") or "")
        location = st.text_input("Business location", value=profile.get("location") or settings.app_location)
    with second:
        industry = st.text_input("Industry", value=profile.get("industry") or "", placeholder="Example: Retail")
        address = st.text_input("Business address", value=profile.get("address") or "")
    description = st.text_area("Business description", value=profile.get("description") or "", max_chars=750)
    save = st.form_submit_button("Save and request verification", type="primary")

if save:
    success, message = save_business_profile(
        settings,
        user,
        {
            "full_name": full_name,
            "business_name": business_name,
            "phone": phone,
            "location": location,
            "industry": industry,
            "address": address,
            "description": description,
        },
    )
    (st.success if success else st.error)(message)
    if success:
        st.rerun()

st.divider()
st.markdown("### Opportunity management")
can_publish = user.mode == "demo" or verification == "verified"
if not can_publish:
    st.info("Your business must be verified before you can create an opportunity.")
else:
    with st.form("opportunity_form", clear_on_submit=True):
        title = st.text_input("Opportunity title", placeholder="Example: Sales Data Cleanup and Dashboard")
        description = st.text_area(
            "Project description",
            placeholder="Explain the business problem, expected work and final deliverable.",
            max_chars=2500,
        )
        skills_text = st.text_input("Required skills", placeholder="Excel, data cleaning, dashboard design")
        first, second = st.columns(2)
        with first:
            opportunity_location = st.text_input("Project location", value=profile.get("location") or settings.app_location)
            work_arrangement = st.selectbox("Work arrangement", WORK_ARRANGEMENTS)
            duration_weeks = st.number_input("Duration in weeks", min_value=1, max_value=52, value=3)
        with second:
            compensation_type = st.selectbox("Compensation", COMPENSATION_TYPES)
            compensation_amount = st.number_input(
                "Amount in naira", min_value=0.0, value=0.0, step=1000.0,
                disabled=compensation_type == "Unpaid",
            )
            application_deadline = st.date_input(
                "Application deadline", value=date.today() + timedelta(days=14), min_value=date.today()
            )
        save_draft = st.form_submit_button("Save draft")
        submit_review = st.form_submit_button("Submit for review", type="primary")

    if save_draft or submit_review:
        success, message = create_opportunity(
            settings,
            user,
            {
                "title": title,
                "description": description,
                "skills_required": skills_text.split(","),
                "location": opportunity_location,
                "work_arrangement": work_arrangement,
                "compensation_type": compensation_type,
                "compensation_amount": compensation_amount,
                "duration_weeks": duration_weeks,
                "application_deadline": application_deadline,
            },
            submit=submit_review,
        )
        (st.success if success else st.error)(message)
        if success:
            st.rerun()

if opportunities:
    st.markdown("#### Your opportunities")
    for item in opportunities:
        with st.expander(f"{item['title']} · {str(item.get('status', 'draft')).replace('_', ' ').title()}"):
            st.write(item.get("description", ""))
            st.caption(
                f"{str(item.get('work_arrangement', '')).replace('_', ' ').title()} · "
                f"{item.get('location', '')} · {item.get('duration_weeks', '')} weeks"
            )

render_footer("SkillBridge Local")
