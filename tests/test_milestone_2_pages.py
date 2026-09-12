from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_account_page_renders_login_and_registration():
    app = AppTest.from_file(str(ROOT / "pages/0_Account.py"))
    app.run(timeout=10)

    assert not app.exception
    labels = [tab.label for tab in app.tabs]
    assert labels == ["Log in", "Create account", "Preview demo"]


def test_demo_student_can_start_a_session():
    app = AppTest.from_file(str(ROOT / "pages/0_Account.py"))
    app.run(timeout=10)
    preview_button = next(button for button in app.button if button.label == "Preview as student")
    preview_button.click()
    app.run(timeout=10)

    assert not app.exception
    assert any("Demo Student" in success.value for success in app.success)


def test_student_dashboard_is_protected_when_logged_out():
    app = AppTest.from_file(str(ROOT / "pages/2_Student_Dashboard.py"))
    app.run(timeout=10)

    assert not app.exception
    assert any("sign in" in warning.value.lower() for warning in app.warning)


def test_business_dashboard_is_protected_when_logged_out():
    app = AppTest.from_file(str(ROOT / "pages/3_Business_Dashboard.py"))
    app.run(timeout=10)

    assert not app.exception
    assert any("sign in" in warning.value.lower() for warning in app.warning)


def test_student_role_can_open_student_profile_form():
    app = AppTest.from_file(str(ROOT / "pages/2_Student_Dashboard.py"))
    app.session_state["auth_user"] = {
        "id": "demo-student",
        "email": "demo.student@skillbridge.local",
        "role": "student",
        "full_name": "Demo Student",
        "mode": "demo",
    }
    app.run(timeout=10)

    assert not app.exception
    assert any(button.label == "Save student profile" for button in app.button)


def test_business_role_can_open_business_profile_form():
    app = AppTest.from_file(str(ROOT / "pages/3_Business_Dashboard.py"))
    app.session_state["auth_user"] = {
        "id": "demo-business",
        "email": "demo.business@skillbridge.local",
        "role": "business",
        "full_name": "Demo Business Owner",
        "mode": "demo",
    }
    app.run(timeout=10)

    assert not app.exception
    assert any(button.label == "Save and request verification" for button in app.button)
