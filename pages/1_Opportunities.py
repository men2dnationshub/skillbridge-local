import streamlit as st

from modules.auth import get_current_user
from modules.config import get_settings
from modules.opportunities import list_published_opportunities
from modules.ui import apply_brand_styles, render_footer, render_header


st.set_page_config(page_title="Opportunities | SkillBridge Local", page_icon="🔎", layout="wide")
settings = get_settings()
user = get_current_user()
apply_brand_styles()
render_header(
    "REAL PROJECTS. PRACTICAL EXPERIENCE.",
    "Browse opportunities",
    "Discover approved projects from verified small businesses.",
)

opportunities = list_published_opportunities(settings, user)
search = st.text_input("Search", placeholder="Search title, skill or location")
arrangement = st.selectbox("Work arrangement", ["All", "On site", "Remote", "Hybrid"])

needle = search.strip().lower()
filtered = []
for item in opportunities:
    searchable = " ".join(
        [item.get("title", ""), item.get("description", ""), item.get("location", ""), *item.get("skills_required", [])]
    ).lower()
    item_arrangement = str(item.get("work_arrangement", "")).replace("_", " ").lower()
    if needle and needle not in searchable:
        continue
    if arrangement != "All" and item_arrangement != arrangement.lower():
        continue
    filtered.append(item)

label = "opportunity" if len(filtered) == 1 else "opportunities"
st.caption(f"{len(filtered)} {label} available")
if not filtered:
    st.info("No published opportunities match your search yet.")
for item in filtered:
    with st.container(border=True):
        st.subheader(item["title"])
        st.write(item["description"])
        st.write("Skills: " + ", ".join(item.get("skills_required", [])))
        compensation = str(item.get("compensation_type", "unpaid")).title()
        if item.get("compensation_amount"):
            compensation += f" · ₦{float(item['compensation_amount']):,.0f}"
        st.caption(
            f"{item.get('location', '')} · {str(item.get('work_arrangement', '')).replace('_', ' ').title()} · "
            f"{compensation} · {item.get('duration_weeks', '')} weeks · Apply by {item.get('application_deadline', '')}"
        )
render_footer("SkillBridge Local")
