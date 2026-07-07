from abc import ABC, abstractmethod


class UI(ABC):
    def __init__(self) -> None:
        self._start_program()

    def _start_program(self) -> None:
        from share.builtns.logger.print import Logger

        current_object = Logger()
        current_object.debug(
            f"\n{'-'*50}\nNEW PROCESS STARTED!\n{'-'*50}\n", flag="SYSTEM"
        )

        del current_object

    @abstractmethod
    def deploy(self) -> None:
        raise NotImplementedError("the deploy are not implemented.")
