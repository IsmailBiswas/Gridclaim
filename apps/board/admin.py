from django.contrib import admin

from apps.board.models import Cell


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("id", "x", "y", "owner", "version", "claimed_at")
    list_filter = ("owner",)
    search_fields = ("x", "y", "owner__display_name")
    readonly_fields = ("version", "claimed_at", "updated_at")