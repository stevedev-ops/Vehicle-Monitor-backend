from rest_framework import serializers
from .models import (
    Owner, Vehicle, StationPump, FuelEntry, FuelEntryStatus,
    VehicleService, ServiceReminder, OwnerDocument, VehicleDocument,
    VehicleExpense, Notification
)

class FuelEntryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelEntryStatus
        fields = '__all__'

class FuelEntrySerializer(serializers.ModelSerializer):
    status = FuelEntryStatusSerializer(read_only=True)
    vehicle_registration = serializers.CharField(source='vehicle.registration_number', read_only=True)

    class Meta:
        model = FuelEntry
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    fuel_entries_count = serializers.IntegerField(source='fuel_entries.count', read_only=True)
    services_count = serializers.IntegerField(source='services.count', read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'

class StationPumpSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationPump
        fields = '__all__'

class VehicleServiceSerializer(serializers.ModelSerializer):
    vehicle_registration = serializers.CharField(source='vehicle.registration_number', read_only=True)

    class Meta:
        model = VehicleService
        fields = '__all__'

class ServiceReminderSerializer(serializers.ModelSerializer):
    vehicle_registration = serializers.CharField(source='vehicle.registration_number', read_only=True)

    class Meta:
        model = ServiceReminder
        fields = '__all__'

class OwnerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerDocument
        fields = '__all__'

class VehicleDocumentSerializer(serializers.ModelSerializer):
    vehicle_registration = serializers.CharField(source='vehicle.registration_number', read_only=True)

    class Meta:
        model = VehicleDocument
        fields = '__all__'

class VehicleExpenseSerializer(serializers.ModelSerializer):
    vehicle_registration = serializers.CharField(source='vehicle.registration_number', read_only=True)

    class Meta:
        model = VehicleExpense
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class OwnerSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True)
    documents = OwnerDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = '__all__'

