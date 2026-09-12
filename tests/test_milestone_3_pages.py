from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_opportunities_page_has_search_and_sample_listing():
    app = AppTest.from_file(str(ROOT / "pages/1_Opportunities.py"))
    app.run(timeout=10)

    assert not app.exception
    assert any(field.label == "Search" for field in app.text_input)
    assert any("Sales Data Cleanup" in heading.value for heading in app.subheader)


def test_demo_business_can_open_opportunity_form():
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
    assert any(button.label == "Submit for review" for button in app.button)


def test_admin_dashboard_is_role_protected():
    app = AppTest.from_file(str(ROOT / "pages/5_Admin_Dashboard.py"))
    app.run(timeout=10)

    assert not app.exception
    assert any("sign in" in warning.value.lower() for warning in app.warning)
