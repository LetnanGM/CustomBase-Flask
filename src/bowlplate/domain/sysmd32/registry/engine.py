import json
from pathlib import Path


class Registry:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(exist_ok=True)

    def path(self, key: str):
        return self.root / f"{key}.json"

    def set(self, key: str, value: dict):
        with open(self.path(key), "w") as f:
            json.dump(value, f, indent=2)

    def get(self, key: str):
        try:
            with open(self.path(key)) as f:
                return json.load(f)
        except FileNotFoundError:
            return None