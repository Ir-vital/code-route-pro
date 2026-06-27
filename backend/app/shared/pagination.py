"""
Pagination générique réutilisable par tous les modules.
Enveloppe de réponse : { items, total, page, page_size, pages }
"""

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Paramètres de pagination en entrée (query params)."""

    page: int = Field(default=1, ge=1, description="Numéro de page (commence à 1)")
    page_size: int = Field(default=20, ge=1, le=100, description="Nombre d'éléments par page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Enveloppe de réponse paginée standard."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        params: PaginationParams,
    ) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=math.ceil(total / params.page_size) if params.page_size > 0 else 0,
        )
