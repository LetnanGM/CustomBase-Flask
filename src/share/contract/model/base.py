from typing import Dict, List, Any, Self
from dataclasses import asdict, fields
from abc import ABC


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
