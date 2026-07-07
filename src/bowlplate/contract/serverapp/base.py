from abc import ABC, abstractmethod
from typing import Optional

from bootstrap.bootstrap import ServerConfig
from share.builtns.logger.server_logger import ServerLogger


class ServerApp(ABC):
    def __init__(
        self, config: Optional[ServerConfig], import_name: str = __name__
    ) -> None:
        """
        Server WebApp
        """
        self.config = config
        self.import_name = import_name
        self.logger = ServerLogger()
        self.app: type = (
            None  # set your instance service here before route or start server
        )

    @abstractmethod
    def setup(self) -> None:
        """
        Setup routes and blueprints
        """

        self.logger.info("Initializing Server setup..")

        # here is log configuration
        self.logger.info("Server Configuration:")
        for key, value in self.config.to_dict().items():
            self.logger.info(f"     {key} : {value}")

    @abstractmethod
    def run(self) -> None:
        """
        Start the instance server
        """
        self.logger.info(f"Starting server on {self.config.host}:{self.config.port}")
        self.logger.info(f"Debug mode: {'ON' if self.config.debug else 'OFF'}")
        pass

    def get_instance(self) -> None:
        """Return instance server for external use"""
        return self.app
