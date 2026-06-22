from bootstrap.bootstrap import blueprint
from bootstrap.config import reader

from share.shared.logger.print import Logger

register = blueprint.registerFunc()


class pluginModel:
    public_plugin = "domain\\web_core\\plugin\\public"
    module_package = "domain.web_core.plugin.public"
    main_package = "main"

    setup_function: str = "setup_me"


class plugin:
    def __init__(self) -> None:
        self._blueprint = blueprint.BlueprintManager()
        self._log = Logger()  # Application Logger

    def _internal(self) -> bool:
        from ..controller.security import Security
        from .private import guardian
        
        read = reader()
        
        data = read.get("security.json")
        data = data["config"]["properties"]
        
        if data["SECURITY_ALTAR"]:
            register(Security.setup)
            self._log.debug("'SecurityMiddleware' internal package registered!")

        if data["GUARDIAN_CRASH"]:
            register(guardian.setup)
            self._log.debug("'Guardian_Crash' internal package registered!")

        return True

    def _extract(self) -> None:
        """ """
        import importlib
        import os

        path = os.path.abspath(os.path.join(os.getcwd(), pluginModel.public_plugin))
        plugin_external = os.listdir(path)

        if not plugin_external:
            return False

        for plugin in plugin_external:
            plugin_path = path + f"\\{plugin}"
            self._log.debug(f"Trying load '{plugin}'..")
            if os.path.isdir(plugin_path):
                try:
                    module_name = (
                        pluginModel.module_package
                        + f".{plugin}."
                        + pluginModel.main_package
                    )
                    module = importlib.import_module(module_name)
                    self._log.debug(
                        f"[{plugin}]: detected object module '{module.__name__}', finding 'setup_me'.."
                    )

                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if isinstance(obj, type):
                            if hasattr(obj, pluginModel.setup_function):
                                self._log.debug(
                                    f"[{plugin}]:{obj.__name__}: {pluginModel.setup_function} finded! object registered into Queue."
                                )
                                instance = obj()

                                # confused here :( i just want 'setup_me' can modified by pluginModel
                                register(instance.setup_me)
                            else:
                                self._log.debug(
                                    f"[{plugin}]:{obj.__name__}: object doesn't have '{pluginModel.setup_function}' function, skiped!"
                                )
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
