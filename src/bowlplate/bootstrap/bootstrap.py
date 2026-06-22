# MAKE CONNECTION HERE

from domain.web_server.model import ServerConfig
from share.contract.ui.local import UI

__all__ = ["UI", "reader", "ServerConfig"]

def WebServer() -> type:
    from application.controller.webapp import server

    return server


def Server() -> type:
    from domain.web_server.server import FlaskServer

    return FlaskServer


def WebController() -> type:
    from domain.web_core.main_controller import controller

    return controller


def RegistryContextProcessor() -> type:
    from domain.web_core.rendering.processor import RegistryContextProcessor

    return RegistryContextProcessor


# package layer
class blueprint:
    def BlueprintManager() -> type:
        from domain.web_server.controller.blueprint.blueprint import \
            BlueprintManager

        return BlueprintManager

    def registerFunc() -> callable:
        from domain.web_server.controller.blueprint.blueprint import register

        return register
