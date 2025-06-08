import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
import os
from datetime import datetime

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
    
    def get_appointments(self, status=None, date=None):
        """Get appointments with optional filtering"""
        if not self.db:
            # Return demo data if no Firebase connection
            appointments = self._get_demo_appointments()
        else:
            try:
                appointments = []
                # Start with base collection
                collection_ref = self.db.collection('appointments')
                
                # Apply filters if provided
                query = collection_ref
                if status:
                    query = query.where('status', '==', status)
                if date:
                    query = query.where('date', '==', date)
                
                # Execute query
                docs = query.stream()
                for doc in docs:
                    appointment = doc.to_dict()
                    appointment['id'] = doc.id
                    appointments.append(appointment)
            except Exception as e:
                st.error(f"Error fetching appointments: {str(e)}")
                appointments = self._get_demo_appointments()
        
        # Apply filters to results if using demo data
        if status:
            appointments = [apt for apt in appointments if apt.get('status') == status]
        if date:
            appointments = [apt for apt in appointments if apt.get('date') == date]
            
        return appointments
    
    def _get_demo_appointments(self):
        """Return demo appointments for testing"""
        from datetime import datetime, timedelta
        
        demo_appointments = []
        today = datetime.now().date()
        
        for i in range(20):
            date = today + timedelta(days=i-5)  # Some past, some future
            demo_appointments.append({
                'id': f'demo_{i}',
                'patient_name': f'Demo Patient {i}',
                'patient_id': f'P00{i}',
                'date': date.strftime('%Y-%m-%d'),
                'time': f'{9 + i % 8}:00 AM',
                'doctor': f'Dr. Demo {i % 3}',
                'specialty': ['General Practice', 'Cardiology', 'Dermatology'][i % 3],
                'status': ['scheduled', 'cancelled', 'filled', 'completed'][i % 4],
                'created_at': datetime.now().isoformat()
            })
        
        return demo_appointments
    
    def get_waitlist(self, specialty=None):
        """Get waitlist entries with optional filtering"""
        if not self.db:
            waitlist = self._get_demo_waitlist()
        else:
            try:
                waitlist = []
                # Start with base collection
                collection_ref = self.db.collection('waitlist')
                
                # Apply filter if provided
                query = collection_ref
                if specialty:
                    query = query.where('specialty', '==', specialty)
                
                # Execute query
                docs = query.stream()
                for doc in docs:
                    entry = doc.to_dict()
                    entry['id'] = doc.id
                    waitlist.append(entry)
            except Exception as e:
                st.error(f"Error fetching waitlist: {str(e)}")
                waitlist = self._get_demo_waitlist()
        
        # Apply filter to results if using demo data
        if specialty:
            waitlist = [entry for entry in waitlist if entry.get('specialty') == specialty]
            
        return waitlist
    
    def _get_demo_waitlist(self):
        """Return demo waitlist for testing"""
        from datetime import datetime
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
            # Add timestamp
            appointment_data['created_at'] = datetime.now().isoformat()
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
            # Add timestamp
            update_data['updated_at'] = datetime.now().isoformat()
            self.db.collection('appointments').document(appointment_id).update(update_data)
            return True
        except Exception as e:
            st.error(f"Error updating appointment: {str(e)}")
            return False
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment"""
        if not self.db:
            st.success("Demo mode: Appointment would be deleted")
            return True
        
        try:
            self.db.collection('appointments').document(appointment_id).delete()
            return True
        except Exception as e:
            st.error(f"Error deleting appointment: {str(e)}")
            return False
    
    def add_to_waitlist(self, waitlist_data):
        """Add patient to waitlist"""
        if not self.db:
            st.success("Demo mode: Patient would be added to waitlist")
            return True
        
        try:
            # Add timestamp
            waitlist_data['created_at'] = datetime.now().isoformat()
            waitlist_data['status'] = 'active'
            self.db.collection('waitlist').add(waitlist_data)
            return True
        except Exception as e:
            st.error(f"Error adding to waitlist: {str(e)}")
            return False
    
    def remove_from_waitlist(self, waitlist_id):
        """Remove patient from waitlist"""
        if not self.db:
            st.success("Demo mode: Patient would be removed from waitlist")
            return True
        
        try:
            self.db.collection('waitlist').document(waitlist_id).delete()
            return True
        except Exception as e:
            st.error(f"Error removing from waitlist: {str(e)}")
            return False
    
    def get_notifications(self):
        """Get all notifications"""
        if not self.db:
            return []
        
        try:
            notifications = []
            docs = self.db.collection('notifications').order_by(
                'created_at', direction=firestore.Query.DESCENDING
            ).limit(100).stream()
            
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
            # Add timestamp
            notification_data['created_at'] = datetime.now().isoformat()
            self.db.collection('notifications').add(notification_data)
            return True
        except Exception as e:
            st.error(f"Error adding notification: {str(e)}")
            return False
    
    def get_users(self):
        """Get all users"""
        if not self.db:
            return []
        
        try:
            users = []
            docs = self.db.collection('users').stream()
            for doc in docs:
                user = doc.to_dict()
                user['id'] = doc.id
                # Don't include password hash in results
                user.pop('password', None)
                users.append(user)
            return users
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return []
    
    def add_user(self, user_data):
        """Add a new user"""
        if not self.db:
            st.success("Demo mode: User would be added")
            return True
        
        try:
            # Add timestamp
            user_data['created_at'] = datetime.now().isoformat()
            user_data['last_login'] = None
            self.db.collection('users').add(user_data)
            return True
        except Exception as e:
            st.error(f"Error adding user: {str(e)}")
            return False
    
    def get_user_by_username(self, username):
        """Get user by username"""
        if not self.db:
            # Return demo user
            if username == "admin":
                return {
                    'id': 'demo_admin',
                    'username': 'admin',
                    'password': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGAmKRS/tGy',  # bcrypt hash of 'admin123'
                    'role': 'Administrator',
                    'name': 'Demo Admin'
                }
            return None
        
        try:
            users = self.db.collection('users').where('username', '==', username).limit(1).stream()
            for doc in users:
                user = doc.to_dict()
                user['id'] = doc.id
                return user
            return None
        except Exception as e:
            st.error(f"Error fetching user: {str(e)}")
            return None
    
    def update_user_login(self, user_id):
        """Update user's last login time"""
        if not self.db:
            return True
        
        try:
            self.db.collection('users').document(user_id).update({
                'last_login': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            st.error(f"Error updating user login: {str(e)}")
            return False
