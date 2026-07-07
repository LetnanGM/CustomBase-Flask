"""Unit test untuk bowlplate.support.time.date.date"""

import pytest

from bowlplate.support.time.date import date, dateconf


def test_get_date_as_ymd_matches_dateconf():
    expected = dateconf.DATE.strftime("%Y-%m-%d")
    assert date.get_date_as_ymd() == expected


def test_get_year_matches_dateconf():
    assert date.get_year() == str(dateconf.DATE.year)


def test_get_month_is_zero_padded_when_single_digit(monkeypatch):
    from datetime import datetime

    monkeypatch.setattr(dateconf, "DATE", datetime(2026, 3, 15))
    assert date.get_month() == "03"


def test_get_month_not_padded_when_two_digits(monkeypatch):
    from datetime import datetime

    monkeypatch.setattr(dateconf, "DATE", datetime(2026, 11, 15))
    assert date.get_month() == 11


@pytest.mark.xfail(
    reason=(
        "date.get_date_as_now() computes the formatted string but never returns it, "
        "so it always evaluates to None."
    ),
    strict=True,
)
def test_get_date_as_now_currently_returns_none():
    result = date.get_date_as_now()
    assert result is not None
    assert isinstance(result, str)
