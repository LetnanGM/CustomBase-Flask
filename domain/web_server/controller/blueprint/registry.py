from typing import Optional
from .model import LoadTarget, RegistrationPriority, BlueprintEntry

import threading

class BlueprintRegistry:
    """
    Thread-safe registry untuk menyimpan blueprint sebelum app tersedia.

    Menggantikan `var.BP` (Queue) + `var.APP` (Flask) dengan
    objek eksplisit yang bisa di-inject atau di-mock saat testing.
    """

    def __init__(self, maxsize: int = 200) -> None:
        self._entries: list[BlueprintEntry] = []
        self._lock = threading.Lock()
        self._maxsize = maxsize

    def add(
        self,
        target: LoadTarget,
        priority: RegistrationPriority = RegistrationPriority.NORMAL,
        tags: Optional[set[str]] = None,
    ) -> None:
        """Daftarkan blueprint ke registry."""
        with self._lock:
            if len(self._entries) >= self._maxsize:
                raise OverflowError(
                    f"Registry penuh ({self._maxsize} entri). "
                    "Naikkan maxsize atau kurangi jumlah blueprint."
                )
            entry = BlueprintEntry(
                target=target,
                priority=priority,
                tags=frozenset(tags or []),
            )
            self._entries.append(entry)

    def drain(self) -> list[BlueprintEntry]:
        """Ambil semua entri terurut berdasarkan prioritas, lalu kosongkan registry."""
        with self._lock:
            sorted_entries = sorted(self._entries)
            self._entries.clear()
            return sorted_entries

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    def __bool__(self) -> bool:
        return len(self) > 0
