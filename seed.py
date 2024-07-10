from config import app, db
from models import Patient, Doctor, Appointment, MedicalRecord, Bill, Service, BillService
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def create_patients(n=50):
    patients = []
    for _ in range(n):
        patient = Patient(
            first_name=fake.first_name(),
            username=fake.user_name(),
            password_hash=fake.password(),
            last_name=fake.last_name(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=90),
            contact_number=fake.phone_number(),
            email=fake.email()
        )
        patients.append(patient)
    return patients

def create_doctors(n=10):
    specializations = ['Cardiology', 'Neurology', 'Pediatrics', 'Orthopedics', 'Dermatology']
    doctors = []
    for _ in range(n):
        doctor = Doctor(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            specialization=random.choice(specializations)
        )
        doctors.append(doctor)
    return doctors

def create_appointments(patients, doctors, n=100):
    appointments = []
    for _ in range(n):
        appointment = Appointment(
            patient=random.choice(patients),
            doctor=random.choice(doctors),
            appointment_date=fake.date_time_between(start_date='now', end_date='+30d'),
            reason=fake.sentence(),
            status=random.choice(['Scheduled', 'Completed', 'Cancelled'])
        )
        appointments.append(appointment)
    return appointments

def create_medical_records(patients, n=200):
    records = []
    for _ in range(n):
        record = MedicalRecord(
            patient=random.choice(patients),
            record_date=fake.date_time_between(start_date='-1y', end_date='now'),
            diagnosis=fake.sentence(),
            treatment=fake.paragraph()
        )
        records.append(record)
    return records

def create_services(n=20):
    service_types = ['Consultation', 'X-Ray', 'Blood Test', 'MRI', 'CT Scan', 'Ultrasound', 
                     'Vaccination', 'Physical Therapy', 'Surgery', 'Dental Cleaning']
    services = []
    for _ in range(n):
        service = Service(
            name=random.choice(service_types) + ' - ' + fake.word().capitalize(),
            description=fake.sentence(),
            price=round(random.uniform(50, 1000), 2)
        )
        services.append(service)
    return services

def create_bills_and_bill_services(patients, services, n=150):
    bills = []
    bill_services = []
    for _ in range(n):
        bill = Bill(
            patient=random.choice(patients),
            bill_date=fake.date_time_between(start_date='-6m', end_date='now'),
            amount=0,  # We'll calculate this based on services
            status=random.choice(['Paid', 'Unpaid', 'Partially Paid'])
        )
        bills.append(bill)
        
        # Create a set of used service indices for this bill
        used_services = set()
        
        # Add 1-5 unique services to each bill
        for _ in range(random.randint(1, min(5, len(services)))):
            # Keep trying to find an unused service
            while True:
                service_index = random.randint(0, len(services) - 1)
                if service_index not in used_services:
                    used_services.add(service_index)
                    break
            
            service = services[service_index]
            quantity = random.randint(1, 3)
            bill_service = BillService(
                bill=bill,
                service=service,
                quantity=quantity,
                notes=fake.sentence()
            )
            bill.amount += service.price * quantity
            bill_services.append(bill_service)
    
    return bills, bill_services

with app.app_context():
    db.drop_all()
    db.create_all()
    
    print("Starting to seed database...")
    
    # Create and add patients
    patients = create_patients()
    db.session.add_all(patients)
    print(f"Added {len(patients)} patients")
    
    # Create and add doctors
    doctors = create_doctors()
    db.session.add_all(doctors)
    print(f"Added {len(doctors)} doctors")
    
    # Create and add appointments
    appointments = create_appointments(patients, doctors)
    db.session.add_all(appointments)
    print(f"Added {len(appointments)} appointments")
    
    # Create and add medical records
    medical_records = create_medical_records(patients)
    db.session.add_all(medical_records)
    print(f"Added {len(medical_records)} medical records")
    
    # Create and add services
    services = create_services()
    db.session.add_all(services)
    db.session.commit()  # Commit to ensure services have IDs
    print(f"Added {len(services)} services")
    
    # Create and add bills and bill services
    bills, bill_services = create_bills_and_bill_services(patients, services)
    db.session.add_all(bills)
    db.session.add_all(bill_services)
    print(f"Added {len(bills)} bills and {len(bill_services)} bill services")
    
    db.session.commit()
    print("Database seeding completed!")