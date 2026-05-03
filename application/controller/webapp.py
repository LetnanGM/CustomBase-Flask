from data.configuration.internal import ServerConfig
from share.support.ui.webapp.server import FlaskServer
from application.bootstrap import WebController
import os

__all__ = ["ServerConfig"]

BASE = os.path.abspath(os.path.join(os.getcwd(), "application/ui/WebUI"))

class server:
    def __init__(self, config: ServerConfig = None) -> None:
        self._new_program()
        
        self._config = config if config else None
        
        self._template_folder = BASE + "\\frontend"
        self._static_folder = BASE + "\\static"
        self._debug = False
        
        self._set_config()
        
    def _new_program(self) -> None:
        from share.shared.logger.print import Logger
        current_object = Logger()
        current_object.debug(f"\n{'-'*50}\nNEW PROCESS STARTED!\n{'-'*50}\n", flag="SYSTEM")
        
        del current_object
    
    def _set_config(self) -> bool:
        
        if self._config:
            return False # no need build config
        
        self._config = ServerConfig(
            template_folder=self._template_folder,
            static_folder=self._static_folder,
            debug=self._debug
        )    
        
    def deploy(self) -> None:
        """
        Deployment
        """
        # load plugin with WC
        WebController()()
        
        instance = FlaskServer(config=self._config)
        instance.run() # run server