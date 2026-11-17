from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Cell(models.Model):
    """A single tile on the shared board.

    `version` acts as an optimistic concurrency token so simultaneous
    claims cannot silently overwrite each other.
    """

    x = models.PositiveSmallIntegerField()
    y = models.PositiveSmallIntegerField()
    owner = models.ForeignKey(
        "identity.Player",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cells",
    )
    version = models.PositiveIntegerField(default=0)
    claimed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["x", "y"], name="uniq_cell_coordinate"),
        ]
        ordering = ["y", "x"]
        indexes = [
            models.Index(fields=["owner"]),
        ]

    def __str__(self) -> str:
        owner = self.owner.display_name if self.owner_id else "empty"
        return f"({self.x},{self.y}) → {owner}"

    @classmethod
    def expected_total(cls) -> int:
        return settings.BOARD_WIDTH * settings.BOARD_HEIGHT

    def assign(self, player) -> None:
        self.owner = player
        self.claimed_at = timezone.now()
        self.version += 1