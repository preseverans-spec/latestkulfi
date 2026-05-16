import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from inventory.models import Product


class Command(BaseCommand):
    help = "Import the committed SQLite database into the current database once."

    def handle(self, *args, **options):
        if Product.objects.exists():
            self.stdout.write(
                self.style.WARNING("Skipping SQLite import: data already exists in the target database.")
            )
            return

        source_db = Path(settings.BASE_DIR) / "db.sqlite3"
        if not source_db.exists():
            self.stdout.write(
                self.style.WARNING(f"Source SQLite database not found: {source_db}. Skipping import.")
            )
            return

        app_labels = []
        for app_config in apps.get_app_configs():
            if list(app_config.get_models()):
                app_labels.append(app_config.label)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            dump_path = Path(temp_file.name)

        try:
            source_env = os.environ.copy()
            source_env["DATABASE_URL"] = f"sqlite:///{source_db.resolve().as_posix()}"

            subprocess.run(
                [
                    sys.executable,
                    str(settings.BASE_DIR / "manage.py"),
                    "dumpdata",
                    "--all",
                    "--indent",
                    "2",
                    "--output",
                    str(dump_path),
                    *app_labels,
                ],
                check=True,
                cwd=str(settings.BASE_DIR),
                env=source_env,
            )

            call_command("flush", interactive=False)
            call_command("loaddata", str(dump_path), verbosity=1)
        finally:
            dump_path.unlink(missing_ok=True)

        if not Product.objects.exists():
            raise CommandError("SQLite import finished, but no product data was loaded.")

        self.stdout.write(self.style.SUCCESS("SQLite database imported into the current database."))