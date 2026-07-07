"""Unit test untuk bowlplate.share.builtns.exceptions"""

from bowlplate.share.builtns.exceptions.parent import AppError
from bowlplate.share.builtns.exceptions.child.InApp import (
    InvalidArgs,
    NameAliasAlreadyInUse,
)


def caller_helper(exc_cls, *args, **kwargs):
    """Helper agar 'func_name' pada AppError berisi nama fungsi ini."""
    raise exc_cls(*args, **kwargs)


def test_apperror_default_message_is_class_name():
    err = AppError()
    assert err.message == "AppError"


def test_apperror_custom_message():
    err = AppError("something went wrong")
    assert err.message == "something went wrong"
    assert str(err).startswith("[APP-000] something went wrong")


def test_apperror_str_includes_context_when_present():
    err = AppError("bad state", context={"field": "email"})
    text = str(err)
    assert "[APP-000] bad state" in text
    assert "Context: {'field': 'email'}" in text


def test_apperror_str_omits_context_when_absent():
    err = AppError("bad state")
    assert "Context:" not in str(err)


def test_apperror_captures_calling_function_name():
    try:
        caller_helper(AppError, "boom")
    except AppError as err:
        assert err.func_name == "caller_helper"
        assert "Function: caller_helper" in str(err)


def test_apperror_format_context_helper():
    ctx = AppError.format_context("app.py", line=42, func="run")
    assert ctx == "File=app.py, Line=42, Func=run"


def test_invalidargs_has_expected_code_and_category():
    err = InvalidArgs("bad type")
    assert err.code == "APP-001"
    assert err.category == "GENERAL"
    assert isinstance(err, AppError)
    assert str(err).startswith("[APP-001] bad type")


def test_namealiasalreadyinuse_has_expected_code():
    err = NameAliasAlreadyInUse()
    assert err.code == "APP-010"
    assert err.message == "NameAliasAlreadyInUse"


def test_exceptions_are_raisable_and_catchable():
    import pytest

    with pytest.raises(InvalidArgs):
        raise InvalidArgs("nope")
