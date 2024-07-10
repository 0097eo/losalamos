from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import Patient, Doctor, Appointment, MedicalRecord, Bill, Service, BillService
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from datetime import timedelta, datetime

class PatientRegistration(Resource):
    def post(self):
        data = request.get_json()
        
        if Patient.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400

        new_patient = Patient(
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            contact_number=data['contact_number'],
            email=data['email']
        )
        new_patient.set_password(data['password'])

        db.session.add(new_patient)
        try:
            db.session.commit()
            return {'message': 'Patient registered successfully'}, 201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'An error occurred while registering the patient'}, 500

api.add_resource(PatientRegistration, '/register')

class PatientLogin(Resource):
    def post(self):
        data = request.get_json()
        patient = Patient.query.filter_by(username=data['username']).first()
        
        if patient and patient.check_password(data['password']):
            access_token = create_access_token(identity=patient.id, expires_delta=timedelta(hours=1))
            refresh_token = create_refresh_token(identity=patient.id)
            return {'access_token': access_token, "refresh_token":refresh_token}, 200
        return {'message': 'Invalid username or password'}, 401
    
    @jwt_required
    def get(self):
        data = request.get_json()
        patient = Patient.query.filter_by(username=data['username']).first()
        token = create_access_token(identity=patient.id)
        return {"access_token": token}

api.add_resource(PatientLogin, '/login')

class CurrentPatient(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        patient = Patient.query.get(current_user_id)
        if patient:
            return patient.to_dict(), 200
        return {'message': 'Patient not found'}, 404

api.add_resource(CurrentPatient, '/me')

class Patients(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        patients = [patient.to_dict() for patient in Patient.query.all()]
        return make_response(jsonify(patients), 200)
    
api.add_resource(Patients, '/patients')

class PatientsById(Resource):
    def get(self, id):
        patient = Patient.query.filter(Patient.id == id).first()
        if patient:
            patient_dict = patient.to_dict()
            return make_response(jsonify(patient_dict), 200)
        else:
            return make_response(jsonify({"error": "Patient not found"}), 404)

api.add_resource(PatientsById, '/patients/<int:id>')
class Doctors(Resource):
    def get(self):
        doctors = [doctor.to_dict() for doctor in Doctor.query.all()]
        return make_response(jsonify(doctors), 200)
    
api.add_resource(Doctors, '/doctors')

class DoctorByID(Resource):
    def get(self, id):
        doctor = Doctor.query.filter(Doctor.id == id).first()
        if doctor:
            doctor_dict = doctor.to_dict()
            return make_response(jsonify(doctor_dict), 200)
        else:
            return make_response(jsonify({"error": "Doctor not found"}), 404)

api.add_resource(DoctorByID, '/doctors/<int:id>')
    
class Appointments(Resource):
    def get(self):
        appointments = [appointment.to_dict() for appointment in Appointment.query.all()]
        return make_response(jsonify(appointments), 200)
    
api.add_resource(Appointments, '/appointments')

class Bills(Resource):
    def get(self):
        bills = [bill.to_dict() for bill in Bill.query.all()]
        return make_response(jsonify(bills), 200)
      
api.add_resource(Bills, '/bills')
    

class BillsByID(Resource):
    def get(self, id):
        bill = Bill.query.filter(Bill.id == id).first()
        if bill:
            bill_dict = bill.to_dict()
            return make_response(jsonify(bill_dict), 200)
        
    
api.add_resource(BillsByID, '/bills/<int:id>')


class BillServices(Resource):
    def get(self):
        bill_services = [bill_service.to_dict() for bill_service in BillService.query.all()]
        return make_response(jsonify(bill_services), 200)
    
api.add_resource(BillServices, '/billservices')
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)