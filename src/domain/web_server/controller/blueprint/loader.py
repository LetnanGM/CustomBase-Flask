from .model import BlueprintEntry, LoadTarget
from typing import Callable
import inspect


class BlueprintLoader:
    """
    Memuat satu blueprint entry ke dalam Flask app.

    Strategy pattern: tambahkan `_load_*` baru untuk mendukung
    tipe target tambahan tanpa menyentuh logika utama.
    """

    from flask import Flask

    def __init__(self, app: Flask) -> None:
        self._app = app

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, entry: BlueprintEntry) -> None:
        """
        Muat satu BlueprintEntry.

        Raises:
            TypeError: jika target bukan class atau callable yang valid.
        """
        target = entry.target

        if self._is_class_with_app_param(target):
            self._load_class_with_app(target)

        elif self._is_class_without_app_param(target):
            self._load_class_blank(target)

        elif callable(target):
            self._load_callable(target)

        else:
            raise TypeError(f"Target '{target}' bukan class atau callable yang valid.")

    # ------------------------------------------------------------------
    # Private helpers — deteksi tipe
    # ------------------------------------------------------------------

    @staticmethod
    def _is_class_with_app_param(target: LoadTarget) -> bool:
        if not isinstance(target, type):
            return False
        try:
            sig = inspect.signature(target.__init__)
            return "app" in sig.parameters
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _is_class_without_app_param(target: LoadTarget) -> bool:
        return isinstance(target, type)

    # ------------------------------------------------------------------
    # Private helpers — pemuatan
    # ------------------------------------------------------------------

    def _load_class_with_app(self, cls: type) -> None:
        cls(app=self._app)

    def _load_class_blank(self, cls: type) -> None:
        cls()

    def _load_callable(self, func: Callable) -> None:
        sig = inspect.signature(func)
        if "app" in sig.parameters:
            func(app=self._app)
        else:
            func()
