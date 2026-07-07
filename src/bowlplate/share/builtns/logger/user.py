from dataclasses import dataclass


@dataclass
class logger:
    verbose: int = 1


@dataclass
class client:
    logger = logger
