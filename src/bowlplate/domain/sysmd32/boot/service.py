import sys
import time

from .model import (
    _RESET,
    _STATUS_COLOR,
    _STATUS_SYMBOL,
    BootFailure,
    BootReport,
    BootStage,
    StageStatus,
)


class BootSequencer:
    """
    Menjalankan daftar BootStage dan menampilkan output bergaya
    systemd / SysV init:

        [  OK  ] Starting werkzeug suppression...
        [  OK  ] Configuring Flask application...
        [ FAIL ] Registering blueprints...
    """

    _COL_WIDTH = 52  # lebar kolom deskripsi

    def __init__(self, logger, *, use_color: bool = True) -> None:
        self._logger = logger
        self._use_color = use_color and sys.stdout.isatty()
        self._stages: list[BootStage] = []

    def add(self, stage: BootStage) -> "BootSequencer":
        """Tambah stage; mendukung method chaining."""
        self._stages.append(stage)
        return self

    def run(self) -> BootReport:
        """
        Jalankan semua stage secara berurutan.

        Returns:
            BootReport berisi ringkasan hasil.

        Raises:
            BootFailure: jika ada stage required yang gagal.
        """
        self._print_banner()
        report = BootReport()

        for stage in self._stages:
            self._execute(stage, report)
            if stage.status == StageStatus.FAILED and stage.required:
                self._print_summary(report)
                raise BootFailure(stage)

        self._print_summary(report)
        return report

    def _execute(self, stage: BootStage, report: BootReport) -> None:
        if stage.condition is not None and not stage.condition():
            stage.status = StageStatus.SKIPPED
            self._print_stage_line(stage)
            report.record(stage)
            return

        stage.status = StageStatus.RUNNING
        t0 = time.perf_counter()

        try:
            stage.action()
            stage.status = StageStatus.OK
        except Exception as exc:
            stage.status = StageStatus.FAILED
            stage.error = exc
            self._logger.error(f"Boot stage '{stage.name}' failed: {exc}")
        finally:
            stage.duration = time.perf_counter() - t0

        self._print_stage_line(stage)
        report.record(stage)

    def _print_stage_line(self, stage: BootStage) -> None:
        symbol = _STATUS_SYMBOL[stage.status]
        label = stage.name[: self._COL_WIDTH].ljust(self._COL_WIDTH)
        ms = f"{stage.duration * 1000:>6.1f}ms"

        if self._use_color:
            color = _STATUS_COLOR[stage.status]
            bracket = f"{color}[{symbol}]{_RESET}"
        else:
            bracket = f"[{symbol}]"

        print(f"{bracket} {label} {ms}")

    def _print_banner(self) -> None:
        width = self._COL_WIDTH + 20
        print("─" * width)
        print(" Custombase Runtime  ·  Boot sequence")
        print("─" * width)

    def _print_summary(self, report: BootReport) -> None:
        print("─" * (self._COL_WIDTH + 20))
        ok = report.count(StageStatus.OK)
        fail = report.count(StageStatus.FAILED)
        skip = report.count(StageStatus.SKIPPED)
        total_ms = f"{report.total_duration * 1000:.1f}ms"
        print(f" {ok} ok  ·  {fail} failed  ·  {skip} skipped  ·  {total_ms} total")
        print("─" * (self._COL_WIDTH + 20))
