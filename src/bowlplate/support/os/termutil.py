from atexit import register

from .system import client as cl


def clean_output():
    import os

    os.system("cls") if cl.OperatingSystem == "Windows" else os.system("clear")


class termutil:
    def __init__(self):
        self.client: str = cl.OperatingSystem

    def exit_(*args, **kwargs) -> None:
        input("[SYS] Press enter before exit...")
        print("+=> Exiting!")


register(termutil.exit_)
