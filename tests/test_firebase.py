# tests/test_firebase.py
"""
Tests for Firebase database operations
"""
import pytest
from datetime import datetime, timedelta
from utils.firebase_utils import FirebaseDB
from tests import TEST_PATIENT, TEST_APPOINTMENT

class TestFirebaseOperations:
    """Test Firebase database operations"""
    
    @pytest.fixture
    def db(self):
        """Create a test database instance"""
        # Use test database configuration
        return FirebaseDB()
    
    @pytest.fixture
    def test_patient_id(self, db):
        """Create a test patient and return ID"""
        patient_id = db.add_to_waitlist(TEST_PATIENT)
        yield patient_id
        # Cleanup after test
        try:
            db.db.reference(f'waitlist/{patient_id}').delete()
        except:
            pass
    
    @pytest.fixture
    def test_appointment_id(self, db):
        """Create a test appointment and return ID"""
        apt_id = db.add_appointment(TEST_APPOINTMENT)
        yield apt_id
        # Cleanup after test
        try:
            db.db.reference(f'appointments/{apt_id}').delete()
        except:
            pass
    
    def test_add_to_waitlist(self, db):
        """Test adding patient to waitlist"""
        patient_id = db.add_to_waitlist(TEST_PATIENT)
        
        assert patient_id is not None
        assert len(patient_id) > 0
        
        # Verify patient was added
        waitlist = db.get_waitlist()
        patient_ids = [p.get('id') for p in waitlist]
        assert patient_id in patient_ids
        
        # Cleanup
        db.db.reference(f'waitlist/{patient_id}').delete()
    
    def test_get_waitlist_with_filters(self, db, test_patient_id):
        """Test getting waitlist with filters"""
        # Get all patients
        all_patients = db.get_waitlist()
        assert len(all_patients) > 0
        
        # Filter by specialty
        derm_patients = db.get_waitlist(specialty='Dermatology')
        for patient in derm_patients:
            assert patient['specialty'] == 'Dermatology'
        
        # Filter by date
        date_patients = db.get_waitlist(date='2025-06-10')
        for patient in date_patients:
            assert '2025-06-10' in patient.get('preferred_dates', [])
    
    def test_add_appointment(self, db):
        """Test adding appointment"""
        apt_id = db.add_appointment(TEST_APPOINTMENT)
        
        assert apt_id is not None
        assert len(apt_id) > 0
        
        # Verify appointment was added
        appointments = db.get_appointments()
        apt_ids = [a.get('id') for a in appointments]
        assert apt_id in apt_ids
        
        # Cleanup
        db.db.reference(f'appointments/{apt_id}').delete()
    
    def test_update_appointment(self, db, test_appointment_id):
        """Test updating appointment status"""
        # Update to cancelled
        db.update_appointment(test_appointment_id, {
            'status': 'cancelled',
            'cancelled_at': datetime.now().isoformat(),
            'cancellation_reason': 'Test cancellation'
        })
        
        # Verify update
        appointments = db.get_appointments()
        updated_apt = next((a for a in appointments if a['id'] == test_appointment_id), None)
        
        assert updated_apt is not None
        assert updated_apt['status'] == 'cancelled'
        assert 'cancelled_at' in updated_apt
        assert updated_apt['cancellation_reason'] == 'Test cancellation'
    
    def test_get_appointments_with_filters(self, db, test_appointment_id):
        """Test getting appointments with filters"""
        # Get by status
        scheduled = db.get_appointments(status='scheduled')
        for apt in scheduled:
            assert apt['status'] == 'scheduled'
        
        # Get by date
        date_apts = db.get_appointments(date='2025-06-10')
        for apt in date_apts:
            assert apt['date'] == '2025-06-10'
    
    def test_create_booking_link(self, db, test_appointment_id, test_patient_id):
        """Test creating secure booking link"""
        link = db.create_booking_link(test_appointment_id, test_patient_id)
        
        assert link is not None
        assert 'token=' in link
        assert len(link) > 50  # Should be a reasonably long URL
    
    def test_log_notification(self, db):
        """Test logging notifications"""
        notification_data = {
            'appointment_id': 'test_apt_123',
            'patient_id': 'test_patient_123',
            'type': 'appointment_available',
            'sent_at': datetime.now().isoformat(),
            'sms_status': True,
            'email_status': True
        }
        
        db.log_notification(notification_data)
        
        # Verify notification was logged
        notifications = db.db.reference('notifications').get()
        assert notifications is not None
        assert len(notifications) > 0
    
    def test_appointment_availability_check(self, db):
        """Test checking appointment availability"""
        # Add a scheduled appointment
        scheduled_apt = TEST_APPOINTMENT.copy()
        scheduled_apt['status'] = 'scheduled'
        apt_id = db.add_appointment(scheduled_apt)
        
        # Get appointments and check availability
        appointments = db.get_appointments(date='2025-06-10')
        
        # Find our test appointment
        test_apt = next((a for a in appointments if a['id'] == apt_id), None)
        assert test_apt is not None
        assert test_apt['status'] == 'scheduled'
        
        # Cleanup
        db.db.reference(f'appointments/{apt_id}').delete()
    
    def test_waitlist_priority_scoring(self, db):
        """Test waitlist patient priority scoring"""
        # Add multiple patients with different wait times
        patient1 = TEST_PATIENT.copy()
        patient1['created_at'] = (datetime.now() - timedelta(days=7)).isoformat()
        patient1['notified_count'] = 0
        
        patient2 = TEST_PATIENT.copy()
        patient2['created_at'] = (datetime.now() - timedelta(days=1)).isoformat()
        patient2['notified_count'] = 3
        
        id1 = db.add_to_waitlist(patient1)
        id2 = db.add_to_waitlist(patient2)
        
        # In a real implementation, you would have a scoring function
        # This is a placeholder for testing the concept
        waitlist = db.get_waitlist()
        
        # Patient 1 should have higher priority (waited longer)
        p1 = next((p for p in waitlist if p['id'] == id1), None)
        p2 = next((p for p in waitlist if p['id'] == id2), None)
        
        assert p1 is not None
        assert p2 is not None
        
        # Cleanup
        db.db.reference(f'waitlist/{id1}').delete()
        db.db.reference(f'waitlist/{id2}').delete()

class TestFirebaseErrorHandling:
    """Test error handling in Firebase operations"""
    
    @pytest.fixture
    def db(self):
        return FirebaseDB()
    
    def test_update_nonexistent_appointment(self, db):
        """Test updating non-existent appointment"""
        # This should not raise an exception
        try:
            db.update_appointment('nonexistent_id', {'status': 'cancelled'})
        except Exception as e:
            pytest.fail(f"Update non-existent appointment raised exception: {e}")
    
    def test_invalid_data_types(self, db):
        """Test handling invalid data types"""
        # Test with None values
        patient_data = TEST_PATIENT.copy()
        patient_data['email'] = None  # Invalid email
        
        # Should handle gracefully
        try:
            patient_id = db.add_to_waitlist(patient_data)
            # Cleanup if it somehow succeeds
            if patient_id:
                db.db.reference(f'waitlist/{patient_id}').delete()
        except Exception as e:
            # Expected to fail validation
            assert 'email' in str(e).lower() or 'validation' in str(e).lower()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])