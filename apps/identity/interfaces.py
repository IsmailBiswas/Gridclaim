"""Contracts for player identity used by other apps.

Other modules should depend on these protocols / DTOs rather than
reaching into Player model details directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PlayerInfo:
    """Immutable snapshot of a player for cross-app use."""

    id: UUID
    display_name: str
    color: str
    session_key: str

    @property
    def public_label(self) -> str:
        return self.display_name


class PlayerDirectory(Protocol):
    """Lookup / ensure players by session."""

    def get_or_create_for_session(self, session_key: str) -> PlayerInfo: ...

    def get_by_id(self, player_id: UUID) -> PlayerInfo | None: ...

    def update_profile(
        self,
        player_id: UUID,
        *,
        display_name: str | None = None,
        color: str | None = None,
    ) -> PlayerInfo: ...