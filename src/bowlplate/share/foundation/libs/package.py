import importlib.util
from typing import Any, Callable, Type

from share.shared.handler.decorator import validate_parameter
from share.shared.logger.print import Logger

log = Logger()

modules: dict = {}
cached: dict = {}
alias: dict = {}


class _Registry:
    def __init__(self):
        pass

    @property
    def modules(self) -> dict:
        return modules

    @property
    def cached(self) -> dict:
        return cached

    @property
    def alias(self) -> dict:
        return alias


class RegistryPackageManager:
    def __init__(self):
        self._object = None

    @staticmethod
    def return_value_of() -> _Registry:
        return _Registry

    @validate_parameter({"path": str})
    def load_package(self, path: str) -> importlib.util.spec_from_file_location:
        """
        Load Package from path
        """

        spec = importlib.util.spec_from_file_location("mod", path)
        log.debug(f"package '{path}' as spec > {spec}", flag="import")

        mod = importlib.util.module_from_spec(spec=spec)
        log.debug(f"module instance > {mod}", flag="import")

        spec.loader.exec_module(mod)
        log.debug("running spec.loader.exec_module(mod)..", flag="import")

        return mod


class package:
    def __init__(self):
        self._RPM = RegistryPackageManager()

    def use(self, name: str) -> Any:
        """
        import new package and cached.
        """
        log.debug(f"Importing package '{name}'..", flag=f"{name}:USE")

        if name in modules:
            log.debug(f"returning instance '{name}'", flag=f"{name}:USE")
            return modules[name]

        path = f"share/foundation/libs/package_lib/{name.replace('.', '/')}/main.py"
        mod = package._load_module(path)
        log.debug(f"[{name}:USE]: registering and received module `{mod}`..")
        modules[name] = mod
        log.debug(f"[{name}:USE]: object registered into Registry cached.")
        return mod

    def spawn(name: str):
        """
        build new instance and interconnecting library with 'Service'.
        """
        log.debug(f"[{name}:SPAWN]: spawning object '{name}'..")
        if name in cached:
            log.debug(f"[{name}:SPAWN]: object already spawned, return value cached..")
            return cached[name]

        mod = package.use(name)
        # 'Service' class is interconnection library with other library
        # build it, if you not use other library, just keep it empty.
        if hasattr(mod, "Service"):
            log.debug(f"[{name}:SPAWN]: initializing 'Service' class..")
            instance = mod.Service()  # initailize Service
        else:
            raise Exception(
                f"'{name}' doesnt have 'Service' class for interconnecting library!"
            )

        cached[name] = instance
        log.debug(
            f"[{name}:SPAWN]: object successfully spawned and registered. returning.."
        )
        return instance

    def build(name: str):
        """
        injecting package into globals with `globals()` syntax.
        """
        log.debug(f"[{name}:build]: building object into globals..")
        instance = package.spawn(name)
        log.debug(f"[{name}:build]: object builded, registering into globals..")
        for attr in dir(instance):
            log.debug(f"[{name}:build]: detected attribute '{attr}'")
            if not attr.startswith("_"):
                log.debug(f"[{name}:build]: '{attr}' registered into globals")
                globals()[attr] = getattr(instance, attr)
            else:
                log.debug(
                    f"[{name}:build]: failed registered '{attr}' into globals, attribute must be public! not private."
                )

    def defer(name):
        """lazy load package, recomended for use!"""
        from .component.deferred import Deferred

        return Deferred(package, name)

    def async_load():
        """asynchronus load package, not recommended cause CPU can idle for a while minute."""
        return NotImplementedError("Currently async load not implemented, wait update!")

    def alias(alias: str, instance_object: Type | Callable):
        from share.shared.exceptions import NameAliasAlreadyInUse

        if alias in alias.keys():
            raise NameAliasAlreadyInUse(
                "Name alias already in use! try another unique alias name"
            )

        alias[alias] = instance_object
        return instance_object
