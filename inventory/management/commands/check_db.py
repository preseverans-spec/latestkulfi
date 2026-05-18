from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import sys

class Command(BaseCommand):
    help = 'Check if the database is available and responding.'

    def handle(self, *args, **options):
        self.stdout.write('Checking database connection...')
        db_conn = connections['default']
        try:
            db_conn.cursor()
        except OperationalError:
            self.stdout.write(self.style.ERROR('Database unavailable!'))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS('Database connection established.'))
