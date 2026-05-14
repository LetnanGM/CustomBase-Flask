from data.configuration.internal import ServerConfig
from application.bootstrap import WebController, UI, Server
import os

__all__ = ["ServerConfig"]

BASE = os.path.abspath(os.path.join(os.getcwd(), "application/ui/WebUI"))

class server(UI):
    def __init__(self, config: ServerConfig = None) -> None:
        self._config = config if config else None
        
        self._template_folder = BASE + "\\frontend"
        self._static_folder = BASE + "\\static"
        self._debug = False
        
        self._set_config()
    
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
        
        instance = Server()(config=self._config)
        instance.setup()
        instance.run() # run server