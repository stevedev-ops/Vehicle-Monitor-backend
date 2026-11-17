import uuid
from django.db import models

def gen_id():
    return str(uuid.uuid4())

class Owner(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ]

    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='vehicles')
    registration_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=60)
    model = models.CharField(max_length=60)
    year = models.IntegerField(default=2015)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    engine_capacity = models.IntegerField(blank=True, null=True, help_text="in cc, e.g. 1500")
    current_odometer = models.DecimalField(max_digits=10, decimal_places=1, default=0.0)
    fuel_benchmark = models.DecimalField(max_digits=5, decimal_places=2, default=17.50, help_text="Expected KM/L baseline")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['registration_number']

    def __str__(self):
        return f"{self.make} {self.model} ({self.registration_number})"

class StationPump(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    brand = models.CharField(max_length=80, help_text="Shell, TotalEnergies, Rubis, Ola, Hass, etc.")
    station_name = models.CharField(max_length=120)
    branch = models.CharField(max_length=100, blank=True, default='')
    pump_number = models.CharField(max_length=30, blank=True, null=True)
    accuracy_index = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)

    class Meta:
        ordering = ['brand', 'station_name']

    def __str__(self):
        return f"{self.brand} - {self.station_name}"

class FuelEntry(models.Model):
    PAYMENT_CHOICES = [
        ('card', 'Card Payment'),
        ('mpesa', 'M-Pesa / Mobile Money'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_entries')
    date = models.DateTimeField()
    litres = models.DecimalField(max_digits=7, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=7, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    trip_km = models.DecimalField(max_digits=8, decimal_places=1, help_text="Trip meter distance since last fill")
    current_odometer = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    cluster_kml = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Car instrument cluster indicated KM/L")
    calculated_kml = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Trip KM / Litres")
    accuracy_percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="(Calculated / Cluster) * 100")
    cost_per_km = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, help_text="Total Cost / Trip KM")
    station = models.ForeignKey(StationPump, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries')
    station_name_text = models.CharField(max_length=120, blank=True, default='')
    pump_number_text = models.CharField(max_length=30, blank=True, default='')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='card')
    notes = models.TextField(blank=True, default='')
    receipt_data = models.TextField(blank=True, default='', help_text="Base64 or photo URL")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if self.litres and self.litres > 0 and self.trip_km and self.trip_km > 0:
            self.calculated_kml = round(float(self.trip_km) / float(self.litres), 2)
            self.cost_per_km = round(float(self.total_cost) / float(self.trip_km), 2)
            if self.cluster_kml and self.cluster_kml > 0:
                self.accuracy_percentage = round((float(self.calculated_kml) / float(self.cluster_kml)) * 100, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.date.strftime('%Y-%m-%d')} ({self.litres}L)"

class FuelEntryStatus(models.Model):
    OVERALL_CHOICES = [
        ('complete', 'Complete'),
        ('incomplete', 'Incomplete'),
        ('needs_review', 'Needs Review'),
    ]

    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    fuel_entry = models.OneToOneField(FuelEntry, on_delete=models.CASCADE, related_name='status')
    receipt_attached = models.BooleanField(default=False)
    payment_verified = models.BooleanField(default=False)
    pump_info_recorded = models.BooleanField(default=True)
    vehicle_readings_recorded = models.BooleanField(default=True)
    pending_review = models.BooleanField(default=False)
    review_reason = models.TextField(blank=True, default='')
    overall_status = models.CharField(max_length=30, choices=OVERALL_CHOICES, default='complete')

    def evaluate_status(self):
        reasons = []
        entry = self.fuel_entry

        expected_cost = float(entry.litres) * float(entry.price_per_litre)
        if abs(expected_cost - float(entry.total_cost)) > 10.0:
            reasons.append(f"Payment discrepancy: entered Ksh {entry.total_cost} vs expected {expected_cost:.2f}")

        benchmark = float(entry.vehicle.fuel_benchmark)
        if entry.calculated_kml:
            kml = float(entry.calculated_kml)
            if kml < (benchmark * 0.5) or kml > (benchmark * 1.5):
                reasons.append(f"Consumption outlier: {kml} KM/L deviates significantly from benchmark {benchmark} KM/L")

        if reasons:
            self.pending_review = True
            self.review_reason = "; ".join(reasons)
            self.overall_status = 'needs_review'
        elif not self.pump_info_recorded or not self.vehicle_readings_recorded:
            self.overall_status = 'incomplete'
        else:
            self.overall_status = 'complete'

    def save(self, *args, **kwargs):
        if not self.review_reason and hasattr(self, 'fuel_entry'):
            self.evaluate_status()
        super().save(*args, **kwargs)

class VehicleService(models.Model):
    CATEGORY_CHOICES = [
        ('engine_oil', 'Engine Oil & Filter'),
        ('air_filter', 'Air Filter'),
        ('fuel_filter', 'Fuel Filter'),
        ('brake_pads', 'Brake Pads & Discs'),
        ('tyres', 'Tyres & Wheel Alignment'),
        ('battery', 'Battery'),
        ('coolant', 'Coolant System'),
        ('transmission', 'Transmission Fluid (CVT/ATF)'),
        ('spark_plugs', 'Spark Plugs'),
        ('inspection', 'General Inspection & Suspension'),
        ('other', 'Other Repairs'),
    ]

    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='services')
    service_date = models.DateField()
    odometer_reading = models.DecimalField(max_digits=10, decimal_places=1)
    service_type = models.CharField(max_length=100, default='Routine Service')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='engine_oil')
    garage = models.CharField(max_length=150, blank=True, default='')
    parts_replaced = models.TextField(blank=True, default='')
    labour_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    notes = models.TextField(blank=True, default='')
    invoice_data = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-service_date']

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.get_category_display()} ({self.service_date})"

