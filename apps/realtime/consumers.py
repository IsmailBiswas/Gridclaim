"""WebSocket consumer that fans out board HTML fragments to browsers."""

from __future__ import annotations

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from apps.identity.services import player_directory


class BoardConsumer(AsyncWebsocketConsumer):
    group_name = settings.BOARD_CHANNEL_GROUP

    async def connect(self):
        self.player_id = await self._resolve_player_id()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data='<div id="ws-status" hx-swap-oob="true" class="pill pill-live">Live</div>')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Client → server messages are unused; claims go through HTTP + HTMX.
        return None

    async def board_cell_update(self, event):
        # Skip echoing the claimer's own cell mutation — HTMX already swapped it.
        if event.get("actor_id") and event["actor_id"] == self.player_id:
            return
        await self.send(text_data=event["html"])

    async def board_stats_refresh(self, event):
        await self.send(text_data=event["html"])

    @database_sync_to_async
    def _resolve_player_id(self) -> str:
        query = parse_qs(self.scope.get("query_string", b"").decode())
        explicit = (query.get("player_id") or [None])[0]
        if explicit:
            return explicit

        session = self.scope.get("session")
        if session and session.session_key:
            info = player_directory.get_or_create_for_session(session.session_key)
            return str(info.id)
        return ""