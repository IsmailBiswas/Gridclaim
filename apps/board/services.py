"""Claim orchestration with row locking + cooldown rules."""

from __future__ import annotations

from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from apps.board.interfaces import (
    BoardEventPublisher,
    BoardStats,
    CellSnapshot,
    ClaimOutcome,
    ClaimResult,
    LeaderboardEntry,
)
from apps.board.models import Cell
from apps.identity.models import Player


class NullBoardEventPublisher:
    def publish_cell_update(self, cell: CellSnapshot, actor_id: UUID) -> None:
        return None

    def publish_stats_refresh(self) -> None:
        return None


class BoardClaimService:
    """Transactional claim engine used by HTTP views and future APIs."""

    def __init__(self, publisher: BoardEventPublisher | None = None) -> None:
        self.publisher = publisher or NullBoardEventPublisher()

    def claim(self, cell_id: int, player_id: UUID) -> ClaimResult:
        with transaction.atomic():
            player = Player.objects.select_for_update().filter(pk=player_id).first()
            if player is None:
                return ClaimResult(
                    outcome=ClaimOutcome.NOT_FOUND,
                    cell=None,
                    message="Player not found.",
                )

            remaining = self._cooldown_remaining(player)
            if remaining > 0:
                cell = Cell.objects.select_related("owner").filter(pk=cell_id).first()
                return ClaimResult(
                    outcome=ClaimOutcome.COOLDOWN,
                    cell=self._snapshot(cell) if cell else None,
                    message=f"Claim on cooldown — wait {remaining:.1f}s before the next click.",
                    cooldown_remaining=remaining,
                )

            # Lock only the cell row. select_related(owner) is a LEFT OUTER JOIN
            # (nullable FK); Postgres rejects FOR UPDATE on that nullable side.
            cell = (
                Cell.objects.select_for_update(of=("self",))
                .select_related("owner")
                .filter(pk=cell_id)
                .first()
            )
            if cell is None:
                return ClaimResult(
                    outcome=ClaimOutcome.NOT_FOUND,
                    cell=None,
                    message="That block does not exist.",
                )

            if cell.owner_id == player.id:
                return ClaimResult(
                    outcome=ClaimOutcome.ALREADY_YOURS,
                    cell=self._snapshot(cell),
                    message="You already own this block.",
                )

            previous_owner_id = cell.owner_id
            cell.assign(player)
            cell.save(update_fields=["owner", "claimed_at", "version", "updated_at"])
            player.last_claim_at = timezone.now()
            player.save(update_fields=["last_claim_at", "updated_at"])

            snapshot = self._snapshot(cell)
            outcome = (
                ClaimOutcome.RECLAIMED
                if previous_owner_id is not None
                else ClaimOutcome.CLAIMED
            )
            message = (
                "Captured from another player!"
                if outcome == ClaimOutcome.RECLAIMED
                else "Block claimed."
            )

        self.publisher.publish_cell_update(snapshot, player_id)
        self.publisher.publish_stats_refresh()
        return ClaimResult(outcome=outcome, cell=snapshot, message=message)

    def get_cell(self, cell_id: int) -> CellSnapshot | None:
        cell = Cell.objects.select_related("owner").filter(pk=cell_id).first()
        return self._snapshot(cell) if cell else None

    def list_cells(self) -> list[CellSnapshot]:
        cells = Cell.objects.select_related("owner").all()
        return [self._snapshot(cell) for cell in cells]

    def leaderboard(self, limit: int = 8) -> list[LeaderboardEntry]:
        rows = (
            Player.objects.annotate(cell_count=Count("cells"))
            .filter(cell_count__gt=0)
            .order_by("-cell_count", "display_name")[:limit]
        )
        return [
            LeaderboardEntry(
                player_id=row.id,
                display_name=row.display_name,
                color=row.color,
                cell_count=row.cell_count,
            )
            for row in rows
        ]

    def stats(self) -> BoardStats:
        total = Cell.objects.count()
        claimed = Cell.objects.filter(owner__isnull=False).count()
        unique_owners = (
            Cell.objects.filter(owner__isnull=False)
            .values("owner_id")
            .distinct()
            .count()
        )
        return BoardStats(
            total_cells=total,
            claimed_cells=claimed,
            open_cells=total - claimed,
            unique_owners=unique_owners,
            width=settings.BOARD_WIDTH,
            height=settings.BOARD_HEIGHT,
        )

    def ensure_board(self) -> int:
        """Idempotently create the full grid. Returns newly created count."""
        width = settings.BOARD_WIDTH
        height = settings.BOARD_HEIGHT
        existing = {(c.x, c.y) for c in Cell.objects.only("x", "y")}
        missing = [
            Cell(x=x, y=y)
            for y in range(height)
            for x in range(width)
            if (x, y) not in existing
        ]
        if missing:
            Cell.objects.bulk_create(missing, batch_size=500)
        return len(missing)

    @staticmethod
    def _cooldown_remaining(player: Player) -> float:
        if not player.last_claim_at:
            return 0.0
        elapsed = (timezone.now() - player.last_claim_at).total_seconds()
        remaining = settings.CLAIM_COOLDOWN_SECONDS - elapsed
        return max(0.0, remaining)

    @staticmethod
    def _snapshot(cell: Cell) -> CellSnapshot:
        owner = cell.owner
        return CellSnapshot(
            id=cell.id,
            x=cell.x,
            y=cell.y,
            owner_id=owner.id if owner else None,
            owner_name=owner.display_name if owner else None,
            owner_color=owner.color if owner else None,
            version=cell.version,
            claimed_at=cell.claimed_at,
        )


def get_claim_service() -> BoardClaimService:
    """Factory that wires the realtime publisher when available."""
    from apps.realtime.publisher import channel_board_publisher

    return BoardClaimService(publisher=channel_board_publisher)