class ServiceReminder(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('due_soon', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
    ]

    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=VehicleService.CATEGORY_CHOICES, default='engine_oil')
    interval_km = models.DecimalField(max_digits=8, decimal_places=1, default=5000.0)
    interval_months = models.IntegerField(default=6)
    last_service_odometer = models.DecimalField(max_digits=10, decimal_places=1, default=0.0)
    last_service_date = models.DateField()
    due_odometer = models.DecimalField(max_digits=10, decimal_places=1)
    due_date = models.DateField()
    is_recurring = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['due_date', 'due_odometer']

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.title} (Due: {self.due_odometer} km / {self.due_date})"

class OwnerDocument(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, default='driving_licence')
    document_number = models.CharField(max_length=80)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField()
    file_data = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.owner.name} - {self.document_type} ({self.document_number})"

class VehicleDocument(models.Model):
    DOC_CHOICES = [
        ('insurance', 'Insurance Certificate & Policy'),
        ('inspection', 'Vehicle Inspection Certificate'),
        ('logbook', 'Logbook / Title Copy'),
        ('permit', 'Commercial / Parking Permit'),
        ('other', 'Other Compliance Document'),
    ]

    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOC_CHOICES, default='insurance')
    provider = models.CharField(max_length=120, blank=True, default='', help_text="e.g. APA, Jubilee, NTSA")
    document_number = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField()
    file_data = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.get_document_type_display()}"

class VehicleExpense(models.Model):
    CATEGORY_CHOICES = [
        ('parking', 'Parking Fees'),
        ('tolls', 'Highway Tolls (e.g. Expressway)'),
        ('cleaning', 'Car Wash & Detailing'),
        ('insurance', 'Insurance Premiums'),
        ('repairs', 'Bodywork & Non-Service Repairs'),
        ('accessories', 'Accessories & Upgrades'),
        ('other', 'Other Operational Expense'),
    ]

    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='expenses')
    expense_date = models.DateField()
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='parking')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, default='')
    receipt_data = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.get_category_display()} (Ksh {self.amount})"

class Notification(models.Model):
    id = models.CharField(primary_key=True, max_length=64, default=gen_id, editable=False)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='notifications')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=40, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"
