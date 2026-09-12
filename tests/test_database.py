from modules.config import Settings
from modules.database import get_database_status


def make_settings(url=None, key=None):
    return Settings(
        app_env="test",
        app_name="SkillBridge Local",
        app_location="Calabar, Cross River State",
        supabase_url=url,
        supabase_anon_key=key,
    )


def test_offline_mode_is_clear_and_safe():
    status = get_database_status(make_settings())

    assert status.is_ready is False
    assert status.label == "Offline demo mode"
    assert "credentials" in status.message.lower()


def test_configured_client_status(monkeypatch):
    monkeypatch.setattr(
        "modules.database.create_supabase_client",
        lambda url, key: object(),
    )

    status = get_database_status(make_settings("https://example.supabase.co", "safe-test-key"))

    assert status.is_ready is True
    assert status.label == "Database client configured"

