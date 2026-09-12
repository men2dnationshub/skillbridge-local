import streamlit as st

from modules.ui import render_footer, render_placeholder


st.set_page_config(page_title="Project Tracker | SkillBridge Local", page_icon="📋", layout="wide")
render_placeholder(
    "Project tracker",
    "Accepted students and businesses will follow deliverables, revisions, and completion here.",
    "Milestone 5",
)
st.markdown("- Project status\n- Submission links\n- Revision requests\n- Completion feedback and ratings")
render_footer("SkillBridge Local")

