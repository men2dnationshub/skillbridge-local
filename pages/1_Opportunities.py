import streamlit as st

from modules.ui import render_footer, render_placeholder


st.set_page_config(page_title="Opportunities | SkillBridge Local", page_icon="🔎", layout="wide")
render_placeholder(
    "Browse opportunities",
    "Students will discover approved local, remote, and hybrid projects here.",
    "Milestone 3",
)
st.markdown("- Keyword and skills search\n- Location and work arrangement filters\n- Clear compensation labels\n- Application deadlines")
render_footer("SkillBridge Local")

