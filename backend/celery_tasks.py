from celery import Celery
from celery.schedules import crontab
from datetime import datetime, date, timedelta
import json
import smtplib
from email.mime.text import MIMEText
import requests

# Celery instance (configured later by init_celery)
import os
import sys
# Ensure backend directory is on sys.path for worker subprocesses
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
_default_redis = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
celery = Celery('hms', broker=_default_redis, backend=_default_redis)


def init_celery(app):
    """Bind Celery to the Flask app and configure beat schedule."""
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        timezone=app.config.get('CELERY_TIMEZONE', 'UTC'),
        beat_schedule={
            'daily-reminders': {
                'task': 'celery_tasks.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),  # 8:00 UTC; adjust env-side if needed
            },
            'monthly-doctor-reports': {
                'task': 'celery_tasks.send_monthly_reports',
                'schedule': crontab(hour=8, minute=0, day_of_month=1),
            },
        },
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            from app import create_app  # local import to avoid cycles
            flask_app = create_app()
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def _send_google_chat(webhook_url: str, text: str) -> None:
    if not webhook_url:
        return
    try:
        requests.post(webhook_url, json={"text": text}, timeout=10)
    except Exception:
        pass


def _send_email(smtp_server, port, username, password, to_email, subject, html_body):
    if not (smtp_server and username and password and to_email):
        return
    msg = MIMEText(html_body, 'html')
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = to_email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        server.sendmail(username, [to_email], msg.as_string())
        server.quit()
    except Exception:
        pass


@celery.task(name='celery_tasks.send_daily_reminders')
def send_daily_reminders():
    """Send reminders to patients with appointments today via Google Chat or email."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from models import Appointment
        today = date.today()
        appointments = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status == 'Booked'
        ).all()
        webhook = app.config.get('GOOGLE_CHAT_WEBHOOK_URL')
        for apt in appointments:
            patient = apt.patient
            message = (
                f"Reminder: {patient.name}, your appointment with Dr. {apt.doctor.name} "
                f"is today at {apt.appointment_time.strftime('%H:%M')}"
            )
            _send_google_chat(webhook, message)
        return f"Sent {len(appointments)} reminders"


@celery.task(name='celery_tasks.send_monthly_reports')
def send_monthly_reports():
    """Generate monthly activity report for each doctor and email it if SMTP is configured."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from models import Doctor, Appointment

        today = date.today()
        if today.month == 1:
            first_day_last_month = date(today.year - 1, 12, 1)
        else:
            first_day_last_month = date(today.year, today.month - 1, 1)
        last_day_last_month = date(today.year, today.month, 1) - timedelta(days=1)

        doctors = Doctor.query.all()
        for doctor in doctors:
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= first_day_last_month,
                Appointment.appointment_date <= last_day_last_month
            ).all()

            report_html = f"""
            <html>
            <body>
                <h2>Monthly Activity Report</h2>
                <p><strong>Doctor:</strong> {doctor.name}</p>
                <p><strong>Period:</strong> {first_day_last_month} to {last_day_last_month}</p>
                <ul>
                    <li>Total Appointments: {len(appointments)}</li>
                    <li>Completed: {len([a for a in appointments if a.status == 'Completed'])}</li>
                    <li>Cancelled: {len([a for a in appointments if a.status == 'Cancelled'])}</li>
                </ul>
                <table border="1" cellpadding="6" cellspacing="0">
                    <tr><th>Date</th><th>Patient</th><th>Status</th><th>Diagnosis</th></tr>
            """

            for apt in appointments:
                diagnosis = apt.treatment.diagnosis if apt.treatment else '—'
                report_html += f"<tr><td>{apt.appointment_date}</td><td>{apt.patient.name}</td><td>{apt.status}</td><td>{diagnosis}</td></tr>"
            report_html += "</table></body></html>"

            _send_email(
                app.config.get('MAIL_SERVER'),
                app.config.get('MAIL_PORT'),
                app.config.get('MAIL_USERNAME'),
                app.config.get('MAIL_PASSWORD'),
                doctor.user.email if doctor.user and doctor.user.email else None,
                "Monthly Activity Report",
                report_html,
            )
        return f"Sent {len(doctors)} monthly reports"


@celery.task(name='celery_tasks.export_patient_treatments')
def export_patient_treatments(patient_id: int):
    """Export patient's treatment history as CSV and return content as string."""
    from app import create_app
    import csv, io
    app = create_app()
    with app.app_context():
        from models import Patient, Appointment
        patient = Patient.query.get(patient_id)
        if not patient:
            return ''
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.status == 'Completed'
        ).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Patient ID', 'Patient Name', 'Doctor', 'Date', 'Diagnosis', 'Prescription', 'Next Visit'])
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
        return output.getvalue()

