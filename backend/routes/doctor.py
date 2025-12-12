from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta, time

from models import db, User, Doctor, Patient, Appointment, Treatment, DoctorAvailability

doctor_bp = Blueprint('doctor', __name__)

def require_doctor(fn):
    """Decorator to require doctor role"""
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        user = User.query.get(user_id)
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Doctor access required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)

@doctor_bp.route('/dashboard', methods=['GET'])
@require_doctor
def get_dashboard():
    """Get doctor dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        # Upcoming appointments (next 7 days)
        today = date.today()
        next_week = today + timedelta(days=7)
        
        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= today,
            Appointment.appointment_date <= next_week,
            Appointment.status == 'Booked'
        ).order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        ).all()
        
        # Today's appointments
        today_appointments = [apt for apt in upcoming_appointments if apt.appointment_date == today]
        
        # Unique patients
        unique_patients = db.session.query(Patient).join(Appointment).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().count()
        
        # Total completed appointments
        completed_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == 'Completed'
        ).count()
        
        return jsonify({
            'doctor_info': {
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization,
                'department': doctor.department.name
            },
            'stats': {
                'upcoming_appointments': len(upcoming_appointments),
                'today_appointments': len(today_appointments),
                'total_patients': unique_patients,
                'completed_appointments': completed_appointments
            },
            'upcoming_appointments': [{
                'id': apt.id,
                'patient_id': apt.patient_id,
                'patient_name': apt.patient.name,
                'patient_phone': apt.patient.phone,
                'appointment_date': apt.appointment_date.isoformat(),
                'appointment_time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'reason': apt.reason
            } for apt in upcoming_appointments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments', methods=['GET'])
@require_doctor
def get_appointments():
    """Get doctor's appointments"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        status = request.args.get('status')
        
        query = Appointment.query.filter(Appointment.doctor_id == doctor.id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).all()
        
        return jsonify([{
            'id': apt.id,
            'patient_id': apt.patient_id,
            'patient_name': apt.patient.name,
            'patient_phone': apt.patient.phone,
            'appointment_date': apt.appointment_date.isoformat(),
            'appointment_time': apt.appointment_time.strftime('%H:%M'),
            'status': apt.status,
            'reason': apt.reason,
            'has_treatment': apt.treatment is not None
        } for apt in appointments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/complete', methods=['PUT'])
@require_doctor
def complete_appointment(appointment_id):
    """Mark appointment as completed and add treatment"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        if appointment.doctor_id != doctor.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update appointment status
        appointment.status = 'Completed'
        appointment.updated_at = datetime.utcnow()
        
        # Create or update treatment
        if appointment.treatment:
            treatment = appointment.treatment
            treatment.diagnosis = data.get('diagnosis', treatment.diagnosis)
            treatment.prescription = data.get('prescription', treatment.prescription)
            treatment.notes = data.get('notes', treatment.notes)
            if 'next_visit' in data and data['next_visit']:
                treatment.next_visit = datetime.strptime(data['next_visit'], '%Y-%m-%d').date()
            treatment.updated_at = datetime.utcnow()
        else:
            treatment = Treatment(
                appointment_id=appointment.id,
                diagnosis=data.get('diagnosis'),
                prescription=data.get('prescription'),
                notes=data.get('notes'),
                next_visit=datetime.strptime(data['next_visit'], '%Y-%m-%d').date() if data.get('next_visit') else None
            )
            db.session.add(treatment)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment completed successfully',
            'appointment': {
                'id': appointment.id,
                'status': appointment.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
@require_doctor
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        if appointment.doctor_id != doctor.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        appointment.status = 'Cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/patients', methods=['GET'])
@require_doctor
def get_patients():
    """Get list of patients assigned to doctor"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        # Get unique patients who have appointments with this doctor
        patients = db.session.query(Patient).join(Appointment).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()
        
        return jsonify([{
            'id': pat.id,
            'name': pat.name,
            'phone': pat.phone,
            'date_of_birth': pat.date_of_birth.isoformat() if pat.date_of_birth else None,
            'gender': pat.gender,
            'blood_group': pat.blood_group,
            'email': pat.user.email,
            'total_appointments': Appointment.query.filter(
                Appointment.patient_id == pat.id,
                Appointment.doctor_id == doctor.id
            ).count()
        } for pat in patients]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@require_doctor
def get_patient_history(patient_id):
    """Get patient's treatment history"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get all appointments with treatments for this patient with this doctor
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.doctor_id == doctor.id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).all()
        
        history = []
        for apt in appointments:
            if apt.treatment:
                history.append({
                    'appointment_id': apt.id,
                    'appointment_date': apt.appointment_date.isoformat(),
                    'appointment_time': apt.appointment_time.strftime('%H:%M'),
                    'diagnosis': apt.treatment.diagnosis,
                    'prescription': apt.treatment.prescription,
                    'notes': apt.treatment.notes,
                    'next_visit': apt.treatment.next_visit.isoformat() if apt.treatment.next_visit else None
                })
        
        return jsonify({
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'phone': patient.phone,
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                'gender': patient.gender,
                'blood_group': patient.blood_group
            },
            'history': history
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/availability', methods=['GET'])
@require_doctor
def get_availability():
    """Get doctor's availability"""
    try:
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        # Get availability for next 7 days
        today = date.today()
        next_week = today + timedelta(days=7)
        
        availability = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= next_week
        ).order_by(DoctorAvailability.date).all()
        
        return jsonify([{
            'id': avail.id,
            'date': avail.date.isoformat(),
            'start_time': avail.start_time.strftime('%H:%M'),
            'end_time': avail.end_time.strftime('%H:%M'),
            'is_available': avail.is_available
        } for avail in availability]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/availability', methods=['POST'])
@require_doctor
def set_availability():
    """Set doctor's availability for next 7 days"""
    try:
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not all(field in data for field in ['date', 'start_time', 'end_time']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        avail_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        # Check if availability already exists
        existing = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date == avail_date
        ).first()
        
        if existing:
            existing.start_time = start_time
            existing.end_time = end_time
            existing.is_available = data.get('is_available', True)
        else:
            availability = DoctorAvailability(
                doctor_id=doctor.id,
                date=avail_date,
                start_time=start_time,
                end_time=end_time,
                is_available=data.get('is_available', True)
            )
            db.session.add(availability)
        
        db.session.commit()
        
        return jsonify({'message': 'Availability set successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

