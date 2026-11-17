from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import (
    Owner, Vehicle, StationPump, FuelEntry, FuelEntryStatus,
    VehicleService, ServiceReminder, OwnerDocument, VehicleDocument,
    VehicleExpense, Notification
)
from .serializers import (
    OwnerSerializer, VehicleSerializer, StationPumpSerializer,
    FuelEntrySerializer, FuelEntryStatusSerializer, VehicleServiceSerializer,
    ServiceReminderSerializer, OwnerDocumentSerializer, VehicleDocumentSerializer,
    VehicleExpenseSerializer, NotificationSerializer
)

class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class StationPumpViewSet(viewsets.ModelViewSet):
    queryset = StationPump.objects.all()
    serializer_class = StationPumpSerializer

class FuelEntryViewSet(viewsets.ModelViewSet):
    queryset = FuelEntry.objects.all()
    serializer_class = FuelEntrySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        return qs

    def perform_create(self, serializer):
        entry = serializer.save()
        # Create default status if not existing
        if not hasattr(entry, 'status'):
            FuelEntryStatus.objects.create(fuel_entry=entry)

class VehicleServiceViewSet(viewsets.ModelViewSet):
    queryset = VehicleService.objects.all()
    serializer_class = VehicleServiceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        return qs

class ServiceReminderViewSet(viewsets.ModelViewSet):
    queryset = ServiceReminder.objects.all()
    serializer_class = ServiceReminderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        return qs

class OwnerDocumentViewSet(viewsets.ModelViewSet):
    queryset = OwnerDocument.objects.all()
    serializer_class = OwnerDocumentSerializer

class VehicleDocumentViewSet(viewsets.ModelViewSet):
    queryset = VehicleDocument.objects.all()
    serializer_class = VehicleDocumentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        return qs

class VehicleExpenseViewSet(viewsets.ModelViewSet):
    queryset = VehicleExpense.objects.all()
    serializer_class = VehicleExpenseSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        return qs

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

@api_view(['POST'])
def sync_offline_data(request):
    """
    Offline sync endpoint: Receives batch records from IndexedDB and upserts them.
    """
    data = request.data
    results = {'synced': 0, 'errors': []}

    try:
        with transaction.atomic():
            # Sync Vehicles
            for v_item in data.get('vehicles', []):
                v_id = v_item.get('id')
                reg = v_item.get('registration_number') or v_item.get('registrationNumber')
                if not reg:
                    continue
                owner_obj = Owner.objects.first()
                if not owner_obj:
                    owner_obj = Owner.objects.create(name="Steve", email="steve@example.com")
                Vehicle.objects.update_or_create(
                    id=v_id,
                    defaults={
                        'owner': owner_obj,
                        'registration_number': reg,
                        'make': v_item.get('make', 'Toyota'),
                        'model': v_item.get('model', 'Axio'),
                        'year': v_item.get('year', 2016),
                        'fuel_type': v_item.get('fuel_type', 'petrol'),
                        'engine_capacity': v_item.get('engine_capacity') or v_item.get('engineCapacity', 1500),
                        'current_odometer': v_item.get('current_odometer') or v_item.get('currentOdometer', 0),
                        'fuel_benchmark': v_item.get('fuel_benchmark') or v_item.get('fuelBenchmark', 17.5),
                        'is_active': v_item.get('is_active', True)
                    }
                )

            # Sync Fuel Entries
            for item in data.get('fuel_entries', []):
                entry_id = item.get('id')
                vehicle_id = item.get('vehicle_id')
                if not vehicle_id:
                    continue
                
                # Check if vehicle exists; if not, look up or link to first available
                veh = Vehicle.objects.filter(id=vehicle_id).first()
                if not veh:
                    veh = Vehicle.objects.filter(registration_number="KCX 123A").first() or Vehicle.objects.first()
                if not veh:
                    owner_obj = Owner.objects.first() or Owner.objects.create(name="Steve")
                    veh = Vehicle.objects.create(id=vehicle_id, owner=owner_obj, registration_number="KCX 123A", make="Toyota", model="Axio")
                
                entry, created = FuelEntry.objects.update_or_create(
                    id=entry_id,
                    defaults={
                        'vehicle': veh,
                        'date': item.get('date'),
                        'litres': item.get('litres'),
                        'price_per_litre': item.get('price_per_litre'),
                        'total_cost': item.get('total_cost'),
                        'trip_km': item.get('trip_km'),
                        'current_odometer': item.get('current_odometer'),
                        'cluster_kml': item.get('cluster_kml'),
                        'station_name_text': item.get('station_name_text', ''),
                        'pump_number_text': item.get('pump_number_text', ''),
                        'payment_method': item.get('payment_method', 'card'),
                        'notes': item.get('notes', ''),
                    }
                )
                
                # Upsert status
                st = item.get('status', {})
                FuelEntryStatus.objects.update_or_create(
                    fuel_entry=entry,
                    defaults={
                        'receipt_attached': st.get('receipt_attached', False),
                        'payment_verified': st.get('payment_verified', True),
                        'pump_info_recorded': st.get('pump_info_recorded', True),
                        'vehicle_readings_recorded': st.get('vehicle_readings_recorded', True),
                        'pending_review': st.get('pending_review', False),
                        'review_reason': st.get('review_reason', ''),
                        'overall_status': st.get('overall_status', 'complete'),
                    }
                )
                results['synced'] += 1

            # Sync Services
            for item in data.get('services', []):
                vid = item.get('vehicle_id')
                veh = Vehicle.objects.filter(id=vid).first() or Vehicle.objects.first()
                if not veh:
                    continue
                VehicleService.objects.update_or_create(
                    id=item.get('id'),
                    defaults={
                        'vehicle': veh,
                        'service_date': item.get('service_date'),
                        'odometer_reading': item.get('odometer_reading'),
                        'service_type': item.get('service_type', 'Routine Service'),
                        'category': item.get('category', 'engine_oil'),
                        'garage': item.get('garage', ''),
                        'parts_replaced': item.get('parts_replaced', ''),
                        'labour_cost': item.get('labour_cost', 0),
                        'parts_cost': item.get('parts_cost', 0),
                        'total_cost': item.get('total_cost', 0),
                        'notes': item.get('notes', ''),
                    }
                )
                results['synced'] += 1

            # Sync Expenses
            for item in data.get('expenses', []):
                vid = item.get('vehicle_id')
                veh = Vehicle.objects.filter(id=vid).first() or Vehicle.objects.first()
                if not veh:
                    continue
                VehicleExpense.objects.update_or_create(
                    id=item.get('id'),
                    defaults={
                        'vehicle': veh,
                        'expense_date': item.get('expense_date'),
                        'category': item.get('category', 'parking'),
                        'amount': item.get('amount', 0),
                        'notes': item.get('notes', ''),
                    }
                )
                results['synced'] += 1

        return Response({'status': 'success', 'data': results})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
