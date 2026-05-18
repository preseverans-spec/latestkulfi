import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kulfi_config.settings')
django.setup()

from django.contrib.auth.models import User

username = 'audit_admin'
password = 'AuditPassword123!'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, password, 'audit@example.com')
    print(f"Created superuser: {username}")
else:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print(f"Updated superuser: {username}")
