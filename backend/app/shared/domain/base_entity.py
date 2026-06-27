"""
Entité de base du domaine.
Les entités du domaine sont des objets Python purs — aucune dépendance ORM ou framework.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BaseEntity:
    """
    Classe de base pour toutes les entités métier.
    Fournit un identifiant UUID et les timestamps.
    Les entités sont identifiées par leur id, pas par leurs attributs.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = field(default=None)
    updated_at: datetime | None = field(default=None)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
