from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

from apps.identity.models import Player


def board_ui(request: HttpRequest) -> dict:
    remaining = 0.0
    player = getattr(request, "player", None)
    if player is not None:
        # Lazy player may be PlayerInfo — load last_claim_at when needed.
        db_player = Player.objects.filter(pk=player.id).only("last_claim_at").first()
        if db_player and db_player.last_claim_at:
            elapsed = (timezone.now() - db_player.last_claim_at).total_seconds()
            remaining = max(0.0, settings.CLAIM_COOLDOWN_SECONDS - elapsed)

    return {
        "cooldown_seconds": settings.CLAIM_COOLDOWN_SECONDS,
        "cooldown_remaining": remaining,
    }