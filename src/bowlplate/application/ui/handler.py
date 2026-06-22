import os
from pathlib import Path

_path_webui: str = "./WebUI"
_path_instance: str = str(Path(_path_webui).resolve())

_frontend = "frontend"
_static = "static"

class web:
    @staticmethod
    def frontend_path() -> str:
        """
        Handling Path frontend agar tidak bercampur ke WebCore.
        """
        return os.path.join(_path_instance, _frontend)
    
    @staticmethod
    def static_path() -> str:
        """
        Handling Path static agar tidka bercampur berat ke WebCore
        """
        return os.path.join(_path_instance, _static)
    
__all__ = ["web"]