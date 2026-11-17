from __future__ import annotations

import json

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from apps.board.interfaces import ClaimOutcome
from apps.board.services import get_claim_service


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    service = get_claim_service()
    cells = service.list_cells()
    return render(
        request,
        "board/home.html",
        {
            "cells": cells,
            "stats": service.stats(),
            "leaderboard": service.leaderboard(),
            "board_width": settings.BOARD_WIDTH,
            "board_height": settings.BOARD_HEIGHT,
            "cooldown_seconds": settings.CLAIM_COOLDOWN_SECONDS,
        },
    )


@require_POST
def claim_cell(request: HttpRequest, cell_id: int) -> HttpResponse:
    service = get_claim_service()
    result = service.claim(cell_id, request.player.id)

    status = 200
    if result.outcome == ClaimOutcome.NOT_FOUND:
        status = 404
    elif result.outcome == ClaimOutcome.COOLDOWN:
        status = 429
    elif result.outcome == ClaimOutcome.CONFLICT:
        status = 409

    response = render(
        request,
        "board/partials/claim_response.html",
        {
            "result": result,
            "stats": service.stats(),
            "leaderboard": service.leaderboard(),
            "current_player_id": str(request.player.id),
            "cooldown_seconds": settings.CLAIM_COOLDOWN_SECONDS,
        },
        status=status,
    )
    if result.outcome in {ClaimOutcome.CLAIMED, ClaimOutcome.RECLAIMED}:
        response["X-Claim-Cooldown"] = str(settings.CLAIM_COOLDOWN_SECONDS)
        response["HX-Trigger"] = json.dumps(
            {"boardClaimed": {"cooldown": settings.CLAIM_COOLDOWN_SECONDS}}
        )
    elif result.outcome == ClaimOutcome.COOLDOWN:
        response["X-Cooldown-Remaining"] = f"{result.cooldown_remaining:.3f}"
        response["HX-Trigger"] = json.dumps(
            {"boardCooldown": {"remaining": result.cooldown_remaining}}
        )
    return response


@require_GET
def cell_partial(request: HttpRequest, cell_id: int) -> HttpResponse:
    service = get_claim_service()
    cell = service.get_cell(cell_id)
    if cell is None:
        return HttpResponseBadRequest("Unknown cell")
    return render(
        request,
        "board/partials/cell.html",
        {
            "cell": cell,
            "current_player_id": str(request.player.id),
            "highlight": "1" if request.GET.get("highlight") == "1" else "",
        },
    )


@require_GET
def sidebar_partial(request: HttpRequest) -> HttpResponse:
    service = get_claim_service()
    return render(
        request,
        "board/partials/sidebar.html",
        {
            "stats": service.stats(),
            "leaderboard": service.leaderboard(),
            "cooldown_seconds": settings.CLAIM_COOLDOWN_SECONDS,
        },
    )