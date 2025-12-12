from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import os

from config.config import Config
from redis import Redis
from models import db, User, Department, Doctor, Patient, Appointment, Treatment, DoctorAvailability

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    JWTManager(app)
    # Redis client for caching/queues
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    
    # Import routes
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    # Initialize Celery (tasks and beat schedule)
    try:
        from celery_tasks import init_celery
        init_celery(app)
    except Exception as _:
        # Celery initialization is optional during simple runs
        pass
    
    # Serve frontend
    @app.route('/')
    def serve_frontend():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Initialize database and create admin
    with app.app_context():
        db.create_all()
        init_database()
    
    return app

def init_database():
    """Initialize database with admin user and sample departments"""
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            password=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        print('Admin user created: username=admin, password=admin123')
    
    # Create sample departments if none exist
    if Department.query.count() == 0:
        departments = [
            Department(name='Cardiology', description='Heart and cardiovascular system'),
            Department(name='Neurology', description='Brain and nervous system'),
            Department(name='Orthopedics', description='Bones, joints, and muscles'),
            Department(name='Pediatrics', description='Child healthcare'),
            Department(name='Dermatology', description='Skin, hair, and nails'),
            Department(name='General Medicine', description='General health concerns')
        ]
        for dept in departments:
            db.session.add(dept)
        print('Sample departments created')
    
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)

