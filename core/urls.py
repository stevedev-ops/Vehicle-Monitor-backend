from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OwnerViewSet, VehicleViewSet, StationPumpViewSet, FuelEntryViewSet,
    VehicleServiceViewSet, ServiceReminderViewSet, OwnerDocumentViewSet,
    VehicleDocumentViewSet, VehicleExpenseViewSet, NotificationViewSet,
    sync_offline_data
)

router = DefaultRouter()
router.register('owners', OwnerViewSet)
router.register('vehicles', VehicleViewSet)
router.register('stations', StationPumpViewSet)
router.register('fuel-entries', FuelEntryViewSet)
router.register('services', VehicleServiceViewSet)
router.register('reminders', ServiceReminderViewSet)
router.register('owner-documents', OwnerDocumentViewSet)
router.register('vehicle-documents', VehicleDocumentViewSet)
router.register('expenses', VehicleExpenseViewSet)
router.register('notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sync/', sync_offline_data, name='offline-sync'),
]

