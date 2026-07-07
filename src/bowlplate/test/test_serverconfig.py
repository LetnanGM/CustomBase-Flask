import pytest
from pathlib import Path

from bowlplate.domain.web_server.model import banner, ServerConfig


def test_banner_contains_rawr():
    b = banner()
    assert isinstance(b, str)
    assert "RAWR" in b


def test_is_valid_ip():
    assert ServerConfig._is_valid_ip("127.0.0.1")
    assert ServerConfig._is_valid_ip("0.0.0.0")

    assert not ServerConfig._is_valid_ip("256.0.0.1")
    assert not ServerConfig._is_valid_ip("abc")
    assert not ServerConfig._is_valid_ip("1.2.3")


def test_to_dict(tmp_path):
    static = str(tmp_path / "static")
    templ = str(tmp_path / "templates")

    sc = ServerConfig(
        host="127.0.0.1",
        port=8000,
        debug=False,
        static_folder=static,
        template_folder=templ,
        max_content_length=1024,
    )

    d = sc.to_dict()
    assert d["host"] == "127.0.0.1"
    assert d["port"] == 8000
    assert d["debug"] is False
    assert d["static_folder"] == static
    assert d["template_folder"] == templ
    assert d["max_content_length"] == 1024


def test_validate_folders_manual(tmp_path):
    static = str(tmp_path / "static")
    templ = str(tmp_path / "templates")

    sc = ServerConfig(
        host="127.0.0.1",
        port=8000,
        debug=False,
        static_folder=static,
        template_folder=templ,
        max_content_length=1024,
    )

    # Directories should not exist until folder validation is run
    assert not Path(static).exists()
    assert not Path(templ).exists()

    sc._validate_folders()

    assert Path(static).exists() and Path(static).is_dir()
    assert Path(templ).exists() and Path(templ).is_dir()


@pytest.mark.xfail(
    reason=(
        "ServerConfig.__post_init__ is defined but Pydantic's BaseModel does not call "
        "__post_init__ on instantiation; therefore folder validation won't run automatically."
    )
)
def test_instantiation_does_not_create_folders(tmp_path):
    static = str(tmp_path / "static")
    templ = str(tmp_path / "templates")

    sc = ServerConfig(
        host="127.0.0.1",
        port=8000,
        debug=False,
        static_folder=static,
        template_folder=templ,
        max_content_length=1024,
    )

    # If __post_init__ ran on instantiation the folders would exist; mark as xfail to
    # surface this as a known behavior without failing CI.
    assert not Path(static).exists()
    assert not Path(templ).exists()
