from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.utils.functional import SimpleLazyObject

from apps.identity.services import player_directory


def _resolve_player(request: HttpRequest):
    if not request.session.session_key:
        request.session.create()
    return player_directory.get_or_create_for_session(request.session.session_key)


class EnsurePlayerMiddleware:
    """Attach request.player for every request with a session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.player = SimpleLazyObject(lambda: _resolve_player(request))
        return self.get_response(request)