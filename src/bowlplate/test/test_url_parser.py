"""Unit test untuk bowlplate.support.parser.url dan url_utils"""

import pytest

from bowlplate.support.parser.url import URLParse
from bowlplate.support.parser.url_utils import uri, vmodel


class TestUri:
    def test_is_url_true_for_http(self):
        u = uri()
        assert u.is_url("http://example.com") is True

    def test_is_url_true_for_https(self):
        u = uri()
        assert u.is_url("https://example.com/path") is True

    def test_is_url_false_for_non_url_string(self):
        u = uri()
        assert u.is_url("not a url") is False

    def test_is_url_false_for_ftp_scheme(self):
        u = uri()
        assert u.is_url("ftp://example.com") is False

    def test_is_url_raises_typeerror_for_non_string(self):
        u = uri()
        with pytest.raises(TypeError):
            u.is_url(123)

    def test_is_url_raises_assertion_for_empty_string(self):
        u = uri()
        with pytest.raises(AssertionError):
            u.is_url("")

    def test_is_url_records_current_uri(self):
        u = uri()
        u.is_url("https://example.com")
        assert vmodel.CURRENT_URI == "https://example.com"


class TestURLParseInternals:
    """Test langsung terhadap logic parsing (method .parse), yang berfungsi benar."""

    def test_parse_populates_components_correctly(self):
        parser = URLParse.__new__(URLParse)  # bypass buggy __init__ reset
        parser._current_url = None
        parser.parse("https://user@example.com:8080/a/b?x=1#frag")

        assert parser.scheme == "https"
        assert parser.netloc == "user@example.com:8080"
        assert parser.path == "/a/b"
        assert parser.fragment == "frag"


@pytest.mark.xfail(
    reason=(
        "URLParse.__init__ calls self.parse(uri) which correctly sets "
        "_scheme/_netloc/_path/etc, but the very next lines in __init__ "
        "reset all of those attributes back to None, so the public "
        "properties always report None regardless of the input URL."
    ),
    strict=True,
)
def test_urlparse_public_properties_reflect_parsed_url():
    parsed = URLParse("https://example.com/path?x=1#frag")

    assert parsed.scheme == "https"
    assert parsed.netloc == "example.com"
    assert parsed.path == "/path"
    assert parsed.fragment == "frag"
