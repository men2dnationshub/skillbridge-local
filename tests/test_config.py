from modules.config import get_settings


def test_default_settings_are_safe(monkeypatch):
    for name in (
        "APP_ENV",
        "APP_NAME",
        "APP_LOCATION",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_name == "SkillBridge Local"
    assert settings.app_location == "Calabar, Cross River State"
    assert settings.has_supabase_credentials is False
    assert settings.is_production is False


def test_credentials_require_both_values(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    get_settings.cache_clear()

    assert get_settings().has_supabase_credentials is False

