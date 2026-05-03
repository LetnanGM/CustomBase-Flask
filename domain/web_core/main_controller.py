class controller:
    def __init__(self) -> None:
        from .plugin.plugin import plugin
        
        self._plugin = plugin()
        self.main_service_loader()
        
    def main_service_loader(self) -> bool:
        self._plugin.load_all()
        
        return True
    