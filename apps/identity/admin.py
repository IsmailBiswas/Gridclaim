from django.contrib import admin

from apps.identity.models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "color", "session_key", "last_claim_at", "created_at")
    search_fields = ("display_name", "session_key")
    readonly_fields = ("id", "session_key", "created_at", "updated_at")