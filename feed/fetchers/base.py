from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from feed.models import Item


class BaseFetcher(ABC):
    name: str = "base"

    def __init__(self, cfg: dict):
        self.cfg = cfg

    @abstractmethod
    def fetch(self) -> Iterable[Item]:
        ...
