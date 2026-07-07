from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def validate_parameter(expected_types: dict):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            params = dict(zip(func.__code__.co_varnames, args))
            params.update(kwargs)

            for param, expected_type in expected_types.items():
                if param not in params:
                    raise ValueError(f"Parameter {param} are not found!")

                if not isinstance(params[param], expected_type):
                    raise TypeError(
                        f"Parameter {param} must be {expected_type.__name__}"
                    )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def required_parameter(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) + len(kwargs) != func.__code__.co_argcount:
            raise TypeError(
                "Parameter are not completed, all of parameter must be fielded!"
            )
        return func(*args, **kwargs)

    return wrapper


__all__ = ["validate_parameter", "required_parameter"]
