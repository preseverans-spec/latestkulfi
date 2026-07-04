import os
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand

from inventory.models import Product


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class Command(BaseCommand):
    help = "Load a fixture once when explicitly enabled and the database is empty."

    def handle(self, *args, **options):
        seed_enabled = _as_bool(os.getenv("SEED_DATA_ON_DEPLOY"), default=False)
        fixture_name = os.getenv("SEED_FIXTURE_PATH", "render_seed.json").strip() or "render_seed.json"
        fixture_path = Path.cwd() / fixture_name

        if not seed_enabled:
            self.stdout.write(
                self.style.WARNING("Skipping seed import: SEED_DATA_ON_DEPLOY is not enabled.")
            )
            return

        if not fixture_path.exists():
            self.stdout.write(
                self.style.WARNING(f"Skipping seed import: fixture not found at {fixture_path}.")
            )
            return

        if Product.objects.exists():
            self.stdout.write(
                self.style.WARNING("Skipping seed import: target database already contains product data.")
            )
            return

        call_command("loaddata", str(fixture_path), verbosity=1)
        self.stdout.write(self.style.SUCCESS(f"Seed data imported from {fixture_name}."))
