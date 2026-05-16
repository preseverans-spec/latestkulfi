from django.http import JsonResponse
from django.core.management import call_command
from django.contrib.auth.models import User
from inventory.models import Product
import io
import sys

def force_migrate_data(request):
    out = io.StringIO()
    err = io.StringIO()
    try:
        # Aggressively delete the default user that causes conflicts
        User.objects.all().delete()
        
        call_command('loaddata', 'data_dump.json', stdout=out, stderr=err)
        product_count = Product.objects.count()
        user_count = User.objects.count()
        return JsonResponse({
            'status': 'success',
            'stdout': out.getvalue(),
            'stderr': err.getvalue(),
            'product_count': product_count,
            'user_count': user_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'stdout': out.getvalue(),
            'stderr': err.getvalue()
        })
