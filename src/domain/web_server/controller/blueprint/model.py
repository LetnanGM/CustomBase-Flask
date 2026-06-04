from enum import IntEnum
from typing import Union, Callable, Optional
from dataclasses import dataclass, field

# global model
LoadTarget = Union[type, Callable]


class RegistrationPriority(IntEnum):
    """Urutan registrasi blueprint. Nilai lebih kecil = lebih awal."""

    CRITICAL = 0  # auth, error handlers
    HIGH = 10  # core feature routes
    NORMAL = 20  # fitur biasa
    LOW = 30  # optional / plugin


@dataclass(frozen=True)
class BlueprintEntry:
    """Satu unit blueprint yang akan diregistrasi."""

    target: LoadTarget
    priority: RegistrationPriority = RegistrationPriority.NORMAL
    tags: frozenset[str] = field(default_factory=frozenset)

    def __lt__(self, other: "BlueprintEntry") -> bool:
        return self.priority < other.priority


@dataclass
class RegistrationHooks:
    """
    Opsional. Inject hook untuk observability, validasi, dsb.

    Contoh penggunaan:
        hooks = RegistrationHooks(
            before=lambda e: metrics.increment("blueprint.load.attempt"),
            after=lambda e: metrics.increment("blueprint.load.success"),
            on_error=lambda e, ex: sentry.capture(ex),
        )
    """

    before: Optional[Callable[[BlueprintEntry], None]] = None
    after: Optional[Callable[[BlueprintEntry], None]] = None
    on_error: Optional[Callable[[BlueprintEntry, Exception], None]] = None
