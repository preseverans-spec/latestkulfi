from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand

from inventory.models import Product


class Command(BaseCommand):
    help = "Load inventory fixture once when database is empty."

    def handle(self, *args, **options):
        fixture_path = Path.cwd() / "inventory_data.json"

        if not fixture_path.exists():
            self.stdout.write(
                self.style.WARNING("Skipping bootstrap: inventory_data.json not found.")
            )
            return

        if Product.objects.exists():
            self.stdout.write(
                self.style.WARNING("Skipping bootstrap: data already exists in database.")
            )
            return

        call_command("loaddata", str(fixture_path), verbosity=1)
        self.stdout.write(self.style.SUCCESS("Initial inventory data imported."))
