import streamlit as st

from modules.auth import (
    get_current_user,
    login,
    logout,
    register,
    start_demo_session,
)
from modules.config import get_settings
from modules.ui import apply_brand_styles, render_footer


st.set_page_config(page_title="Account | SkillBridge Local", page_icon="🔐", layout="wide")
settings = get_settings()
apply_brand_styles()
st.title("Account")

user = get_current_user()
if user:
    st.success(f"Signed in as {user.full_name}")
    st.write(f"**Role:** {user.role.title()}")
    st.write(f"**Email:** {user.email}")
    if user.mode == "demo":
        st.warning("Demo mode stores changes only for this browser session.")
    st.info("Select your Student or Business Dashboard from the page menu.")
    if st.button("Log out", type="primary"):
        logout(settings)
        st.rerun()
else:
    if not settings.has_supabase_credentials:
        st.info("The app is in offline demo mode. Connect Supabase to create real accounts.")

    login_tab, register_tab, demo_tab = st.tabs(["Log in", "Create account", "Preview demo"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input("Email address")
            login_password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in", type="primary")
        if submitted:
            result = login(settings, login_email, login_password)
            if result.success:
                st.success(result.message)
                st.rerun()
            else:
                st.error(result.message)

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Full name")
            email = st.text_input("Email address")
            role = st.radio("I am registering as a", ["Student", "Business"], horizontal=True)
            password = st.text_input("Password", type="password", help="Use at least eight characters.")
            confirm_password = st.text_input("Confirm password", type="password")
            accepted_terms = st.checkbox("I agree to the platform terms and privacy notice")
            create_account = st.form_submit_button("Create account", type="primary")
        if create_account:
            if password != confirm_password:
                st.error("The passwords do not match.")
            elif not accepted_terms:
                st.error("Accept the terms and privacy notice to continue.")
            else:
                result = register(settings, full_name, email, password, role.lower())
                if result.success:
                    st.success(result.message)
                    if not result.requires_email_confirmation:
                        st.rerun()
                else:
                    st.error(result.message)

    with demo_tab:
        st.write("Preview a protected dashboard without creating an account.")
        student_col, business_col = st.columns(2)
        with student_col:
            if st.button("Preview as student", use_container_width=True):
                start_demo_session("student")
                st.rerun()
        with business_col:
            if st.button("Preview as business", use_container_width=True):
                start_demo_session("business")
                st.rerun()

render_footer(settings.app_name)
