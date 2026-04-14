import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a default superuser from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL", "")
        password = os.getenv("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping default superuser creation: ADMIN_USERNAME/ADMIN_PASSWORD not set."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed = False
        if email and user.email != email:
            user.email = email
            changed = True

        if not user.is_staff:
            user.is_staff = True
            changed = True

        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        user.set_password(password)
        changed = True

        if changed:
            user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created default admin user '{username}'."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated default admin user '{username}'."))
