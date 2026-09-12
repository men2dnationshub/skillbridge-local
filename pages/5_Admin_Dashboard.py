import streamlit as st

from modules.config import get_settings
from modules.opportunities import (
    list_opportunity_review_queue,
    list_verification_queue,
    review_business,
    review_opportunity,
)
from modules.permissions import require_user
from modules.ui import apply_brand_styles, render_footer


st.set_page_config(page_title="Admin Dashboard | SkillBridge Local", page_icon="🛡️", layout="wide")
settings = get_settings()
apply_brand_styles()
user = require_user({"admin"})
businesses = list_verification_queue(settings, user)
opportunities = list_opportunity_review_queue(settings, user)

st.title("Administrator review dashboard")
first, second = st.columns(2)
first.metric("Businesses awaiting review", len(businesses))
second.metric("Opportunities awaiting review", len(opportunities))

business_tab, opportunity_tab = st.tabs(["Business verification", "Opportunity review"])
with business_tab:
    if not businesses:
        st.info("There are no businesses awaiting verification.")
    for business in businesses:
        with st.expander(business.get("business_name") or "Unnamed business"):
            st.write(business.get("description") or "No description supplied")
            st.caption(f"{business.get('industry') or 'Industry not supplied'} · {business.get('address') or 'Address not supplied'}")
            note = st.text_area("Review note", key=f"business-note-{business['user_id']}")
            approve = st.button("Verify", type="primary", key=f"verify-{business['user_id']}")
            reject = st.button("Reject", key=f"reject-business-{business['user_id']}")
            if approve or reject:
                success, message = review_business(settings, user, business["user_id"], "verified" if approve else "rejected", note)
                (st.success if success else st.error)(message)
                if success:
                    st.rerun()

with opportunity_tab:
    if not opportunities:
        st.info("There are no opportunities awaiting review.")
    for opportunity in opportunities:
        with st.expander(opportunity["title"]):
            st.write(opportunity.get("description", ""))
            st.caption(f"{opportunity.get('location', '')} · {str(opportunity.get('work_arrangement', '')).replace('_', ' ').title()}")
            note = st.text_area("Review note", key=f"opportunity-note-{opportunity['id']}")
            publish = st.button("Publish", type="primary", key=f"publish-{opportunity['id']}")
            reject = st.button("Reject", key=f"reject-opportunity-{opportunity['id']}")
            if publish or reject:
                success, message = review_opportunity(settings, user, opportunity["id"], "published" if publish else "rejected", note)
                (st.success if success else st.error)(message)
                if success:
                    st.rerun()
render_footer("SkillBridge Local")
