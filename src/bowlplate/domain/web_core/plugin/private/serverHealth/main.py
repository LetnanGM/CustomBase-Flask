from datetime import timedelta

import psutil


class Compute:
    def __init__(self) -> None:
        self._compute: str = ""

    def _gb(value: bytes) -> str:
        return f"{value/1024/1024/1024:.1f} GB"

    def hostname(self) -> str:
        import socket

        return socket.gethostname()

    def uptime(self) -> int:
        return timedelta(seconds=int(psutil.boot_time()))

    def cpu(self) -> dict:
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "load_average": "unknown",
            "core_count": psutil.cpu_count(),
        }

    def top_cpu(self) -> str:
        return sorted(
            psutil.process_iter(["pid", "name", "cpu_percent"]),
            key=lambda p: p.info["cpu_percent"],
            reverse=True,
        )[:5]

    def ram(self) -> dict:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "memory": mem.percent,
            "mem_stats": f"{self._gb(mem.used)}/{self._fb(mem.total)}",
            "swap": swap.percent,
            "swap_stats": f"{self._gb(swap.used)}/{self._gb(swap.total)}",
        }

    def top_ram(self) -> list:
        return sorted(
            psutil.process_iter(["pid", "name", "memory_percent"]),
            key=lambda p: p.info["memory_percent"],
            reverse=True,
        )[:5]

    def disk(self) -> dict:
        data = []
        for part in psutil.disk_partitions():
            partitions = {}
            try:
                usage = psutil.disk_usage(part.mountpoint)
                warn = True if usage.percent > 80 else False
                partitions = {
                    part.device: {
                        "mountpoint": part.mountpoint,
                        "usage_percent": usage.percent,
                        "stats": f"{self._gb(usage.used)}/{self._gb(usage.total)}",
                        "warn": {
                            "status": warn,
                            "message": [
                                (
                                    f"WARNING: Disk {part.mountpoint} >80!!!"
                                    if warn
                                    else None
                                )
                            ],
                        },
                    }
                }
                data.append(partitions)
            except Exception as e:
                print(e)

    def disk_io(self) -> dict:
        io = psutil.disk_io_counters()
        return {"read": {self._gb(io.read_bytes)}, "write": {self._gb(io.write_bytes)}}
