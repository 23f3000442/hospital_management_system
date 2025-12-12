from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from sqlalchemy import or_
import csv
import io
import os

from models import db, User, Patient, Doctor, Appointment, Treatment, Department, DoctorAvailability
from celery.result import AsyncResult
from celery_tasks import celery, export_patient_treatments

patient_bp = Blueprint('patient', __name__)

def require_patient(fn):
    """Decorator to require patient role"""
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        user = User.query.get(user_id)
        if not user or user.role != 'patient':
            return jsonify({'error': 'Patient access required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)

@patient_bp.route('/dashboard', methods=['GET'])
@require_patient
def get_dashboard():
    """Get patient dashboard"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        # Get all departments
        departments = Department.query.all()
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'Booked'
        ).order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        ).all()
        
        # Get past appointments
        past_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            or_(
                Appointment.appointment_date < date.today(),
                Appointment.status.in_(['Completed', 'Cancelled'])
            )
        ).order_by(
            Appointment.appointment_date.desc()
        ).limit(5).all()
        
        return jsonify({
            'patient_info': {
                'id': patient.id,
                'name': patient.name,
                'phone': patient.phone,
                'email': patient.user.email
            },
            'departments': [{
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'doctors_count': len(dept.doctors)
            } for dept in departments],
            'upcoming_appointments': [{
                'id': apt.id,
                'doctor_id': apt.doctor_id,
                'doctor_name': apt.doctor.name,
                'specialization': apt.doctor.specialization,
                'appointment_date': apt.appointment_date.isoformat(),
                'appointment_time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'reason': apt.reason
            } for apt in upcoming_appointments],
            'past_appointments': [{
                'id': apt.id,
                'doctor_name': apt.doctor.name,
                'specialization': apt.doctor.specialization,
                'appointment_date': apt.appointment_date.isoformat(),
                'appointment_time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status
            } for apt in past_appointments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/profile', methods=['GET'])
@require_patient
def get_profile():
    """Get patient profile"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        return jsonify({
            'id': patient.id,
            'name': patient.name,
            'phone': patient.phone,
            'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            'gender': patient.gender,
            'address': patient.address,
            'blood_group': patient.blood_group,
            'email': patient.user.email
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/profile', methods=['PUT'])
@require_patient
def update_profile():
    """Update patient profile"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            patient.name = data['name']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'date_of_birth' in data:
            patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        if 'gender' in data:
            patient.gender = data['gender']
        if 'address' in data:
            patient.address = data['address']
        if 'blood_group' in data:
            patient.blood_group = data['blood_group']
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/doctors', methods=['GET'])
@require_patient
def get_doctors():
    """Get list of doctors with availability"""
    try:
        specialization = request.args.get('specialization')
        department_id = request.args.get('department_id')
        search = request.args.get('search')
        
        query = Doctor.query.join(Doctor.user).filter(Doctor.user.has(is_active=True))
        
        if specialization:
            query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
        
        if department_id:
            query = query.filter(Doctor.department_id == department_id)
        
        if search:
            query = query.filter(
                or_(
                    Doctor.name.ilike(f'%{search}%'),
                    Doctor.specialization.ilike(f'%{search}%')
                )
            )
        
        doctors = query.all()
        
        # Get availability for next 7 days
        today = date.today()
        next_week = today + timedelta(days=7)
        
        result = []
        for doc in doctors:
            availability = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doc.id,
                DoctorAvailability.date >= today,
                DoctorAvailability.date <= next_week,
                DoctorAvailability.is_available == True
            ).order_by(DoctorAvailability.date).all()
            
            result.append({
                'id': doc.id,
                'name': doc.name,
                'specialization': doc.specialization,
                'department_id': doc.department_id,
                'department_name': doc.department.name,
                'phone': doc.phone,
                'experience_years': doc.experience_years,
                'qualification': doc.qualification,
                'availability': [{
                    'date': avail.date.isoformat(),
                    'start_time': avail.start_time.strftime('%H:%M'),
                    'end_time': avail.end_time.strftime('%H:%M')
                } for avail in availability]
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments', methods=['POST'])
@require_patient
def book_appointment():
    """Book a new appointment"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not all(field in data for field in ['doctor_id', 'appointment_date', 'appointment_time']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        doctor_id = data['doctor_id']
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        # Check if appointment date is in the future
        if appointment_date < date.today():
            return jsonify({'error': 'Cannot book appointments in the past'}), 400
        
        # Check if doctor is available at that time
        existing_appointment = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == 'Booked'
        ).first()
        
        if existing_appointment:
            return jsonify({'error': 'Doctor is not available at this time'}), 400
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=data.get('reason'),
            status='Booked'
        )
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': {
                'id': appointment.id,
                'doctor_id': appointment.doctor_id,
                'appointment_date': appointment.appointment_date.isoformat(),
                'appointment_time': appointment.appointment_time.strftime('%H:%M'),
                'status': appointment.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@require_patient
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        if appointment.patient_id != patient.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if appointment.status != 'Booked':
            return jsonify({'error': 'Can only reschedule booked appointments'}), 400
        
        data = request.get_json()
        
        if 'appointment_date' in data:
            new_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            if new_date < date.today():
                return jsonify({'error': 'Cannot reschedule to a past date'}), 400
            appointment.appointment_date = new_date
        
        if 'appointment_time' in data:
            new_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
            
            # Check for conflicts
            conflict = Appointment.query.filter(
                Appointment.id != appointment_id,
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.appointment_date == appointment.appointment_date,
                Appointment.appointment_time == new_time,
                Appointment.status == 'Booked'
            ).first()
            
            if conflict:
                return jsonify({'error': 'Doctor is not available at this time'}), 400
            
            appointment.appointment_time = new_time
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Appointment rescheduled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@require_patient
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        if appointment.patient_id != patient.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        appointment.status = 'Cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/treatment-history', methods=['GET'])
@require_patient
def get_treatment_history():
    """Get patient's treatment history"""
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        # Get all completed appointments with treatments
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).all()
        
        history = []
        for apt in appointments:
            if apt.treatment:
                history.append({
                    'appointment_id': apt.id,
                    'doctor_name': apt.doctor.name,
                    'specialization': apt.doctor.specialization,
                    'appointment_date': apt.appointment_date.isoformat(),
                    'appointment_time': apt.appointment_time.strftime('%H:%M'),
                    'diagnosis': apt.treatment.diagnosis,
                    'prescription': apt.treatment.prescription,
                    'notes': apt.treatment.notes,
                    'next_visit': apt.treatment.next_visit.isoformat() if apt.treatment.next_visit else None
                })
        
        return jsonify(history), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/export-treatments', methods=['GET'])
