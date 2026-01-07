from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Args:
    """Mini-Namespace compatible avec les cmd_* qui attendent args.xxx"""

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
