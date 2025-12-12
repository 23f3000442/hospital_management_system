from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from models import db, User, Patient

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'name', 'phone']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role='patient'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            name=data['name'],
            phone=data['phone'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender') or None,
            address=data.get('address') or None,
            blood_group=data.get('blood_group') or None
        )
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login for all users (admin, doctor, patient)"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 401
        
        # Create access token (string identity to satisfy PyJWT 'sub' claim type)
        access_token = create_access_token(identity=str(user.id))
        
        # Get role-specific info
        role_data = {}
        if user.role == 'doctor' and user.doctor:
            role_data = {
                'doctor_id': user.doctor.id,
                'name': user.doctor.name,
                'specialization': user.doctor.specialization
            }
        elif user.role == 'patient' and user.patient:
            role_data = {
                'patient_id': user.patient.id,
                'name': user.patient.name
            }
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                **role_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        
        if user.role == 'doctor' and user.doctor:
            user_data['doctor'] = {
                'id': user.doctor.id,
                'name': user.doctor.name,
                'specialization': user.doctor.specialization,
                'phone': user.doctor.phone,
                'department_id': user.doctor.department_id
            }
        elif user.role == 'patient' and user.patient:
            user_data['patient'] = {
                'id': user.patient.id,
                'name': user.patient.name,
                'phone': user.patient.phone,
                'date_of_birth': user.patient.date_of_birth.isoformat() if user.patient.date_of_birth else None,
                'gender': user.patient.gender,
                'address': user.patient.address,
                'blood_group': user.patient.blood_group
            }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

