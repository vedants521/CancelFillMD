import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
import os

@st.cache_resource
def init_firebase():
    """Initialize Firebase connection using Streamlit secrets or environment variables"""
    try:
        if not firebase_admin._apps:
            # Try to use Streamlit secrets first
            if "firebase" in st.secrets:
                # Create credentials from secrets
                firebase_config = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_config)
            # Try environment variable
            elif os.getenv('FIREBASE_CREDENTIALS'):
                firebase_config = json.loads(os.getenv('FIREBASE_CREDENTIALS'))
                cred = credentials.Certificate(firebase_config)
            # Try local file (for development)
            elif os.path.exists('firebase-key.json'):
                cred = credentials.Certificate('firebase-key.json')
            else:
                # Use demo mode
                st.warning("No Firebase credentials found. Running in demo mode.")
                return None
            
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {str(e)}")
        return None

class FirebaseDB:
    def __init__(self):
        self.db = init_firebase()
    
    def get_appointments(self):
        """Get all appointments"""
        if not self.db:
            # Return demo data if no Firebase connection
            return self._get_demo_appointments()
        
        try:
            appointments = []
            docs = self.db.collection('appointments').stream()
            for doc in docs:
                appointment = doc.to_dict()
                appointment['id'] = doc.id
                appointments.append(appointment)
            return appointments
        except Exception as e:
            st.error(f"Error fetching appointments: {str(e)}")
            return []
    
    def _get_demo_appointments(self):
        """Return demo appointments for testing"""
        from datetime import datetime, timedelta
        
        demo_appointments = []
        today = datetime.now().date()
        
        for i in range(10):
            date = today + timedelta(days=i)
            demo_appointments.append({
                'id': f'demo_{i}',
                'patient_name': f'Demo Patient {i}',
                'patient_id': f'P00{i}',
                'date': date.strftime('%Y-%m-%d'),
                'time': f'{9 + i % 8}:00 AM',
                'doctor': f'Dr. Demo {i % 3}',
                'specialty': ['General Practice', 'Cardiology', 'Dermatology'][i % 3],
                'status': ['scheduled', 'cancelled', 'filled'][i % 3],
                'created_at': datetime.now().isoformat()
            })
        
        return demo_appointments
    
    def get_waitlist(self):
        """Get all waitlist entries"""
        if not self.db:
            return self._get_demo_waitlist()
        
        try:
            waitlist = []
            docs = self.db.collection('waitlist').stream()
            for doc in docs:
                entry = doc.to_dict()
                entry['id'] = doc.id
                waitlist.append(entry)
            return waitlist
        except Exception as e:
            st.error(f"Error fetching waitlist: {str(e)}")
            return []
    
    def _get_demo_waitlist(self):
        """Return demo waitlist for testing"""
        demo_waitlist = []
        
        for i in range(20):
            demo_waitlist.append({
                'id': f'wait_{i}',
                'patient_name': f'Waitlist Patient {i}',
                'patient_id': f'W00{i}',
                'phone': f'+1555000{1000 + i}',
                'email': f'patient{i}@demo.com',
                'specialty': ['General Practice', 'Cardiology', 'Dermatology', 'Orthopedics'][i % 4],
                'flexibility': ['Very Flexible', 'Somewhat Flexible', 'Not Flexible'][i % 3],
                'preferred_times': ['Morning', 'Afternoon', 'Evening'][i % 3],
                'created_at': datetime.now().isoformat()
            })
        
        return demo_waitlist
    
    def add_appointment(self, appointment_data):
        """Add a new appointment"""
        if not self.db:
            st.success("Demo mode: Appointment would be added")
            return True
        
        try:
            self.db.collection('appointments').add(appointment_data)
            return True
        except Exception as e:
            st.error(f"Error adding appointment: {str(e)}")
            return False
    
    def update_appointment(self, appointment_id, update_data):
        """Update an appointment"""
        if not self.db:
            st.success("Demo mode: Appointment would be updated")
            return True
        
        try:
            self.db.collection('appointments').document(appointment_id).update(update_data)
            return True
        except Exception as e:
            st.error(f"Error updating appointment: {str(e)}")
            return False
    
    def add_to_waitlist(self, waitlist_data):
        """Add patient to waitlist"""
        if not self.db:
            st.success("Demo mode: Patient would be added to waitlist")
            return True
        
        try:
            self.db.collection('waitlist').add(waitlist_data)
            return True
        except Exception as e:
            st.error(f"Error adding to waitlist: {str(e)}")
            return False
    
    def get_notifications(self):
        """Get all notifications"""
        if not self.db:
            return []
        
        try:
            notifications = []
            docs = self.db.collection('notifications').stream()
            for doc in docs:
                notification = doc.to_dict()
                notification['id'] = doc.id
                notifications.append(notification)
            return notifications
        except Exception as e:
            st.error(f"Error fetching notifications: {str(e)}")
            return []
    
    def add_notification(self, notification_data):
        """Add a notification record"""
        if not self.db:
            return True
        
        try:
            self.db.collection('notifications').add(notification_data)
            return True
        except Exception as e:
            st.error(f"Error adding notification: {str(e)}")
            return False
