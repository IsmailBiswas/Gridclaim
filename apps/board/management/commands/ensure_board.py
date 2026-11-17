from django.core.management.base import BaseCommand

from apps.board.services import BoardClaimService


class Command(BaseCommand):
    help = "Create missing board cells based on BOARD_WIDTH / BOARD_HEIGHT."

    def handle(self, *args, **options):
        created = BoardClaimService().ensure_board()
        self.stdout.write(self.style.SUCCESS(f"Board ready. Created {created} cells."))