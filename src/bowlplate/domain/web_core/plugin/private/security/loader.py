from typing import Any, Dict

from flask import Flask

from domain.web_core.bootstrap import SMiddleware_logger, global_protection_logger
from ....protector import (
    CSRFProtection,
    ErrorHandler,
    InputValidator,
    OBSecurity,
    RateLimiter,
)
from ....rendering.processor import ContextProcessor
from .middleware import setup_securitychain


class loader_security:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.data_mapping: Dict[str, Any] = {
            "RateLimiter": {"args": "", "obj": RateLimiter},
            "InputValiator": {
                "args": "",
                "obj": InputValidator,
            },
            "CSRFProtection": {
                "args": "app",
                "obj": CSRFProtection,
            },
            "OBSecurity": {
                "args": "app",
                "obj": OBSecurity,
            },
            "ErrorPage": {
                "args": "app",
                "obj": ErrorHandler,
            },
            "ContextProcessor": {
                "args": "app",
                "obj": ContextProcessor,
            },
            "SetupSecurity": {
                "args": "app",
                "obj": setup_securitychain,
            },
        }

        self.load()

    def load(self):
        for name, data in self.data_mapping.items():
            args, exe = data.get("args", ""), data.get("obj", "")

            if args == "app":
                exe(app=self.app)
            else:
                exe()

            global_protection_logger.debug(f"'{name}' successfully loaded!")

        SMiddleware_logger.debug(
            "'Middleware' all resource and security successfully loaded!"
        )
