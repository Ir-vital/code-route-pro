"""
Interface générique de repository (port).
Chaque module définit ses propres interfaces qui héritent ou s'inspirent de celle-ci.
Le domaine dépend de ces interfaces — jamais de SQLAlchemy directement.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Interface abstraite de repository.
    Contrat minimal : get_by_id, save, delete.
    Les repositories concrets dans infrastructure/ implémentent ce contrat.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        ...

    @abstractmethod
    async def save(self, entity: T) -> T:
        ...

    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> None:
        ...
