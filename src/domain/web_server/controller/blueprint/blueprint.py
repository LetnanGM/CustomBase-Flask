from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Union

from flask import Flask

from .model import BlueprintEntry, RegistrationHooks, RegistrationPriority, LoadTarget
from .registry import BlueprintRegistry


class BlueprintManager:
    """
    Orkestrasi registrasi blueprint ke Flask app.

    Parameters
    ----------
    app:
        Instance Flask yang sudah dikonfigurasi.
    registry:
        BlueprintRegistry berisi blueprint yang akan diload.
        Default: registry singleton global.
    logger:
        Logger apa pun yang punya method .info() dan .error().
    hooks:
        Lifecycle callbacks opsional.
    isolate_errors:
        True  → blueprint yang gagal di-skip, sisanya tetap diload.
        False → satu kegagalan langsung raise (fail-fast).
    """

    def __init__(
        self,
        app: Flask,
        registry: BlueprintRegistry,
        logger,
        hooks: Optional[RegistrationHooks] = None,
        *,
        isolate_errors: bool = False,
    ) -> None:
        from .loader import BlueprintLoader

        self._app = app
        self._registry = registry
        self._logger = logger
        self._hooks = hooks or RegistrationHooks()
        self._isolate_errors = isolate_errors
        self._loader = BlueprintLoader(app)
        
    def register_blueprints(self) -> RegistrationReport:
        """
        Registrasi semua blueprint dari registry.

        Returns:
            RegistrationReport berisi ringkasan hasil registrasi.
        """
        entries = self._registry.drain()

        if not entries:
            self._logger.info("Tidak ada blueprint untuk diregistrasi.")
            return RegistrationReport()

        report = RegistrationReport()

        for entry in entries:
            self._process_entry(entry, report)

        self._logger.debug(
            f"Registrasi selesai — "
            f"berhasil: {report.succeeded}, gagal: {report.failed}."
        )

        if report.errors and not self._isolate_errors:
            raise BlueprintRegistrationError(report)

        return report

    def _process_entry(self, entry: BlueprintEntry, report: RegistrationReport) -> None:
        self._logger.debug(
            f"Memuat blueprint '{entry.target.__name__}' (prioritas={entry.priority.name}).."
        )

        if self._hooks.before:
            self._hooks.before(entry)

        try:
            self._loader.load(entry)
            report.record_success(entry)

            if self._hooks.after:
                self._hooks.after(entry)

        except Exception as exc:
            report.record_failure(entry, exc)
            self._logger.error(f"Gagal memuat '{entry.target.__name__}': {exc}")

            if self._hooks.on_error:
                self._hooks.on_error(entry, exc)

            if not self._isolate_errors:
                raise


# ---------------------------------------------------------------------------
# Report  (replaces silent failure)
# ---------------------------------------------------------------------------


@dataclass
class RegistrationReport:
    """Hasil registrasi — berguna untuk health-check endpoint."""

    _successes: list[BlueprintEntry] = field(default_factory=list)
    _failures: list[tuple[BlueprintEntry, Exception]] = field(default_factory=list)

    def record_success(self, entry: BlueprintEntry) -> None:
        self._successes.append(entry)

    def record_failure(self, entry: BlueprintEntry, exc: Exception) -> None:
        self._failures.append((entry, exc))

    @property
    def succeeded(self) -> int:
        return len(self._successes)

    @property
    def failed(self) -> int:
        return len(self._failures)

    @property
    def errors(self) -> list[tuple[BlueprintEntry, Exception]]:
        return list(self._failures)

    def __bool__(self) -> bool:
        """True jika semua blueprint berhasil."""
        return self.failed == 0


class BlueprintRegistrationError(RuntimeError):
    """Dilempar saat ada blueprint yang gagal dan isolate_errors=False."""

    def __init__(self, report: RegistrationReport) -> None:
        failed = [e.target.__name__ for e, _ in report.errors]
        super().__init__(f"Blueprint gagal diregistrasi: {failed}")
        self.report = report


# ---------------------------------------------------------------------------
# Convenience decorator / helper  (menggantikan bpm.register_queue)
# ---------------------------------------------------------------------------

# Registry default — dipakai kalau tidak ada DI
_default_registry = BlueprintRegistry()


def register(
    target: Optional[LoadTarget] = None,
    *,
    priority: RegistrationPriority = RegistrationPriority.NORMAL,
    tags: Optional[set[str]] = None,
    registry: BlueprintRegistry = _default_registry,
) -> Union[LoadTarget, Callable[[LoadTarget], LoadTarget]]:
    """
    Decorator atau fungsi untuk mendaftarkan blueprint.

    Contoh sebagai decorator:

        @register(priority=RegistrationPriority.HIGH)
        class AuthBlueprint:
            def __init__(self, app: Flask): ...

    Contoh sebagai fungsi:

        register(AuthBlueprint, priority=RegistrationPriority.CRITICAL)
    """

    def _register(t: LoadTarget) -> LoadTarget:
        registry.add(t, priority=priority, tags=tags)
        return t

    if target is not None:
        # Dipanggil sebagai fungsi: register(MyClass)
        return _register(target)

    # Dipanggil sebagai decorator: @register(priority=...)
    return _register


def get_default_registry() -> BlueprintRegistry:
    """Akses registry default (untuk diinject ke BlueprintManager)."""
    return _default_registry
