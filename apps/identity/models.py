from __future__ import annotations

import random
import uuid

from django.db import models
from django.utils import timezone

PLAYER_COLORS = [
    "#111111",
    "#2A2A2A",
    "#3D3D3D",
    "#525252",
    "#666666",
    "#7A7A7A",
    "#8F8F8F",
    "#A3A3A3",
    "#B8B8B8",
    "#1A1A1A",
]

NAME_ADJECTIVES = [
    "Swift",
    "Quiet",
    "Bright",
    "Bold",
    "Calm",
    "Keen",
    "Lucky",
    "Nimble",
    "Cosmic",
    "Pixel",
]

NAME_NOUNS = [
    "Fox",
    "Otter",
    "Hawk",
    "Lynx",
    "Nova",
    "Comet",
    "Maple",
    "Cedar",
    "Spark",
    "Drift",
]


def generate_display_name() -> str:
    return f"{random.choice(NAME_ADJECTIVES)} {random.choice(NAME_NOUNS)}"


def generate_color() -> str:
    return random.choice(PLAYER_COLORS)


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=64, unique=True, db_index=True)
    display_name = models.CharField(max_length=40, default=generate_display_name)
    color = models.CharField(max_length=7, default=generate_color)
    last_claim_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.color})"