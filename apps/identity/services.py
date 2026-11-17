"""Concrete PlayerDirectory implementation."""

from __future__ import annotations

from uuid import UUID

from django.db import transaction

from apps.identity.interfaces import PlayerInfo
from apps.identity.models import PLAYER_COLORS, Player, generate_display_name


class DjangoPlayerDirectory:
    """Persists players in Postgres and exposes PlayerInfo snapshots."""

    def get_or_create_for_session(self, session_key: str) -> PlayerInfo:
        if not session_key:
            raise ValueError("session_key is required")

        player, _ = Player.objects.get_or_create(
            session_key=session_key,
            defaults={
                "display_name": generate_display_name(),
            },
        )
        return self._to_info(player)

    def get_by_id(self, player_id: UUID) -> PlayerInfo | None:
        player = Player.objects.filter(pk=player_id).first()
        return self._to_info(player) if player else None

    @transaction.atomic
    def update_profile(
        self,
        player_id: UUID,
        *,
        display_name: str | None = None,
        color: str | None = None,
    ) -> PlayerInfo:
        player = Player.objects.select_for_update().get(pk=player_id)
        if display_name is not None:
            cleaned = display_name.strip()[:40]
            if cleaned:
                player.display_name = cleaned
        if color is not None and color in PLAYER_COLORS:
            player.color = color
        player.save(update_fields=["display_name", "color", "updated_at"])
        return self._to_info(player)

    @staticmethod
    def _to_info(player: Player) -> PlayerInfo:
        return PlayerInfo(
            id=player.id,
            display_name=player.display_name,
            color=player.color,
            session_key=player.session_key,
        )


# Default singleton used by the rest of the project.
player_directory = DjangoPlayerDirectory()