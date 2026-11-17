from __future__ import annotations

from django.http import HttpRequest

from apps.identity.models import PLAYER_COLORS


def current_player(request: HttpRequest) -> dict:
    player = getattr(request, "player", None)
    return {
        "current_player": player,
        "player_colors": PLAYER_COLORS,
    }