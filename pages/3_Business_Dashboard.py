import streamlit as st

from modules.config import get_settings
from modules.permissions import require_user
from modules.profiles import get_profile, profile_completion, save_business_profile
from modules.ui import apply_brand_styles, render_footer, status_badge


st.set_page_config(page_title="Business Dashboard | SkillBridge Local", page_icon="🏪", layout="wide")
settings = get_settings()
apply_brand_styles()
user = require_user({"business"})
profile = get_profile(settings, user)

st.title("Business dashboard")
st.caption(f"Welcome, {profile.get('full_name') or user.full_name}")
if user.mode == "demo":
    st.warning("Demo mode: your changes remain only in this browser session.")

completion = profile_completion(user, profile)
verification = profile.get("verification_status", "pending")
metric_one, metric_two, metric_three = st.columns(3)
metric_one.metric("Profile completion", f"{completion}%")
metric_two.metric("Opportunities", "0", help="Enabled in Milestone 3")
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

render_footer("SkillBridge Local")
