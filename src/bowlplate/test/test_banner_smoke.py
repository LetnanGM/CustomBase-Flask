# basic smoke test for banner
from bowlplate.domain.web_server import model


def test_banner_returns_string():
    b = model.banner()
    assert isinstance(b, str)
    assert len(b) > 0
