"""
URL configuration for kulfi project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('api/v1/', include('api.urls')),
]

# Serve media files (user uploads)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files (logos, CSS, JS) - needed for both DEBUG and production (Railway with WhiteNoise)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
