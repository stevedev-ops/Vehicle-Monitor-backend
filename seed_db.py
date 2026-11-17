import os
import django
from datetime import datetime, date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petrol_backend.settings')
django.setup()

from core.models import (
    Owner, Vehicle, StationPump, FuelEntry, FuelEntryStatus,
    VehicleService, ServiceReminder, OwnerDocument, VehicleDocument,
    VehicleExpense
)

def run_seed():
    print("Clearing old seed data...")
    FuelEntryStatus.objects.all().delete()
    FuelEntry.objects.all().delete()
    VehicleExpense.objects.all().delete()
    VehicleService.objects.all().delete()
    ServiceReminder.objects.all().delete()
    VehicleDocument.objects.all().delete()
    OwnerDocument.objects.all().delete()
    Vehicle.objects.all().delete()
    StationPump.objects.all().delete()
    Owner.objects.all().delete()

    print("Seeding Owner...")
    owner = Owner.objects.create(
        id="owner-steve-01",
        name="Steve",
        email="steve@example.com",
        phone="+254700000000"
    )

    print("Seeding Owner Document (Driving Licence)...")
    OwnerDocument.objects.create(
        id="doc-owner-dl-01",
        owner=owner,
        document_type="driving_licence",
        document_number="DL-KE-982341",
        issue_date=date(2023, 5, 10),
        expiry_date=date(2028, 5, 10),
        notes="Class B & C endorsement"
    )

    print("Seeding Stations...")
    st_rubis = StationPump.objects.create(id="st-rubis-west", brand="Rubis", station_name="Rubis Westlands", branch="Westlands", pump_number="P3", accuracy_index=99.2)
    st_total = StationPump.objects.create(id="st-total-kimathi", brand="TotalEnergies", station_name="TotalEnergies Kimathi", branch="CBD", pump_number="P1", accuracy_index=98.5)
    st_shell = StationPump.objects.create(id="st-shell-kilimani", brand="Shell", station_name="Shell Kilimani", branch="Kilimani", pump_number="P4", accuracy_index=97.8)
    st_hass  = StationPump.objects.create(id="st-hass-ind", brand="Hass", station_name="Hass Enterprise", branch="Industrial Area", pump_number="P2", accuracy_index=96.1)

    print("Seeding Vehicles...")
    v_axio = Vehicle.objects.create(
        id="veh-axio-kcx123a",
        owner=owner,
        registration_number="KCX 123A",
        make="Toyota",
        model="Axio",
        year=2016,
        fuel_type="petrol",
        engine_capacity=1500,
        current_odometer=158891.0,
        fuel_benchmark=17.50,
        is_active=True
    )

    v_fielder = Vehicle.objects.create(
        id="veh-fielder-kda456b",
        owner=owner,
        registration_number="KDA 456B",
        make="Toyota",
        model="Fielder",
        year=2018,
        fuel_type="petrol",
        engine_capacity=1800,
        current_odometer=82450.0,
        fuel_benchmark=15.80,
        is_active=False
    )

    v_demio = Vehicle.objects.create(
        id="veh-demio-kcb789c",
        owner=owner,
        registration_number="KCB 789C",
        make="Mazda",
        model="Demio",
        year=2014,
        fuel_type="petrol",
        engine_capacity=1300,
        current_odometer=114200.0,
        fuel_benchmark=18.20,
        is_active=False
    )

    print("Seeding Real KCX Historical Fuel Entries (from spreadsheet)...")
    raw_entries = [
        {"litres": 15.17, "price": 226.90, "trip": 253, "cluster": 16.5, "days_ago": 2, "station": st_rubis, "pump": "P3"},
        {"litres": 32.01, "price": 226.90, "trip": 506, "cluster": 15.5, "days_ago": 7, "station": st_total, "pump": "P1"},
        {"litres": 13.53, "price": 224.09, "trip": 177, "cluster": 14.1, "days_ago": 12, "station": st_shell, "pump": "P4"},
        {"litres": 31.44, "price": 224.14, "trip": 519, "cluster": 16.7, "days_ago": 18, "station": st_rubis, "pump": "P3"},
        {"litres": 26.76, "price": 226.87, "trip": 430, "cluster": 18.2, "days_ago": 24, "station": st_total, "pump": "P2"},
        {"litres": 28.62, "price": 226.87, "trip": 513, "cluster": 18.4, "days_ago": 30, "station": st_rubis, "pump": "P3"},
        {"litres": 28.70, "price": 213.97, "trip": 480, "cluster": 17.2, "days_ago": 38, "station": st_shell, "pump": "P4"},
        {"litres": 28.57, "price": 213.97, "trip": 517, "cluster": 18.6, "days_ago": 45, "station": st_total, "pump": "P1"},
        {"litres": 34.27, "price": 213.77, "trip": 624, "cluster": 18.9, "days_ago": 52, "station": st_rubis, "pump": "P3"},
        {"litres": 26.44, "price": 213.99, "trip": 521, "cluster": 20.0, "days_ago": 60, "station": st_shell, "pump": "P2"},
        {"litres": 39.27, "price": 214.67, "trip": 706, "cluster": 18.2, "days_ago": 68, "station": st_total, "pump": "P1"},
        {"litres": 18.30, "price": 208.96, "trip": 321, "cluster": 18.7, "days_ago": 75, "station": st_hass, "pump": "P2"},
        {"litres": 25.28, "price": 214.00, "trip": 515, "cluster": 21.1, "days_ago": 82, "station": st_rubis, "pump": "P3"},
    ]

    base_date = datetime.now()
    for item in raw_entries:
        entry_date = base_date - timedelta(days=item['days_ago'])
        total_cost = round(item['litres'] * item['price'], 2)
        fe = FuelEntry(
            vehicle=v_axio,
            date=entry_date,
            litres=item['litres'],
            price_per_litre=item['price'],
            total_cost=total_cost,
            trip_km=item['trip'],
            cluster_kml=item['cluster'],
            station=item['station'],
            station_name_text=item['station'].station_name,
            pump_number_text=item['pump'],
            payment_method='card',
            notes="Full tank brim-to-brim"
        )
        fe.save()
        FuelEntryStatus.objects.create(
            fuel_entry=fe,
            receipt_attached=True,
            payment_verified=True,
            pump_info_recorded=True,
            vehicle_readings_recorded=True,
            pending_review=False,
            overall_status='complete'
        )

    print("Seeding Vehicle Documents...")
    VehicleDocument.objects.create(
        vehicle=v_axio,
        document_type="insurance",
        provider="APA Insurance",
        document_number="POL-APA-2026-9921",
        start_date=date(2026, 1, 1),
        expiry_date=date(2026, 12, 31),
        notes="Comprehensive private motor insurance"
    )

    VehicleDocument.objects.create(
        vehicle=v_axio,
        document_type="inspection",
        provider="NTSA Motor Inspection",
        document_number="CERT-INSP-2026-4412",
        start_date=date(2026, 3, 15),
        expiry_date=date(2027, 3, 14),
        notes="Annual safety & roadworthiness inspection"
    )

    print("Seeding Maintenance & Reminders...")
    VehicleService.objects.create(
        vehicle=v_axio,
        service_date=date(2026, 9, 15),
        odometer_reading=155000.0,
        service_type="Routine Service",
        category="engine_oil",
        garage="AutoCare Westlands",
        parts_replaced="Toyota 0W-20 Synthetic Oil (4L), OEM Oil Filter",
        labour_cost=1500.0,
        parts_cost=6500.0,
        total_cost=8000.0,
        notes="Next service due at 160,000 km or 6 months"
    )

    ServiceReminder.objects.create(
        vehicle=v_axio,
        title="Engine Oil & Filter Service",
        category="engine_oil",
        interval_km=5000.0,
        interval_months=6,
        last_service_odometer=155000.0,
        last_service_date=date(2026, 9, 15),
        due_odometer=160000.0,
        due_date=date(2027, 3, 15),
        status="active"
    )

    print("Seeding Non-Fuel Expenses...")
    VehicleExpense.objects.create(
        vehicle=v_axio,
        expense_date=date(2026, 11, 10),
        category="tolls",
        amount=360.0,
        notes="Nairobi Expressway Westlands to JKIA"
    )
    VehicleExpense.objects.create(
        vehicle=v_axio,
        expense_date=date(2026, 11, 5),
        category="cleaning",
        amount=500.0,
        notes="Full exterior wash & interior vacuum"
    )
    VehicleExpense.objects.create(
        vehicle=v_axio,
        expense_date=date(2026, 11, 2),
        category="parking",
        amount=300.0,
        notes="Nairobi County CBD daily automated parking"
    )

    print("Seed complete! 3 Vehicles, 13 Fuel logs, Documents, Services and Expenses ready.")

if __name__ == '__main__':
    run_seed()

