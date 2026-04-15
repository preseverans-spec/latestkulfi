from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import (
    AuthViewSet,
    InventoryViewSet,
    MobileTokenObtainPairView,
    MobileTokenRefreshView,
    OperationsExpenseViewSet,
    ProductViewSet,
    SalesViewSet,
    SyncViewSet,
)

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('products', ProductViewSet, basename='product')
router.register('inventory/movements', InventoryViewSet, basename='inventory-movement')
router.register('sales', SalesViewSet, basename='sale')
router.register('expenses', OperationsExpenseViewSet, basename='expense')
router.register('sync', SyncViewSet, basename='sync')

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('auth/login/', MobileTokenObtainPairView.as_view(), name='mobile-login'),
    path('auth/refresh/', MobileTokenRefreshView.as_view(), name='mobile-refresh'),
    path('', include(router.urls)),
]
