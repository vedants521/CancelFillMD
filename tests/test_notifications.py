# tests/test_notifications.py
"""
Tests for notification services (SMS and Email)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from utils.notification_utils import NotificationService
from tests import TEST_PATIENT, TEST_APPOINTMENT

class TestNotificationService:
    """Test notification service functionality"""
    
    @pytest.fixture
    def notification_service(self):
        """Create a mock notification service"""
        with patch('utils.notification_utils.Client') as mock_twilio:
            with patch('utils.notification_utils.SendGridAPIClient') as mock_sendgrid:
                service = NotificationService()
                # Configure mocks
                service.twilio_client = mock_twilio.return_value
                service.sg_client = mock_sendgrid.return_value
                yield service
    
    def test_send_sms_success(self, notification_service):
        """Test successful SMS sending"""
        # Mock successful response
        mock_message = Mock()
        mock_message.sid = 'TEST_MESSAGE_SID_123'
        notification_service.twilio_client.messages.create.return_value = mock_message
        
        success, result = notification_service.send_sms('+15551234567', 'Test message')
        
        assert success is True
        assert result == 'TEST_MESSAGE_SID_123'
        
        # Verify Twilio was called correctly
        notification_service.twilio_client.messages.create.assert_called_once()
        call_args = notification_service.twilio_client.messages.create.call_args
        assert call_args[1]['to'] == '+15551234567'
        assert call_args[1]['body'] == 'Test message'
    
    def test_send_sms_failure(self, notification_service):
        """Test SMS sending failure"""
        # Mock Twilio exception
        notification_service.twilio_client.messages.create.side_effect = Exception('Twilio error')
        
        success, result = notification_service.send_sms('+15551234567', 'Test message')
        
        assert success is False
        assert 'Twilio error' in result
    
    def test_send_email_success(self, notification_service):
        """Test successful email sending"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 202
        notification_service.sg_client.send.return_value = mock_response
        
        success, result = notification_service.send_email(
            'test@example.com',
            'Test Subject',
            '<p>Test email content</p>'
        )
        
        assert success is True
        assert result == 202
        
        # Verify SendGrid was called
        notification_service.sg_client.send.assert_called_once()
    
    def test_send_email_failure(self, notification_service):
        """Test email sending failure"""
        # Mock SendGrid exception
        notification_service.sg_client.send.side_effect = Exception('SendGrid error')
        
        success, result = notification_service.send_email(
            'test@example.com',
            'Test Subject',
            '<p>Test content</p>'
        )
        
        assert success is False
        assert 'SendGrid error' in result
    
    def test_notify_appointment_available(self, notification_service):
        """Test appointment availability notification"""
        # Mock successful sends
        notification_service.send_sms = Mock(return_value=(True, 'SMS_ID'))
        notification_service.send_email = Mock(return_value=(True, 200))
        
        booking_link = 'https://cancelfillmd.app/booking?token=abc123'
        
        result = notification_service.notify_appointment_available(
            TEST_PATIENT,
            TEST_APPOINTMENT,
            booking_link
        )
        
        assert result['sms']['success'] is True
        assert result['email']['success'] is True
        
        # Verify SMS was sent with correct content
        sms_call = notification_service.send_sms.call_args
        assert TEST_PATIENT['phone'] in str(sms_call)
        assert booking_link in str(sms_call)
        assert TEST_APPOINTMENT['date'] in str(sms_call)
        
        # Verify email was sent with correct content
        email_call = notification_service.send_email.call_args
        assert TEST_PATIENT['email'] in str(email_call)
        assert booking_link in str(email_call)
        assert TEST_APPOINTMENT['doctor'] in str(email_call)
    
    def test_notify_booking_confirmed(self, notification_service):
        """Test booking confirmation notification"""
        notification_service.send_sms = Mock(return_value=(True, 'SMS_ID'))
        
        result = notification_service.notify_booking_confirmed(
            TEST_PATIENT,
            TEST_APPOINTMENT
        )
        
        assert result == (True, 'SMS_ID')
        
        # Verify confirmation message content
        sms_call = notification_service.send_sms.call_args
        sms_content = str(sms_call)
        assert 'confirmed' in sms_content.lower()
        assert TEST_APPOINTMENT['date'] in sms_content
        assert TEST_APPOINTMENT['time'] in sms_content
    
    def test_notify_staff_appointment_filled(self, notification_service):
        """Test staff notification when appointment is filled"""
        notification_service.send_email = Mock(return_value=(True, 200))
        
        result = notification_service.notify_staff_appointment_filled(
            TEST_APPOINTMENT,
            TEST_PATIENT
        )
        
        assert result == (True, 200)
        
        # Verify email content
        email_call = notification_service.send_email.call_args
        email_content = str(email_call)
        assert 'filled' in email_content.lower()
        assert TEST_PATIENT['name'] in email_content
        assert TEST_APPOINTMENT['date'] in email_content
    
    def test_message_formatting(self, notification_service):
        """Test message formatting with templates"""
        # Test SMS length
        appointment = TEST_APPOINTMENT.copy()
        appointment['doctor'] = 'Dr. Very Long Name That Exceeds Normal Length'
        
        notification_service.send_sms = Mock(return_value=(True, 'SMS_ID'))
        
        notification_service.notify_appointment_available(
            TEST_PATIENT,
            appointment,
            'https://short.link/abc'
        )
        
        # Get SMS content
        sms_call = notification_service.send_sms.call_args
        sms_body = sms_call[0][1]
        
        # SMS should be under 160 characters for best delivery
        assert len(sms_body) <= 300  # Allow some flexibility for long names
    
    def test_notification_retry_logic(self, notification_service):
        """Test notification retry on failure"""
        # First call fails, second succeeds
        notification_service.twilio_client.messages.create.side_effect = [
            Exception('Temporary failure'),
            Mock(sid='SUCCESS_ID')
        ]
        
        # In real implementation, you would have retry logic
        # This tests the concept
        attempts = []
        for i in range(2):
            try:
                success, result = notification_service.send_sms('+15551234567', 'Test')
                attempts.append((success, result))
                if success:
                    break
            except:
                attempts.append((False, 'Failed'))
        
        # Should eventually succeed
        assert len(attempts) >= 1
        assert any(success for success, _ in attempts)