@require_patient
def export_treatments():
    """Export treatment history as CSV"""
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        # Get all completed appointments with treatments
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Patient ID', 'Patient Name', 'Doctor Name', 'Appointment Date',
            'Diagnosis', 'Treatment', 'Next Visit Suggested'
        ])
        
        # Write data
        for apt in appointments:
            if apt.treatment:
                writer.writerow([
                    patient.id,
                    patient.name,
                    apt.doctor.name,
                    apt.appointment_date.isoformat(),
                    apt.treatment.diagnosis or '',
                    apt.treatment.prescription or '',
                    apt.treatment.next_visit.isoformat() if apt.treatment.next_visit else ''
                ])
        
        # Create response
        output.seek(0)
        return jsonify({
            'message': 'Export ready',
            'csv_data': output.getvalue()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/export-treatments/async', methods=['POST'])
@require_patient
def export_treatments_async():
    """Trigger async CSV export via Celery and return task id."""
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        task = export_patient_treatments.delay(patient.id)
        return jsonify({'task_id': task.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/export-treatments/status/<task_id>', methods=['GET'])
@require_patient
def export_treatments_status(task_id):
    """Check status of async CSV export; return CSV when ready."""
    try:
        result = AsyncResult(task_id, app=celery)
        response = {
            'task_id': task_id,
            'state': result.state,
            'ready': result.ready()
        }
        if result.ready():
            # CSV string result
            response['csv_data'] = result.get() or ''
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/departments', methods=['GET'])
@require_patient
def get_departments():
    """Get all departments"""
    try:
        cache_key = 'departments:all'
        cached = current_app.redis.get(cache_key)
        if cached:
            import json as _json
            return jsonify(_json.loads(cached)), 200
        departments = Department.query.all()
        payload = [{
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'doctors_count': len([d for d in dept.doctors if d.user.is_active])
        } for dept in departments]
        import json as _json
        current_app.redis.setex(cache_key, current_app.config['CACHE_DEFAULT_TIMEOUT'], _json.dumps(payload))
        return jsonify(payload), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

