"""
Community-Security Flask Middleware
Plugin dikonfigurasi manual lewat Config class.
Mendukung priority & depends_on untuk urutan eksekusi.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable, NamedTuple

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_compress import Compress
from flask_caching import Cache


class PLUGIN(StrEnum):
    CORS = "cors"
    RATELIMIT = "ratelimit"
    TALISMAN = "talisman"
    COMPRESS = "compress"
    CACHE = "cache"


@dataclass
class Config:
    ENABLED_PLUGINS: set[PLUGIN] = field(
        default_factory=lambda: {
            PLUGIN.CORS,
            PLUGIN.RATELIMIT,
        }
    )

    RATELIMIT_DEFAULT: list[str] = field(
        default_factory=lambda: ["200 per day", "50 per hour"]
    )
    CACHE_TYPE: str = "SimpleCache"
    TALISMAN_FORCE_HTTPS: bool = True


# ---------------------------------------------------------
# Registry — sekarang menyimpan priority & depends_on
# ---------------------------------------------------------
class PluginEntry(NamedTuple):
    handler: Callable[[Flask, Config], None]
    priority: int  # lebih kecil = dijalankan lebih dulu
    depends_on: tuple[PLUGIN, ...]


class PluginRegistry:
    def __init__(self) -> None:
        self._registry: dict[PLUGIN, PluginEntry] = {}

    def register(
        self,
        key: PLUGIN,
        priority: int = 100,
        depends_on: tuple[PLUGIN, ...] = (),
    ):
        def decorator(fn: Callable[[Flask, Config], None]):
            self._registry[key] = PluginEntry(fn, priority, depends_on)
            return fn

        return decorator

    def available(self) -> set[PLUGIN]:
        return set(self._registry.keys())

    def resolve_order(self, selected: set[PLUGIN]) -> list[PLUGIN]:
        """Topological sort (depends_on) + priority sebagai tie-breaker."""
        unknown = selected - self.available()
        if unknown:
            raise ValueError(f"Plugin tidak dikenal: {unknown}")

        visited: set[PLUGIN] = set()
        temp_mark: set[PLUGIN] = set()
        ordered: list[PLUGIN] = []

        def visit(node: PLUGIN) -> None:
            if node in visited:
                return
            if node in temp_mark:
                raise ValueError(f"Circular dependency terdeteksi pada '{node}'")

            temp_mark.add(node)
            entry = self._registry[node]
            for dep in entry.depends_on:
                if dep not in self.available():
                    raise ValueError(
                        f"Plugin '{node}' depends_on '{dep}' yang tidak terdaftar."
                    )
                if dep in selected:
                    visit(dep)
            temp_mark.discard(node)
            visited.add(node)
            ordered.append(node)

        # urutkan dulu berdasar priority supaya hasil sort stabil & predictable
        for plugin in sorted(selected, key=lambda p: self._registry[p].priority):
            visit(plugin)

        return ordered

    def run(self, key: PLUGIN, app: Flask, config: Config) -> None:
        self._registry[key].handler(app, config)


registry = PluginRegistry()


# priority rendah dieksekusi lebih dulu
@registry.register(PLUGIN.TALISMAN, priority=10)
def _setup_talisman(app: Flask, config: Config) -> None:
    Talisman(app, force_https=config.TALISMAN_FORCE_HTTPS)


@registry.register(PLUGIN.CORS, priority=20, depends_on=(PLUGIN.TALISMAN,))
def _setup_cors(app: Flask, config: Config) -> None:
    # contoh: CORS "bergantung" secara logis pada Talisman
    # supaya security header sudah terpasang duluan
    CORS(app)


@registry.register(PLUGIN.COMPRESS, priority=30)
def _setup_compress(app: Flask, config: Config) -> None:
    Compress(app)


@registry.register(PLUGIN.RATELIMIT, priority=40)
def _setup_ratelimit(app: Flask, config: Config) -> None:
    Limiter(
        get_remote_address,
        app=app,
        default_limits=config.RATELIMIT_DEFAULT,
    )


@registry.register(PLUGIN.CACHE, priority=50)
def _setup_cache(app: Flask, config: Config) -> None:
    Cache(app, config={"CACHE_TYPE": config.CACHE_TYPE})


class Middleware:
    __PLUGIN_NAME__ = "Community-Security Flask"
    __VERSION__ = "1.0.0"
    __DEVELOPER__ = "LetnanDev"
    __SUPPORTED__ = ["Flask"]

    def __init__(self, config: Config | None = None) -> None:
        self._app: Flask | None = None
        self._config: Config = config or Config()

    def main_routes_register(self) -> None:
        pass

    def main_blueprint_register(self) -> None:
        pass

    def main_plugin_register(self) -> None:
        app = self._app
        if app is None:
            raise RuntimeError("App belum di-set. Panggil setup() dulu.")

        order = registry.resolve_order(self._config.ENABLED_PLUGINS)
        for plugin in order:
            registry.run(plugin, app, self._config)

    def setup(self, app: Flask) -> None:
        self._app = app

        self.main_routes_register()
        self.main_blueprint_register()
        self.main_plugin_register()