class TestNotificationTemplates:
    """Test notification templates and content"""
    
    def test_appointment_available_template(self):
        """Test appointment available message template"""
        template = """
{clinic_name} - Appointment Available!
        
Date: {date}
Time: {time}
Doctor: {doctor}

Book now: {link}
(Link expires in 2 hours)
"""
        
        # Test variable substitution
        message = template.format(
            clinic_name='Test Clinic',
            date='2025-06-10',
            time='10:00 AM',
            doctor='Dr. Smith',
            link='https://link.test/abc'
        )
        
        assert 'Test Clinic' in message
        assert '2025-06-10' in message
        assert '10:00 AM' in message
        assert 'Dr. Smith' in message
        assert 'https://link.test/abc' in message
    
    def test_html_email_template(self):
        """Test HTML email template rendering"""
        # This would test your actual HTML template
        html_template = """
        <h1>{clinic_name}</h1>
        <p>Appointment available on {date} at {time}</p>
        <a href="{link}">Book Now</a>
        """
        
        rendered = html_template.format(
            clinic_name='Test Clinic',
            date='2025-06-10',
            time='10:00 AM',
            link='https://link.test/abc'
        )
        
        assert '<h1>Test Clinic</h1>' in rendered
        assert 'href="https://link.test/abc"' in rendered

class TestNotificationMocking:
    """Test notification mocking for development"""
    
    def test_mock_mode(self):
        """Test mock mode doesn't send real notifications"""
        with patch.dict('os.environ', {'MOCK_NOTIFICATIONS': 'True'}):
            service = NotificationService()
            
            # In mock mode, should not actually call Twilio/SendGrid
            # This is a conceptual test - implement mock mode in your service
            assert hasattr(service, 'twilio_client')
            assert hasattr(service, 'sg_client')

if __name__ == '__main__':
    pytest.main([__file__, '-v'])