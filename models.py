from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

from config import db, bcrypt


class Patient(db.Model, SerializerMixin):
    __tablename__ = 'patients'

    

    serialize_rules = ('-appointments.patient', '-medical_records.patient', '-bills.patient')

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    appointments = db.relationship('Appointment', back_populates='patient')
    medical_records = db.relationship('MedicalRecord', back_populates='patient')
    bills = db.relationship('Bill', back_populates='patient')

    doctors = association_proxy('appointments', 'doctor')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Doctor(db.Model, SerializerMixin):
    __tablename__ = 'doctors'

    serialize_rules = ('-patients', )
    

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(100))
    
    appointments = db.relationship('Appointment', back_populates='doctor')

    patients = association_proxy('appointments', 'patient')

class Appointment(db.Model, SerializerMixin):
    __tablename__ = 'appointments'

    serialize_rules = ('-patient', '-doctor')
    serialize_only = ('id', 'patient_id', 'doctor_id', 'appointment_date', 'reason', 'status')

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Scheduled')
    
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')

class MedicalRecord(db.Model, SerializerMixin):
    __tablename__ = 'medical_records'

    serialize_rules = ('-patient.medical_records',)

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    diagnosis = db.Column(db.String(200))
    treatment = db.Column(db.String(500))
    
    patient = db.relationship('Patient', back_populates='medical_records')

class Bill(db.Model, SerializerMixin):
    __tablename__ = 'bills'

    serialize_rules = ('-patient.bills', '-bill_services', '-patient.appointments')

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Unpaid')
    
    patient = db.relationship('Patient', back_populates='bills')
    bill_services = db.relationship('BillService', back_populates='bill', cascade='all, delete-orphan')
    
    services = association_proxy('bill_services', 'service')

class Service(db.Model, SerializerMixin):
    __tablename__ = 'services'

    serialize_rules = ('-bill_services.service',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    
    bill_services = db.relationship('BillService', back_populates='service')
    
    bills = association_proxy('bill_services', 'bill')

class BillService(db.Model, SerializerMixin):
    __tablename__ = 'bill_services'

    serialize_rules = ('-bill.bill_services', '-service.bill_services', '-bill.patient.appointments', '-bill.patient.medical_records')

    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    notes = db.Column(db.String(200))  
    
    bill = db.relationship('Bill', back_populates='bill_services')
    service = db.relationship('Service', back_populates='bill_services')