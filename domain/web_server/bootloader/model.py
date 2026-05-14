from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional

class StageStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    OK      = auto()
    FAILED  = auto()
    SKIPPED = auto()


_STATUS_SYMBOL = {
    StageStatus.OK:      "  OK  ",
    StageStatus.FAILED:  " FAIL ",
    StageStatus.SKIPPED: " SKIP ",
    StageStatus.RUNNING: "  ··  ",
}

_STATUS_COLOR = {
    StageStatus.OK:      "\033[32m",   # green
    StageStatus.FAILED:  "\033[31m",   # red
    StageStatus.SKIPPED: "\033[33m",   # yellow
    StageStatus.RUNNING: "\033[36m",   # cyan
}
_RESET = "\033[0m"

@dataclass
class BootStage:
    """
    Satu tahap dalam proses startup.

    Parameters
    ----------
    name:
        Label singkat yang tampil di console (≤ 40 karakter).
    action:
        Callable yang dipanggil saat stage dieksekusi.
        Jika raise → stage dianggap FAILED.
    required:
        False → kegagalan hanya menghasilkan SKIPPED, bukan abort.
    condition:
        Jika disediakan, stage di-skip ketika condition() → False.
    """
    name:      str
    action:    Callable[[], None]
    required:  bool = True
    condition: Optional[Callable[[], bool]] = None
    status:    StageStatus = field(default=StageStatus.PENDING, init=False)
    duration:  float = field(default=0.0, init=False)
    error:     Optional[Exception] = field(default=None, init=False)


@dataclass
class BootReport:
    _stages: list[BootStage] = field(default_factory=list)

    def record(self, stage: BootStage) -> None:
        self._stages.append(stage)

    def count(self, status: StageStatus) -> int:
        return sum(1 for s in self._stages if s.status == status)

    @property
    def total_duration(self) -> float:
        return sum(s.duration for s in self._stages)

    @property
    def success(self) -> bool:
        return self.count(StageStatus.FAILED) == 0


class BootFailure(RuntimeError):
    """Dilempar saat required stage gagal."""
    def __init__(self, stage: BootStage) -> None:
        super().__init__(
            f"Required boot stage failed: '{stage.name}' — {stage.error}"
        )
        self.stage = stage

