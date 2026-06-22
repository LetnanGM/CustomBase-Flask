import uuid
from functools import wraps
from dataclasses import dataclass

from flask import Flask, jsonify, render_template, request

from bootstrap.config import reader
from share.shared.logger.server_logger import ServerLogger

read = reader()
service = read.get("service.json")["config"]

@dataclass
class Service:
    ADMIN_KEY: str = "ABC"
    MAINTENANCE = False
    SERVICE_TITLE = "APC"
    SERVICE_VERSION = "1.0.0"

class routeState:
    cache: dict = {}
    routes: dict = {}
    logger: ServerLogger = None


class route:
    def __init__(self):
        self._log = routeState.logger

    def register(self, path: str, method=["GET"]) -> None:
        """ """
        if not path:
            raise ValueError("path are not recognized")

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                routeState.routes[str(uuid.uuid4())] = {
                    "path": path,
                    "method": method,
                    "func": func,
                }

                self._log.debug(f"routes '{path}' loggined.")

            return wrapper

        return decorator


class RouteManager:
    """Manages route registration for the Flask app"""

    def __init__(self, app: Flask, logger: ServerLogger):
        routeState.logger = logger

        self.app = app
        self.logger = logger

    def register_routes(self) -> None:
        """Register all application routes"""
        self._register_main_request()
        self._register_main_routes()

        self.logger.debug("All routes registered successfully")

    def _register_main_request(self) -> None:
        """ """

        @self.app.before_request
        def seize_server():
            if Service.MAINTENANCE:
                if (
                    request.headers.get("X-ADMIN-KEY")
                    and Service.ADMIN_KEY
                    and request.headers.get("X-ADMIN-KEY") in Service.ADMIN_KEY
                ):
                    return None

                return "SERVER ARE IN MAINTENANCE!", 503

    def _register_main_routes(self) -> None:
        """Register main application routes"""

        @self.app.route("/")
        def index():
            """Main landing page"""
            return render_template("index.html"), 200

        @self.app.route("/health")
        def health_check():
            """Health check endpoint"""
            return (
                jsonify({"status": Service.STATUS, "service": Service.SERVICE_TITLE}),
                200,
            )

        @self.app.route("/api/v1/info")
        def api_info():
            """API information endpoint"""
            return (
                jsonify(
                    {"version": Service.SERVICE_VERSION, "endpoints": []}
                ),
                200,
            )
