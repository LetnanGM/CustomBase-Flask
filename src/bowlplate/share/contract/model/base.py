from abc import ABC
from dataclasses import asdict, fields
from typing import Any, Dict, List, Self


class InternalModel(ABC):
    """Contract for all model internal"""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(cls, data: Dict[str, Any], except_key: List[str]) -> Self:
        field_names = (f.name for f in fields(cls))
        filtered = {k: v for k, v in data.items() if k in field_names}

        for k in except_key:
            if k in filtered.keys():
                del filtered[k]
            continue

        return cls(**filtered)
