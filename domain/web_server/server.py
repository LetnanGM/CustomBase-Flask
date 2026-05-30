from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from flask import Flask

from share.contract.serverapp import ServerApp
from share.shared.logger.print import Logger

from data.configuration.internal.server.webapp import ServerConfig, banner
from .controller.blueprint.blueprint import (
    BlueprintManager,
    BlueprintRegistry,
    get_default_registry,
)
from .controller.route.routes import RouteManager

from ..sysmd32.boot.service import BootSequencer, BootStage, BootReport


@dataclass(frozen=True)
class ServerContext:
    """
    Immutable runtime state.  Dibuat sekali di FlaskServer.__init__
    dan diteruskan ke komponen lain via constructor injection.
    """

    config: ServerConfig
    app: Flask
    registry: BlueprintRegistry


class FlaskServer(ServerApp):
    """
    Flask server dengan Linux-style boot sequence.

    Boot stages (berurutan):
      1. Suppress werkzeug noise
      2. Configure Flask app
      3. Register blueprints
      4. Register routes
      5. Validate config
      6. Print listening info
    """

    def __init__(self, config: ServerConfig) -> None:
        super().__init__(config=config)
        self._flask_app = Flask(
            import_name=__name__,
            static_folder=config.static_folder,
            template_folder=config.template_folder,
        )

        registry = get_default_registry()

        self._ctx = ServerContext(
            config=config,
            app=self._flask_app,
            registry=registry,
        )
        self.logger = Logger()

        self._sequencer = BootSequencer(self.logger)
        self._build_boot_sequence()

    def _build_boot_sequence(self) -> None:
        """
        Definisikan semua stage di satu tempat.
        Urutan di sini = urutan eksekusi.
        """
        ctx = self._ctx

        self._sequencer.add(
            BootStage(
                name="Suppress werkzeug / CLI banner",
                action=self._suppress_werkzeug,
            )
        ).add(
            BootStage(
                name="Configure Flask application",
                action=lambda: self._configure_flask(ctx.app, ctx.config),
            )
        ).add(
            BootStage(
                name="Register blueprints",
                action=lambda: BlueprintManager(
                    app=ctx.app,
                    registry=ctx.registry,
                    logger=self.logger,
                    isolate_errors=False,
                ).register_blueprints(),
            )
        ).add(
            BootStage(
                name="Register routes",
                action=lambda: RouteManager(
                    app=ctx.app,
                    logger=self.logger,
                ).register_routes(),
            )
        ).add(
            BootStage(
                name="Validate server configuration",
                action=lambda: self._validate_config(ctx.config),
            )
        ).add(
            BootStage(
                name="Print listening address",
                action=lambda: self._print_listen_info(ctx.config),
            )
        )

    def setup(self) -> BootReport:
        """
        Jalankan boot sequence.  Biasanya dipanggil dari create_app().

        Returns:
            BootReport — berguna untuk health-check atau testing.

        Raises:
            BootFailure: jika required stage gagal.
        """
        print(banner())
        report = self._sequencer.run()
        self.logger.debug("Server setup completed.")
        return report

    def run(self) -> None:
        from share.support.os.termutil import clean_output
        import time

        time.sleep(2)
        clean_output()

        try:
            print(banner())

            super().run()
            self._flask_app.run(
                host=self._ctx.config.host,
                port=self._ctx.config.port,
                debug=self._ctx.config.debug,
                use_reloader=self._ctx.config.debug,
            )
        except Exception as exc:
            self.logger.error(f"FlaskServer.run() error: {exc}")
            raise

    @staticmethod
    def _suppress_werkzeug() -> None:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        cli = sys.modules.get("flask.cli")
        if cli:
            cli.show_server_banner = lambda *_: None

    @staticmethod
    def _configure_flask(app: Flask, config: ServerConfig) -> None:
        app.config.update(
            {
                "MAX_CONTENT_LENGTH": config.max_content_length,
                "SECRET_KEY": config.secret_key,
                "JSON_SORT_KEYS": False,
                "JSONIFY_PRETTYPRINT_REGULAR": True,
            }
        )

    @staticmethod
    def _validate_config(config: ServerConfig) -> None:
        if not config.host:
            raise ValueError("ServerConfig.host tidak boleh kosong.")
        if not (0 < config.port < 65536):
            raise ValueError(f"Port tidak valid: {config.port}")

    @staticmethod
    def _print_listen_info(config: ServerConfig) -> None:
        scheme = "https" if getattr(config, "ssl", False) else "http"
        print(f"\n  Listening on  {scheme}://{config.host}:{config.port}")
        if config.debug:
            print("  Mode          debug  (reload enabled)")
        print()
