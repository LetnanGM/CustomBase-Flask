from typing import Dict


class Service:
    SERVICE_TITLE: str = "Server FL"
    SERVICE_VERSION: str = "1.0.0"
    STATUS = "Healthy"
    ENDPOINTS: Dict[str, str] = {}
    ADMIN_KEY = []
    MAINTENANCE = False

    def __call__(*args, **kwargs) -> None:
        pass

    @property
    def to_dict() -> None:
        if not Service.ENDPOINTS:
            Service.endpoints_load()

        return {
            "title": Service.SERVICE_TITLE,
            "version": Service.SERVICE_VERSION,
            "status": Service.STATUS,
            "endpoints": Service.ENDPOINTS,
        }
