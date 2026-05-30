from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------

class StageStatus(str, Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    OK       = "ok"
    FAILED   = "failed"
    SKIPPED  = "skipped"


# ---------------------------------------------------------------------------
# Terminal styling helpers
# ---------------------------------------------------------------------------

_RESET = "\033[0m"

_STATUS_COLOR: dict[StageStatus, str] = {
    StageStatus.PENDING:  "\033[90m",   # dark gray
    StageStatus.RUNNING:  "\033[34m",   # blue
    StageStatus.OK:       "\033[32m",   # green
    StageStatus.FAILED:   "\033[31m",   # red
    StageStatus.SKIPPED:  "\033[33m",   # yellow
}

_STATUS_SYMBOL: dict[StageStatus, str] = {
    StageStatus.PENDING:  "    ",
    StageStatus.RUNNING:  " ── ",
    StageStatus.OK:       "  OK  ",
    StageStatus.FAILED:   " FAIL ",
    StageStatus.SKIPPED:  " SKIP ",
}


# ---------------------------------------------------------------------------
# BootStage — one unit of work in the boot sequence
# ---------------------------------------------------------------------------

@dataclass
class BootStage:
    """
    Represents a single step in the boot sequence.

    Attributes:
        name:      Human-readable description shown in the boot log.
        action:    Zero-argument callable that performs the work.
        required:  If True and the stage fails, BootSequencer raises BootFailure.
        condition: Optional zero-argument predicate; when it returns False the
                   stage is skipped without calling *action*.
        status:    Updated by BootSequencer during execution.
        duration:  Wall-clock seconds elapsed during *action* (set after run).
        error:     Exception captured if the stage raised, otherwise None.
    """

    name:      str
    action:    Callable[[], None]
    required:  bool                      = True
    condition: Optional[Callable[[], bool]] = None

    # --- mutable runtime state (not constructor args) ---
    status:   StageStatus               = field(default=StageStatus.PENDING, init=False)
    duration: float                     = field(default=0.0,                 init=False)
    error:    Optional[Exception]       = field(default=None,                init=False)


# ---------------------------------------------------------------------------
# BootReport — collects per-stage results and aggregate metrics
# ---------------------------------------------------------------------------

class BootReport:
    """
    Accumulates BootStage results produced by a single BootSequencer.run() call.
    """

    def __init__(self) -> None:
        self._stages:         list[BootStage] = []
        self._start_time:     float           = time.perf_counter()
        self.total_duration:  float           = 0.0

    # --- called by BootSequencer ---

    def record(self, stage: BootStage) -> None:
        """Append a completed stage and update cumulative duration."""
        self._stages.append(stage)
        self.total_duration += stage.duration

    # --- query helpers ---

    def count(self, status: StageStatus) -> int:
        """Return number of stages that finished with *status*."""
        return sum(1 for s in self._stages if s.status == status)

    @property
    def stages(self) -> list[BootStage]:
        """Read-only view of recorded stages in execution order."""
        return list(self._stages)

    @property
    def success(self) -> bool:
        """True when no required stage failed."""
        return not any(
            s.status == StageStatus.FAILED and s.required for s in self._stages
        )

    def __repr__(self) -> str:  # pragma: no cover
        ok   = self.count(StageStatus.OK)
        fail = self.count(StageStatus.FAILED)
        skip = self.count(StageStatus.SKIPPED)
        ms   = self.total_duration * 1000
        return f"<BootReport ok={ok} failed={fail} skipped={skip} total={ms:.1f}ms>"


# ---------------------------------------------------------------------------
# BootFailure — raised when a required stage fails
# ---------------------------------------------------------------------------

class BootFailure(RuntimeError):
    """
    Raised by BootSequencer when a *required* BootStage fails.

    Attributes:
        stage: The BootStage that triggered the failure.
    """

    def __init__(self, stage: BootStage) -> None:
        self.stage = stage
        cause = f": {stage.error}" if stage.error else ""
        super().__init__(f"Required boot stage '{stage.name}' failed{cause}")