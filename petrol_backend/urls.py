from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
import os

def api_root(request):
    return JsonResponse({
        "status": "online",
        "service": "Vehicle Monitor & Fleet Backend API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "vehicles": "/api/vehicles/",
            "fuel_entries": "/api/fuel-entries/",
            "services": "/api/services/",
            "reminders": "/api/reminders/",
            "expenses": "/api/expenses/",
            "vehicle_documents": "/api/vehicle-documents/",
            "owner_documents": "/api/owner-documents/"
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

# Serve static frontend files during development if frontend directory is present
if settings.DEBUG and getattr(settings, 'STATICFILES_DIRS', None):
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
