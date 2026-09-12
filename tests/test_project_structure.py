from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_milestone_one_files_exist():
    expected = (
        "app.py",
        "requirements.txt",
        ".env.example",
        ".streamlit/config.toml",
        "modules/config.py",
        "modules/database.py",
        "modules/auth.py",
        "modules/permissions.py",
        "modules/profiles.py",
        "modules/ui.py",
        "pages/0_Account.py",
        "sql/001_milestone_2_auth_profiles.sql",
    )

    for relative_path in expected:
        assert (ROOT / relative_path).is_file(), relative_path


def test_secret_files_are_gitignored():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".env" in gitignore
    assert ".streamlit/secrets.toml" in gitignore
