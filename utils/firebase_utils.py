import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime, timedelta
import streamlit as st

# Initialize Firebase (only once)
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-key.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://cancelfillmd-pro-default-rtdb.firebaseio.com/'
        })
    return db

# Database operations
class FirebaseDB:
    def __init__(self):
        self.db = init_firebase()
    
    def add_to_waitlist(self, patient_data):
        """Add patient to waitlist"""
        ref = self.db.reference('waitlist')
        new_ref = ref.push(patient_data)
        return new_ref.key
    
    def get_waitlist(self, specialty=None, date=None):
        """Get waitlist patients with filters"""
        ref = self.db.reference('waitlist')
        all_patients = ref.get() or {}
        
        filtered = []
        for key, patient in all_patients.items():
            if specialty and patient.get('specialty') != specialty:
                continue
            if date and date not in patient.get('preferred_dates', []):
                continue
            patient['id'] = key
            filtered.append(patient)
        
        return filtered
    
    def add_appointment(self, appointment_data):
        """Add new appointment"""
        ref = self.db.reference('appointments')
        new_ref = ref.push(appointment_data)
        return new_ref.key
    
    def update_appointment(self, appointment_id, updates):
        """Update appointment status"""
        ref = self.db.reference(f'appointments/{appointment_id}')
        ref.update(updates)
    
    def get_appointments(self, status=None, date=None):
        """Get appointments with filters"""
        ref = self.db.reference('appointments')
        all_appointments = ref.get() or {}
        
        filtered = []
        for key, apt in all_appointments.items():
            if status and apt.get('status') != status:
                continue
            if date and apt.get('date') != date:
                continue
            apt['id'] = key
            filtered.append(apt)
        
        return filtered
    
    def log_notification(self, notification_data):
        """Log notification sent"""
        ref = self.db.reference('notifications')
        ref.push(notification_data)
    
    def create_booking_link(self, appointment_id, patient_id):
        """Create secure booking link"""
        import uuid
        token = str(uuid.uuid4())
        
        ref = self.db.reference('booking_tokens')
        ref.push({
            'token': token,
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=2)).isoformat(),
            'used': False
        })
        
        return f"{os.getenv('APP_URL')}/booking?token={token}"