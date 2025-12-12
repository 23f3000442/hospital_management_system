# Hospital Management System (HMS)

A comprehensive web-based Hospital Management System built with Flask (backend) and Vue.js (frontend).

## Features

### Admin Features
- Dashboard with statistics (total doctors, patients, appointments)
- Manage doctors (add, edit, delete/deactivate)
- Manage patients (view, search, delete/deactivate)
- View and manage all appointments
- Search functionality for doctors and patients
- Department management

### Doctor Features
- Dashboard with upcoming appointments and statistics
- View and manage appointments
- Mark appointments as completed
- Add diagnosis, prescription, and treatment notes
- View patient list and treatment history
- Set availability for next 7 days

### Patient Features
- Browse departments and find doctors
- Search doctors by name, specialization, or department
- View doctor availability
- Book, reschedule, and cancel appointments
- View treatment history with prescriptions
- Export treatment history as CSV
- Update profile information

## Technology Stack

- **Backend:** Flask 3.0, Flask-SQLAlchemy, Flask-JWT-Extended
- **Frontend:** Vue.js 3.3, Bootstrap 5.3, Axios
- **Database:** SQLite
- **Authentication:** JWT Token-based
- **Caching:** Redis (configured, optional)
- **Background Jobs:** Celery (configured, optional)

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The backend server will start at `http://localhost:5001`

### Frontend Setup

The frontend uses CDN-based Vue.js, so no build step is required. Simply serve the frontend directory using the Flask backend or any web server.

## Default Credentials

- **Admin:**
  - Username: `admin`
  - Password: `admin123`

After registration, you can create doctor accounts through the admin dashboard.

## Database

The SQLite database (`hospital.db`) will be created automatically when you first run the application. The admin user is created programmatically on first run.

### Database Schema

- **Users:** Authentication and user management
- **Departments:** Medical departments/specializations
- **Doctors:** Doctor profiles linked to users
- **Patients:** Patient profiles linked to users
- **Appointments:** Booking and scheduling
- **Treatments:** Medical records and prescriptions
- **DoctorAvailability:** Doctor scheduling

## API Endpoints

### Authentication
- `POST /api/auth/register` - Patient registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Admin
- `GET /api/admin/dashboard` - Dashboard statistics
- `GET /api/admin/doctors` - List all doctors
- `POST /api/admin/doctors` - Create doctor
- `PUT /api/admin/doctors/:id` - Update doctor
- `DELETE /api/admin/doctors/:id` - Deactivate doctor
- `GET /api/admin/patients` - List all patients
- `GET /api/admin/appointments` - List all appointments
- `GET /api/admin/departments` - List departments
- `GET /api/admin/search` - Search doctors/patients

### Doctor
- `GET /api/doctor/dashboard` - Doctor dashboard
- `GET /api/doctor/appointments` - Doctor's appointments
- `PUT /api/doctor/appointments/:id/complete` - Complete appointment with treatment
- `GET /api/doctor/patients` - List doctor's patients
- `GET /api/doctor/patients/:id/history` - Patient treatment history
- `GET /api/doctor/availability` - Get availability
- `POST /api/doctor/availability` - Set availability

### Patient
- `GET /api/patient/dashboard` - Patient dashboard
- `GET /api/patient/profile` - Get profile
- `PUT /api/patient/profile` - Update profile
- `GET /api/patient/doctors` - Search doctors
- `POST /api/patient/appointments` - Book appointment
- `PUT /api/patient/appointments/:id` - Reschedule appointment
- `DELETE /api/patient/appointments/:id` - Cancel appointment
- `GET /api/patient/treatment-history` - Get treatment history
- `GET /api/patient/export-treatments` - Export treatments as CSV

## Features Implementation

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (Admin, Doctor, Patient)
- Protected routes with middleware

### Appointment Management
- Prevents double-booking for same doctor/time
- Status tracking (Booked, Completed, Cancelled)
- Automatic validation of appointment dates

### Search Functionality
- Real-time search for doctors by name/specialization
- Patient search by name/phone
- Department-wise doctor filtering

### Treatment Records
- Complete medical history tracking
- Diagnosis, prescription, and notes
- Next visit recommendations
- CSV export functionality

## Optional Features (Configured)

### Redis Caching
Redis is used for caching selected endpoints (admin dashboard and departments). Ensure Redis is running at `redis://localhost:6379/0`.

### Celery Background Jobs (Async & Scheduled)
Celery app is wired with Redis backend. Jobs:
1. Daily reminders (08:00 UTC)
2. Monthly doctor reports (1st of month, 08:00 UTC)
3. Patient CSV export (async) with status polling API

Run workers and scheduler in two terminals:
```bash
cd backend
source venv/bin/activate
celery -A celery_tasks.celery worker --loglevel=info
celery -A celery_tasks.celery beat --loglevel=info
```

Optional environment variables:
```bash
# Google Chat notifications for reminders
export GOOGLE_CHAT_WEBHOOK_URL="https://chat.googleapis.com/v1/spaces/.../messages?key=...&token=..."

# Email for monthly reports
export MAIL_USERNAME="your@gmail.com"
export MAIL_PASSWORD="app_password"
```

## Project Structure

```
hospitalmgmt-appdev2/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── celery_tasks.py       # Background jobs
│   ├── config/
│   │   └── config.py         # Configuration
│   ├── models/
│   │   └── __init__.py       # Database models
│   └── routes/
│       ├── auth.py           # Authentication routes
│       ├── admin.py          # Admin routes
│       ├── doctor.py         # Doctor routes
│       └── patient.py        # Patient routes
├── frontend/
│   ├── index.html            # Main HTML entry point
│   └── src/
│       ├── app.js            # Login, Register, Admin components
│       ├── doctor-component.js   # Doctor dashboard
│       ├── patient-component.js  # Patient dashboard
│       └── main.js           # Router and app initialization
└── README.md
```

## Development

### Adding New Features
1. Add backend routes in appropriate `routes/*.py` file
2. Add frontend components in `frontend/src/*.js`
3. Update router in `main.js` if needed

### Testing
1. Start the Flask backend
2. Open browser to `http://localhost:5001`
3. Login with admin credentials or register as a patient
4. Test all role-specific features
5. For async CSV export (Patient > History), click Export; it triggers a Celery job and downloads when ready

## Security Notes

- Change default admin password in production
- Set strong `SECRET_KEY` and `JWT_SECRET_KEY` in environment variables
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Enable CORS only for trusted origins

## Future Enhancements

- Payment integration
- Video consultation
- Mobile responsive UI improvements
- Email/SMS notifications
- Advanced analytics and reporting
- Prescription printing
- Medical test results upload

## License

This project is created for educational purposes.

## Support

For issues or questions, please contact the development team.

