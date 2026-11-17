from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.identity.models import PLAYER_COLORS
from apps.identity.services import player_directory


@require_http_methods(["GET", "POST"])
def profile(request: HttpRequest) -> HttpResponse:
    player = request.player
    error = ""

    if request.method == "POST":
        name = request.POST.get("display_name", "")
        color = request.POST.get("color", "")
        if not name.strip():
            error = "Name cannot be empty."
        elif color and color not in PLAYER_COLORS:
            error = "Pick a color from the palette."
        else:
            player_directory.update_profile(
                player.id,
                display_name=name,
                color=color or None,
            )
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "identity/partials/profile_form.html",
                    {
                        "current_player": player_directory.get_by_id(player.id),
                        "player_colors": PLAYER_COLORS,
                        "saved": True,
                    },
                )
            return redirect("board:home")

    return render(
        request,
        "identity/partials/profile_form.html",
        {
            "current_player": player_directory.get_by_id(player.id),
            "player_colors": PLAYER_COLORS,
            "error": error,
            "saved": False,
        },
    )