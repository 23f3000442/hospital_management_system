from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import or_, func
import json

from models import db, User, Department, Doctor, Patient, Appointment, Treatment, DoctorAvailability

admin_bp = Blueprint('admin', __name__)

def require_admin(fn):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        try:
            user_id = int(user_id)
        except Exception:
            pass
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return jwt_required()(wrapper)

@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        cache_key = 'admin:dashboard'
        cached = current_app.redis.get(cache_key)
        if cached:
            return jsonify(json.loads(cached)), 200

        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        upcoming_appointments = Appointment.query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'Booked'
        ).count()
        recent_appointments = Appointment.query.order_by(
            Appointment.created_at.desc()
        ).limit(5).all()
        payload = {
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming_appointments,
            'recent_appointments': [{
                'id': apt.id,
                'patient_name': apt.patient.name,
                'doctor_name': apt.doctor.name,
                'date': apt.appointment_date.isoformat(),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status
            } for apt in recent_appointments]
        }
        current_app.redis.setex(cache_key, current_app.config['CACHE_DEFAULT_TIMEOUT'], json.dumps(payload))
        return jsonify(payload), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['GET'])
@require_admin
def get_departments():
    """Get all departments"""
    try:
        cache_key = 'departments:all'
        cached = current_app.redis.get(cache_key)
        if cached:
            return jsonify(json.loads(cached)), 200
        departments = Department.query.all()
        payload = [{
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'doctors_count': len(dept.doctors)
        } for dept in departments]
        current_app.redis.setex(cache_key, current_app.config['CACHE_DEFAULT_TIMEOUT'], json.dumps(payload))
        return jsonify(payload), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors', methods=['GET'])
@require_admin
def get_doctors():
    """Get all doctors"""
    try:
        search = request.args.get('search', '')
        
        query = Doctor.query.join(User).filter(User.is_active == True)
        
        if search:
            query = query.filter(
                or_(
                    Doctor.name.ilike(f'%{search}%'),
                    Doctor.specialization.ilike(f'%{search}%')
                )
            )
        
        doctors = query.all()
        
        return jsonify([{
            'id': doc.id,
            'user_id': doc.user_id,
            'name': doc.name,
            'specialization': doc.specialization,
            'department_id': doc.department_id,
            'department_name': doc.department.name,
            'phone': doc.phone,
            'experience_years': doc.experience_years,
            'qualification': doc.qualification,
            'is_active': doc.user.is_active
        } for doc in doctors]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors', methods=['POST'])
@require_admin
def create_doctor():
    """Create a new doctor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'name', 'specialization', 'department_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if username or email exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role='doctor'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            name=data['name'],
            specialization=data['specialization'],
            department_id=data['department_id'],
            phone=data.get('phone'),
            experience_years=data.get('experience_years'),
            qualification=data.get('qualification')
        )
        db.session.add(doctor)
        db.session.commit()
        # Invalidate cached dashboard/departments
        try:
            current_app.redis.delete('admin:dashboard', 'departments:all')
        except Exception:
            pass
        
        return jsonify({
            'message': 'Doctor created successfully',
            'doctor': {
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@require_admin
def update_doctor(doctor_id):
    """Update doctor details"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            doctor.name = data['name']
        if 'specialization' in data:
            doctor.specialization = data['specialization']
        if 'department_id' in data:
            doctor.department_id = data['department_id']
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'experience_years' in data:
            doctor.experience_years = data['experience_years']
        if 'qualification' in data:
            doctor.qualification = data['qualification']
        
        # Update user email if provided
        if 'email' in data:
            doctor.user.email = data['email']
        
        db.session.commit()
        try:
            current_app.redis.delete('admin:dashboard', 'departments:all')
        except Exception:
            pass
        
        return jsonify({
            'message': 'Doctor updated successfully',
            'doctor': {
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@require_admin
def delete_doctor(doctor_id):
    """Deactivate/blacklist a doctor"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        doctor.user.is_active = False
        db.session.commit()
        try:
            current_app.redis.delete('admin:dashboard', 'departments:all')
        except Exception:
            pass
        
        return jsonify({'message': 'Doctor deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/patients', methods=['GET'])
@require_admin
def get_patients():
    """Get all patients"""
    try:
        search = request.args.get('search', '')
        
        query = Patient.query.join(User).filter(User.is_active == True)
        
        if search:
            query = query.filter(
                or_(
                    Patient.name.ilike(f'%{search}%'),
                    Patient.phone.ilike(f'%{search}%')
                )
            )
        
        patients = query.all()
        
        return jsonify([{
            'id': pat.id,
            'user_id': pat.user_id,
            'name': pat.name,
            'phone': pat.phone,
            'date_of_birth': pat.date_of_birth.isoformat() if pat.date_of_birth else None,
            'gender': pat.gender,
            'address': pat.address,
            'blood_group': pat.blood_group,
            'email': pat.user.email,
            'is_active': pat.user.is_active
        } for pat in patients]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@require_admin
def update_patient(patient_id):
    """Update patient details"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
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
        
        if 'email' in data:
            patient.user.email = data['email']
        
        db.session.commit()
        try:
            current_app.redis.delete('admin:dashboard')
        except Exception:
            pass
        
        return jsonify({'message': 'Patient updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@require_admin
def delete_patient(patient_id):
    """Deactivate/blacklist a patient"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient.user.is_active = False
        db.session.commit()
        try:
            current_app.redis.delete('admin:dashboard')
        except Exception:
            pass
        
        return jsonify({'message': 'Patient deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/appointments', methods=['GET'])
@require_admin
def get_all_appointments():
    """Get all appointments"""
    try:
        status = request.args.get('status')
        
        query = Appointment.query
        
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
            'doctor_id': apt.doctor_id,
            'doctor_name': apt.doctor.name,
            'appointment_date': apt.appointment_date.isoformat(),
            'appointment_time': apt.appointment_time.strftime('%H:%M'),
            'status': apt.status,
            'reason': apt.reason
        } for apt in appointments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search', methods=['GET'])
@require_admin
def search():
    """Search for doctors or patients"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')  # all, doctor, patient
        
        results = {
            'doctors': [],
            'patients': []
        }
        
        if search_type in ['all', 'doctor']:
            doctors = Doctor.query.join(User).filter(
                User.is_active == True,
                or_(
                    Doctor.name.ilike(f'%{query}%'),
                    Doctor.specialization.ilike(f'%{query}%')
                )
            ).limit(10).all()
            
            results['doctors'] = [{
                'id': doc.id,
                'name': doc.name,
                'specialization': doc.specialization,
                'department_name': doc.department.name
            } for doc in doctors]
        
        if search_type in ['all', 'patient']:
            patients = Patient.query.join(User).filter(
                User.is_active == True,
                or_(
                    Patient.name.ilike(f'%{query}%'),
                    Patient.phone.ilike(f'%{query}%')
                )
            ).limit(10).all()
            
            results['patients'] = [{
                'id': pat.id,
                'name': pat.name,
                'phone': pat.phone,
                'email': pat.user.email
            } for pat in patients]
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

