"""Unit test untuk bowlplate.domain.web_core.utils.crypto.encryption

Catatan: modul ini di-load langsung dari file (bukan lewat `import
bowlplate.domain.web_core.utils...`) karena package `domain.web_core.utils`
saat ini tidak bisa di-import sama sekali. Rantainya:

    utils/__init__.py
      -> validator/header/hvalidator.py
        -> bowlplate.domain.web_core.bootstrap
          -> .data.configuration.sys.SecurityConfig.SecurityConfig

dan modul `SecurityConfig` itu tidak ada di repo (ModuleNotFoundError).
Ini bug pre-existing di project, di luar scope encryption.py itu sendiri,
jadi test ini di-isolasi supaya tidak ikut gagal karenanya.
"""

import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "domain"
    / "web_core"
    / "utils"
    / "crypto"
    / "encryption.py"
)
_spec = importlib.util.spec_from_file_location("encryption_direct", _MODULE_PATH)
_encryption = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_encryption)

safe_str_cmp = _encryption.safe_str_cmp


def test_safe_str_cmp_true_for_equal_strings():
    assert safe_str_cmp("secret-token", "secret-token") is True


def test_safe_str_cmp_false_for_different_strings():
    assert safe_str_cmp("secret-token", "other-token") is False


def test_safe_str_cmp_false_for_different_length():
    assert safe_str_cmp("short", "much-longer-string") is False


def test_safe_str_cmp_case_sensitive():
    assert safe_str_cmp("Secret", "secret") is False


def test_safe_str_cmp_works_with_bytes():
    assert safe_str_cmp(b"secret", b"secret") is True
    assert safe_str_cmp(b"secret", b"other") is False


def test_safe_str_cmp_raises_on_mixed_str_and_bytes():
    with pytest.raises(TypeError):
        safe_str_cmp("secret", b"secret")
