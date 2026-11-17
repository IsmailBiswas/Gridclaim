"""Board domain contracts.

Claim rules, cell snapshots, and event payloads live here so realtime
and UI layers can stay decoupled from ORM models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID


class ClaimOutcome(str, Enum):
    CLAIMED = "claimed"
    RECLAIMED = "reclaimed"
    ALREADY_YOURS = "already_yours"
    COOLDOWN = "cooldown"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class CellSnapshot:
    id: int
    x: int
    y: int
    owner_id: UUID | None
    owner_name: str | None
    owner_color: str | None
    version: int
    claimed_at: datetime | None


@dataclass(frozen=True, slots=True)
class ClaimResult:
    outcome: ClaimOutcome
    cell: CellSnapshot | None
    message: str
    cooldown_remaining: float = 0.0


@dataclass(frozen=True, slots=True)
class LeaderboardEntry:
    player_id: UUID
    display_name: str
    color: str
    cell_count: int


@dataclass(frozen=True, slots=True)
class BoardStats:
    total_cells: int
    claimed_cells: int
    open_cells: int
    unique_owners: int
    width: int
    height: int


class ClaimService(Protocol):
    def claim(self, cell_id: int, player_id: UUID) -> ClaimResult: ...

    def get_cell(self, cell_id: int) -> CellSnapshot | None: ...

    def list_cells(self) -> list[CellSnapshot]: ...

    def leaderboard(self, limit: int = 8) -> list[LeaderboardEntry]: ...

    def stats(self) -> BoardStats: ...


class BoardEventPublisher(Protocol):
    """Realtime fan-out for board mutations (implemented in apps.realtime)."""

    def publish_cell_update(self, cell: CellSnapshot, actor_id: UUID) -> None: ...

    def publish_stats_refresh(self) -> None: ...