from modules.auth import _safe_role, register
from modules.config import Settings


def settings_without_database():
    return Settings(
        app_env="test",
        app_name="SkillBridge Local",
        app_location="Calabar, Cross River State",
        supabase_url=None,
        supabase_anon_key=None,
    )


def test_public_role_allowlist_blocks_admin_registration():
    assert _safe_role("student") == "student"
    assert _safe_role("business") == "business"
    assert _safe_role("admin") == "student"


def test_registration_validates_password_before_backend():
    result = register(
        settings_without_database(),
        full_name="Mfon Nsimah",
        email="mfon@example.com",
        password="short",
        role="student",
    )

    assert result.success is False
    assert "eight" in result.message.lower()


def test_registration_explains_offline_mode():
    result = register(
        settings_without_database(),
        full_name="Mfon Nsimah",
        email="mfon@example.com",
        password="long-enough-password",
        role="student",
    )

    assert result.success is False
    assert "supabase" in result.message.lower()

