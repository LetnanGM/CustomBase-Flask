from typing import Dict, Any, Callable, Type
from pydantic import BaseModel, field_validator


class processorState:
    _database = {}


class Item(BaseModel):
    label: str
    object: Any | Callable | Type

    @field_validator("object")
    def object_validation(object: Any):
        if not isinstance(object, Any | Callable | Type):
            return "UNKNOWN"

        return object

    @field_validator("label")
    def label_sanitizer(label: str) -> str:
        import bleach

        return bleach.clean(label)


class ContextProcessor:
    __TITLE__ = "ContextProcessor Flask Manager"
    __VERSION__ = "1.0.0"
    __AUTHOR__ = "LetnanGM"
    __server__ = "Flask"

    def __init__(self, app) -> None:
        self.app = app

        self.main_processor_register()

    def main_context_register(self):
        @self.app.context_processor
        def inject_dynamic_context():
            return processorState._database

    def main_processor_register(self):
        self.main_context_register()


class RegistryContextProcessor:
    def __init__(self) -> None:
        pass

    @property
    def all(self) -> Dict[str, Any]:
        return processorState._database

    @staticmethod
    def register(key: str, value: Any) -> bool:
        """
        register - ContextProcessor
        Registered every start

        add your variable or function to jinja syntax with this!
        usage:
        >>> ContextProcessor.register('my_name', 'Jhon Doe')

        OR u can do this:
        >>> cp = ContextProcessor()
        >>> cp.register('my_name', 'Alice')
        """
        if not value:
            return False
        object = Item(label=key, object=value)

        processorState._database[object.label] = object.object

        return True
