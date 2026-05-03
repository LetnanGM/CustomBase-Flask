# MAKE CONNECTION HERE

def WebServer() -> type:
    from .controller.webapp import server
    
    return server

def WebController() -> type:
    from domain.web_core.main_controller import controller
    return controller

def RegistryContextProcessor() -> type:
    from domain.web_core.rendering.processor import RegistryContextProcessor
    return RegistryContextProcessor