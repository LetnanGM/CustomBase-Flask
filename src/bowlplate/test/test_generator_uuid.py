"""Unit test untuk bowlplate.support.generator.uuid.uid"""

import uuid as uuid_lib

import pytest

from bowlplate.support.generator.uuid import uid


def test_token_char_default_length():
    token = uid.token_char()
    assert isinstance(token, str)
    assert len(token) == 6


def test_token_char_custom_length():
    token = uid.token_char(16)
    assert len(token) == 16
    assert all(c.isalnum() for c in token)


def test_token_char_zero_length():
    token = uid.token_char(0)
    assert token == ""


def test_token_uuid_is_valid_uuid4():
    token = uid.token_uuid()
    parsed = uuid_lib.UUID(token, version=4)
    assert str(parsed) == token


def test_token_uuid_unique_across_calls():
    tokens = {uid.token_uuid() for _ in range(20)}
    assert len(tokens) == 20


def test_token_hex_random_is_hex_string():
    token = uid.token_hex_random()
    assert isinstance(token, str)
    int(token, 16)  # should not raise


def test_token_urlsafe_is_string():
    token = uid.token_urlsafe()
    assert isinstance(token, str)
    assert len(token) > 0


def test_token_bytes_returns_bytes():
    token = uid.token_bytes()
    assert isinstance(token, (bytes, bytearray))


@pytest.mark.xfail(
    reason=(
        "uid.token_hex_safe() calls uuid.uuid4().hex() as if 'hex' were a method, "
        "but UUID.hex is a str property, not callable -> raises TypeError."
    ),
    raises=TypeError,
    strict=True,
)
def test_token_hex_safe_currently_broken():
    uid.token_hex_safe()
