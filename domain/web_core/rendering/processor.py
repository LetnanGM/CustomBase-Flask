from typing import Dict, Any

_database = {}

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
            return _database
        
    def main_processor_register(self):
        self.main_context_register()
    
class RegistryContextProcessor:
    def __init__(self) -> None:
        pass

    @property
    def all(self) -> Dict[str, Any]:
        return _database
    
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
        
        _database[key] = value
        
        return True