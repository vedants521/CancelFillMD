# tests/test_validation.py
"""
Tests for validation utilities
"""
import pytest
from datetime import date, time, datetime, timedelta
from utils.validation_utils import (
    FormValidator, 
    DataValidator, 
    BusinessRuleValidator,
    DataSanitizer,
    ValidationError
)

class TestFormValidator:
    """Test form validation functions"""
    
    def test_validate_required(self):
        """Test required field validation"""
        # Valid cases
        assert FormValidator.validate_required("test", "Field") is True
        assert FormValidator.validate_required(123, "Field") is True
        assert FormValidator.validate_required([1, 2, 3], "Field") is True
        
        # Invalid cases
        with pytest.raises(ValidationError):
            FormValidator.validate_required("", "Field")
        with pytest.raises(ValidationError):
            FormValidator.validate_required(None, "Field")
        with pytest.raises(ValidationError):
            FormValidator.validate_required([], "Field")
    
    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        valid_emails = [
            'user@example.com',
            'test.user@example.com',
            'user+tag@example.co.uk',
            'user123@subdomain.example.com'
        ]
        
        for email in valid_emails:
            valid, msg = FormValidator.validate_email(email)
            assert valid is True
            assert msg == "Valid email"
        
        # Invalid emails
        invalid_emails = [
            '',
            'notanemail',
            '@example.com',
            'user@',
            'user@.com',
            'user space@example.com',
            'user@example'
        ]
        
        for email in invalid_emails:
            valid, msg = FormValidator.validate_email(email)
            assert valid is False
        
        # Test common typo detection
        valid, msg = FormValidator.validate_email('user@gmial.com')
        assert valid is False
        assert 'gmail.com' in msg
    
    def test_validate_phone(self):
        """Test phone number validation"""
        # Valid US phone numbers
        valid_phones = [
            '5551234567',
            '555-123-4567',
            '(555) 123-4567',
            '555.123.4567',
            '15551234567',
            '1-555-123-4567',
            '+1 555 123 4567'
        ]
        
        for phone in valid_phones:
            valid, formatted = FormValidator.validate_phone(phone, 'US')
            assert valid is True
            # Check formatting
            assert '(' in formatted or '+1' in formatted
        
        # Invalid phone numbers
        invalid_phones = [
            '',
            '123',
            '555123456',  # Too short
            '55512345678',  # Too long (without country code)
            'abcdefghij',
            '123-456-789'
        ]
        
        for phone in invalid_phones:
            valid, msg = FormValidator.validate_phone(phone, 'US')
            assert valid is False
    
    def test_validate_date(self):
        """Test date validation"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        # Valid date
        valid, msg = FormValidator.validate_date(tomorrow)
        assert valid is True
        
        # Test date string
        valid, msg = FormValidator.validate_date('2025-06-10')
        assert valid is True
        
        # Invalid date format
        valid, msg = FormValidator.validate_date('06/10/2025')
        assert valid is False
        assert 'Invalid date format' in msg
        
        # Test min date
        valid, msg = FormValidator.validate_date(yesterday, min_date=today)
        assert valid is False
        assert 'cannot be before' in msg
        
        # Test max date
        next_week = today + timedelta(days=7)
        valid, msg = FormValidator.validate_date(next_week, max_date=tomorrow)
        assert valid is False
        assert 'cannot be after' in msg
    
    def test_validate_time_slot(self):
        """Test appointment time validation"""
        # Valid business hours
        valid, msg = FormValidator.validate_time_slot('10:00 AM')
        assert valid is True
        
        valid, msg = FormValidator.validate_time_slot('4:30 PM')
        assert valid is True
        
        # Invalid format
        valid, msg = FormValidator.validate_time_slot('10:00')
        assert valid is False
        assert 'Invalid time format' in msg
        
        # Outside business hours
        valid, msg = FormValidator.validate_time_slot('6:00 AM')
        assert valid is False
        assert 'must be between' in msg
        
        valid, msg = FormValidator.validate_time_slot('9:00 PM')
        assert valid is False
    
    def test_validate_name(self):
        """Test name validation"""
        # Valid names
        valid_names = [
            'John Doe',
            'Mary Smith-Johnson',
            "Patrick O'Brien",
            'José García',
            'Anne Marie'
        ]
        
        for name in valid_names:
            valid, formatted = FormValidator.validate_name(name)
            assert valid is True
            # Check proper capitalization
            assert formatted[0].isupper()
        
        # Invalid names
        invalid_names = [
            '',
            'J',  # Too short
            'A' * 51,  # Too long
            'John123',  # Contains numbers
            'John@Doe',  # Contains invalid characters
        ]
        
        for name in invalid_names:
            valid, msg = FormValidator.validate_name(name)
            assert valid is False

class TestDataValidator:
    """Test data integrity validation"""
    
    def test_validate_appointment_availability(self):
        """Test appointment slot availability validation"""
        existing_appointments = [
            {
                'date': '2025-06-10',
                'time': '10:00 AM',
                'status': 'scheduled'
            },
            {
                'date': '2025-06-10',
                'time': '11:00 AM',
                'status': 'cancelled'
            }
        ]
        
        # Test unavailable slot
        valid, msg = DataValidator.validate_appointment_availability(
            date(2025, 6, 10),
            '10:00 AM',
            existing_appointments
        )
        assert valid is False
        assert 'already booked' in msg
        
        # Test available slot (cancelled)
        valid, msg = DataValidator.validate_appointment_availability(
            date(2025, 6, 10),
            '11:00 AM',
            existing_appointments
        )
        assert valid is True
        
        # Test completely new slot
        valid, msg = DataValidator.validate_appointment_availability(
            date(2025, 6, 10),
            '2:00 PM',
            existing_appointments
        )
        assert valid is True
        
        # Test past appointment
        past_date = date.today() - timedelta(days=1)
        valid, msg = DataValidator.validate_appointment_availability(
            past_date,
            '10:00 AM',
            existing_appointments
        )
        assert valid is False
        assert 'past' in msg.lower()
    
    def test_validate_waitlist_preferences(self):
        """Test waitlist preference validation"""
        # Valid preferences
        valid_prefs = {
            'preferred_dates': ['2025-06-10', '2025-06-11'],
            'time_preferences': ['morning', 'afternoon']
        }
        valid, msg = DataValidator.validate_waitlist_preferences(valid_prefs)
        assert valid is True
        
        # Missing dates
        invalid_prefs = {
            'preferred_dates': [],
            'time_preferences': ['morning']
        }
        valid, msg = DataValidator.validate_waitlist_preferences(invalid_prefs)
        assert valid is False
        assert 'preferred date' in msg
        
        # Invalid time preference
        invalid_prefs = {
            'preferred_dates': ['2025-06-10'],
            'time_preferences': ['invalid_time']
        }
        valid, msg = DataValidator.validate_waitlist_preferences(invalid_prefs)
        assert valid is False
        assert 'Invalid time preference' in msg
    
    def test_validate_booking_eligibility(self):
        """Test patient eligibility for booking"""
        patient = {
            'specialty': 'Dermatology',
            'preferred_dates': ['2025-06-10', '2025-06-11'],
            'time_preferences': ['morning', 'afternoon']
        }
        
        appointment = {
            'specialty': 'Dermatology',
            'date': '2025-06-10',
            'time': '10:00 AM'
        }
        
        # Valid match
        valid, msg = DataValidator.validate_booking_eligibility(patient, appointment)
        assert valid is True
        
        # Wrong specialty
        appointment['specialty'] = 'Cardiology'
        valid, msg = DataValidator.validate_booking_eligibility(patient, appointment)
        assert valid is False
        assert 'Specialty mismatch' in msg
        
        # Date not in preferences
        appointment['specialty'] = 'Dermatology'
        appointment['date'] = '2025-06-15'
        valid, msg = DataValidator.validate_booking_eligibility(patient, appointment)
        assert valid is False
        assert 'not in patient\'s preferences' in msg

class TestBusinessRuleValidator:
    """Test business rule validation"""
    
    def test_validate_cancellation_window(self):
        """Test cancellation notice validation"""
        # Appointment tomorrow at 2 PM
        tomorrow_2pm = datetime.combine(
            date.today() + timedelta(days=1),
            time(14, 0)
        )
        
        # More than 24 hours notice - should be valid
        valid, msg = BusinessRuleValidator.validate_cancellation_window(
            tomorrow_2pm,
            min_hours_notice=24
        )
        assert valid is True
        
        # Less than 24 hours notice
        soon = datetime.now() + timedelta(hours=12)
        valid, msg = BusinessRuleValidator.validate_cancellation_window(
            soon,
            min_hours_notice=24
        )
        assert valid is False
        assert '24 hours notice' in msg
    
    def test_validate_max_waitlist_entries(self):
        """Test maximum waitlist entries per patient"""
        current_waitlist = [
            {'email': 'patient1@example.com', 'active': True},
            {'email': 'patient1@example.com', 'active': True},
            {'email': 'patient2@example.com', 'active': True},
        ]
        
        # Under limit
        valid, msg = BusinessRuleValidator.validate_max_waitlist_entries(
            'patient2@example.com',
            current_waitlist,
            max_entries=5
        )
        assert valid is True
        
        # At limit
        valid, msg = BusinessRuleValidator.validate_max_waitlist_entries(
            'patient1@example.com',
            current_waitlist,
            max_entries=2
        )
        assert valid is False
        assert 'Maximum 2' in msg
    
    def test_validate_appointment_duration(self):
        """Test appointment duration by specialty"""
        # Valid duration
        valid, msg = BusinessRuleValidator.validate_appointment_duration(
            '30 minutes',
            'Dermatology'
        )
        assert valid is True
        
        # Too short
        valid, msg = BusinessRuleValidator.validate_appointment_duration(
            '10 minutes',
            'Dermatology'
        )
        assert valid is False
        assert 'Minimum duration' in msg
        
        # Too long
        valid, msg = BusinessRuleValidator.validate_appointment_duration(
            '90 minutes',
            'General Practice'
        )
        assert valid is False
        assert 'Maximum duration' in msg

class TestDataSanitizer:
    """Test data sanitization functions"""
    
    def test_sanitize_phone(self):
        """Test phone number sanitization"""
        # Various formats to standard format
        phones = [
            ('555-123-4567', '(555) 123-4567'),
            ('5551234567', '(555) 123-4567'),
            ('(555) 123-4567', '(555) 123-4567'),
            ('1-555-123-4567', '+1 (555) 123-4567'),
            ('+1 555 123 4567', '+1 (555) 123-4567')
        ]
        
        for input_phone, expected in phones:
            sanitized = DataSanitizer.sanitize_phone(input_phone)
            assert sanitized == expected
    
    def test_sanitize_name(self):
        """Test name sanitization"""
        # Test cases
        names = [
            ('john doe', 'John Doe'),
            ('MARY SMITH', 'Mary Smith'),
            ('  jane   jones  ', 'Jane Jones'),
            ("o'brien", "O'Brien"),
            ('smith-johnson', 'Smith-Johnson')
        ]
        
        for input_name, expected in names:
            sanitized = DataSanitizer.sanitize_name(input_name)
            assert sanitized == expected
    
    def test_sanitize_email(self):
        """Test email sanitization"""
        # Should lowercase and strip
        emails = [
            ('User@Example.com', 'user@example.com'),
            ('  test@example.com  ', 'test@example.com'),
            ('ADMIN@CLINIC.COM', 'admin@clinic.com')
        ]
        
        for input_email, expected in emails:
            sanitized = DataSanitizer.sanitize_email(input_email)
            assert sanitized == expected
    
    def test_sanitize_text_input(self):
        """Test general text sanitization"""
        # Test cases
        texts = [
            ('  Hello   World  ', 'Hello World'),
            ('Multiple     spaces', 'Multiple spaces'),
            ('\n\nNewlines\n\n', 'Newlines'),
            ('A' * 100 + ' test', 'A' * 97 + '...')  # Truncation
        ]
        
        for input_text, expected in texts:
            sanitized = DataSanitizer.sanitize_text_input(input_text, max_length=100)
            assert sanitized == expected

if __name__ == '__main__':
    pytest.main([__file__, '-v'])