from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_home_page_renders_without_exception():
    app = AppTest.from_file(str(ROOT / "app.py"))
    app.run(timeout=10)

    assert not app.exception
    assert app.title or app.markdown

