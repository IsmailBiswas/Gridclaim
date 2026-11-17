"""Channels-backed implementation of BoardEventPublisher."""

from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.template.loader import render_to_string

from apps.board.interfaces import CellSnapshot


class ChannelBoardPublisher:
    """Broadcast HTML fragments so HTMX clients can OOB-swap updates."""

    group_name = settings.BOARD_CHANNEL_GROUP

    def publish_cell_update(self, cell: CellSnapshot, actor_id) -> None:
        cell_html = render_to_string(
            "board/partials/cell.html",
            {
                "cell": cell,
                "current_player_id": "",
                "highlight": "1",
                "oob": "1",
            },
        )
        toast_html = render_to_string(
            "board/partials/toast_oob.html",
            {
                "message": f"{cell.owner_name} claimed ({cell.x}, {cell.y})",
                "color": cell.owner_color,
                "actor_id": str(actor_id),
            },
        )
        self._send(
            {
                "type": "board.cell_update",
                "cell_id": cell.id,
                "actor_id": str(actor_id),
                "html": cell_html + toast_html,
            }
        )

    def publish_stats_refresh(self) -> None:
        from apps.board.services import BoardClaimService

        service = BoardClaimService()
        sidebar_html = render_to_string(
            "board/partials/sidebar_oob.html",
            {
                "stats": service.stats(),
                "leaderboard": service.leaderboard(),
                "cooldown_seconds": settings.CLAIM_COOLDOWN_SECONDS,
            },
        )
        self._send(
            {
                "type": "board.stats_refresh",
                "html": sidebar_html,
            }
        )

    def _send(self, payload: dict) -> None:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(self.group_name, payload)


channel_board_publisher = ChannelBoardPublisher()