import streamlit as st

from modules.ui import render_footer, render_placeholder


st.set_page_config(page_title="Admin Dashboard | SkillBridge Local", page_icon="🛡️", layout="wide")
render_placeholder(
    "Administrator dashboard",
    "Administrators will review businesses, opportunities, safety reports, and pilot performance here.",
    "Milestone 6",
)
st.markdown("- Verification queue\n- Opportunity approval\n- Safety reports\n- Pilot performance indicators")
render_footer("SkillBridge Local")

