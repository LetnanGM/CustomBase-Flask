from functools import wraps

from flask import jsonify


def on_maintenance(use_template: bool = True):
    def maintenance(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if use_template:
                return "This feature is still evolve! Thanks for use the service.", 503
            if not use_template:
                return (
                    jsonify(
                        {
                            "status": False,
                            "reason": "Feature are still in evolve :D",
                            "data": {},
                        }
                    ),
                    503,
                )

            return func(*args, **kwargs)

        return wrapper

    return maintenance
