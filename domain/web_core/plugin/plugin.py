from share.shared.logger.print import Logger
from share.support.ui.webapp.blueprint.blueprint import bpm
from data.configuration.internal.server.security import SECURITY_ALTAR, GUARDIAN_CRASH

class plugin:
    def __init__(self) -> None:
        self._blueprint = bpm()
        self._log = Logger() # Application Logger

    def _internal(self) -> bool:
        from ..controller.security import Security
        from .private import guardian
            
        if SECURITY_ALTAR:
            self._blueprint.register_queue(Security.setup)
            self._log.debug("'SecurityMiddleware' internal package registered!")
                
        if GUARDIAN_CRASH:
            self._blueprint.register_queue(guardian.setup)
            self._log.debug("'Guardian_Crash' internal package registered!")
            
            
        return True

    def _extract(self) -> None:
        """
        
        """
        import os
        import importlib
        
        path = os.path.abspath(os.path.join(os.getcwd(), "domain\\web_core\\plugin\\public"))
        plugin_external = os.listdir(path)
        
        if not plugin_external:
            return False
        
        for plugin in plugin_external:
            plugin_path = path + f"\\{plugin}"
            self._log.debug(f"Trying load '{plugin}'..")
            if os.path.isdir(plugin_path):
                try:
                    module_name = f"domain.web_core.plugin.public.{plugin}.main"
                    module = importlib.import_module(module_name)
                    self._log.debug(f"[{plugin}]: detected object module '{module.__name__}', finding 'setup_me'..")
                    
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if isinstance(obj, type):
                            if hasattr(obj, "setup_me"):
                                self._log.debug(f"[{plugin}]:{obj.__name__}: setup_me finded! object registered into Queue.")
                                instance = obj()
                                self._blueprint.register_queue(instance.setup_me)
                            else:
                                self._log.debug(f"[{plugin}]:{obj.__name__}: object doesn't have 'setup_me' function, skiped!")
                        else:
                            continue
                except Exception as e:
                    print(f"[ERROR:PLUGIN]: > '{plugin}' have error '{e}'.")
            else:
                print(f"[ERROR]: Cannot find folder plugin '{plugin}'")
        
    def load_all(self): 
        self._internal()
        self._extract()
        
        return True