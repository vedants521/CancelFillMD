# API Reference - CancelFillMD Pro

## Table of Contents
1. [Overview](#overview)
2. [Database Structure](#database-structure)
3. [Core Functions](#core-functions)
4. [Utility Functions](#utility-functions)
5. [Page Components](#page-components)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

## Overview

CancelFillMD Pro is built with a modular architecture using Streamlit for the frontend and Firebase for the backend. This reference documents all major functions and their usage.

### Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│   Utils Layer   │────▶│    Firebase     │
│     (Pages)     │     │   (Business     │     │    Database     │
│                 │◀────│     Logic)      │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │  External APIs  │
                        │ Twilio/SendGrid │
                        └─────────────────┘
```

## Database Structure

### Firebase Realtime Database Schema

```javascript
{
  "appointments": {
    "<appointment_id>": {
      "date": "2024-06-10",
      "time": "10:00 AM",
      "doctor": "Dr. Smith",
      "specialty": "Dermatology",
      "duration": "1 hour",
      "status": "scheduled|cancelled|filled|available",
      "patient_name": "John Doe",
      "patient_email": "john@example.com",
      "patient_phone": "+15551234567",
      "created_at": "2024-06-01T10:00:00Z",
      "cancelled_at": "2024-06-09T14:30:00Z",
      "filled_at": "2024-06-09T14:45:00Z",
      "cancellation_reason": "Personal emergency"
    }
  },
  
  "waitlist": {
    "<waitlist_id>": {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+15559876543",
      "specialty": "Dermatology",
      "preferred_dates": ["2024-06-10", "2024-06-11"],
      "time_preferences": ["morning", "afternoon"],
      "created_at": "2024-06-01T09:00:00Z",
      "active": true,
      "notified_count": 2
    }
  },
  
  "users": {
    "<username>": {
      "username": "staff1",
      "password_hash": "hashed_password",
      "role": "Staff Member|Manager|Administrator",
      "full_name": "John Staff",
      "email": "staff@clinic.com",
      "created_at": "2024-01-01T08:00:00Z",
      "last_login": "2024-06-10T08:30:00Z"
    }
  },
  
  "notifications": {
    "<notification_id>": {
      "appointment_id": "apt_123",
      "patient_id": "patient_123",
      "type": "appointment_available",
      "sent_at": "2024-06-10T10:15:00Z",
      "sms_status": true,
      "email_status": true,
      "response_time_minutes": 15
    }
  },
  
  "booking_tokens": {
    "<token_id>": {
      "token": "secure_random_token",
      "appointment_id": "apt_123",
      "patient_id": "patient_123",
      "created_at": "2024-06-10T10:15:00Z",
      "expires_at": "2024-06-10T12:15:00Z",
      "used": false
    }
  }
}
```

## Core Functions

### FirebaseDB Class (`utils/firebase_utils.py`)

#### `__init__(self)`
Initialize Firebase connection.
```python
db = FirebaseDB()
```

#### `add_to_waitlist(patient_data: dict) -> str`
Add a patient to the waitlist.

**Parameters:**
- `patient_data`: Dictionary containing patient information

**Returns:**
- `str`: Unique waitlist ID

**Example:**
```python
patient_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+15551234567',
    'specialty': 'Dermatology',
    'preferred_dates': ['2024-06-10', '2024-06-11'],
    'time_preferences': ['morning', 'afternoon']
}
waitlist_id = db.add_to_waitlist(patient_data)
```

#### `get_waitlist(specialty: str = None, date: str = None) -> List[dict]`
Retrieve waitlist patients with optional filters.

**Parameters:**
- `specialty` (optional): Filter by medical specialty
- `date` (optional): Filter by preferred date

**Returns:**
- `List[dict]`: List of patient dictionaries

**Example:**
```python
# Get all Dermatology waitlist patients
derm_patients = db.get_waitlist(specialty='Dermatology')

# Get patients available on specific date
date_patients = db.get_waitlist(date='2024-06-10')
```

#### `add_appointment(appointment_data: dict) -> str`
Add a new appointment to the system.

**Parameters:**
- `appointment_data`: Dictionary with appointment details

**Returns:**
- `str`: Unique appointment ID

#### `update_appointment(appointment_id: str, updates: dict) -> None`
Update appointment information.

**Parameters:**
- `appointment_id`: ID of appointment to update
- `updates`: Dictionary of fields to update

**Example:**
```python
db.update_appointment('apt_123', {
    'status': 'cancelled',
    'cancelled_at': datetime.now().isoformat(),
    'cancellation_reason': 'Patient request'
})
```

#### `create_booking_link(appointment_id: str, patient_id: str) -> str`
Create secure booking link for patient.

**Parameters:**
- `appointment_id`: ID of available appointment
- `patient_id`: ID of waitlist patient

**Returns:**
- `str`: Secure booking URL

### NotificationService Class (`utils/notification_utils.py`)

#### `send_sms(to_number: str, message: str) -> Tuple[bool, str]`
Send SMS notification via Twilio.

**Parameters:**
- `to_number`: Recipient phone number (E.164 format)
- `message`: SMS message text

**Returns:**
- `Tuple[bool, str]`: (Success status, Message SID or error)

#### `send_email(to_email: str, subject: str, html_content: str) -> Tuple[bool, Union[int, str]]`
Send email notification via SendGrid.

**Parameters:**
- `to_email`: Recipient email address
- `subject`: Email subject line
- `html_content`: HTML email body

**Returns:**
- `Tuple[bool, Union[int, str]]`: (Success status, Status code or error)

#### `notify_appointment_available(patient: dict, appointment: dict, booking_link: str) -> dict`
Send appointment availability notification to patient.

**Parameters:**
- `patient`: Patient information dictionary
- `appointment`: Appointment details dictionary
- `booking_link`: Secure booking URL

**Returns:**
- `dict`: Results with SMS and email status

**Example:**
```python
notifier = NotificationService()
result = notifier.notify_appointment_available(
    patient={'name': 'John Doe', 'email': 'john@example.com', 'phone': '+15551234567'},
    appointment={'date': '2024-06-10', 'time': '10:00 AM', 'doctor': 'Dr. Smith'},
    booking_link='https://app.clinic.com/book?token=abc123'
)
```

## Utility Functions

### Validation (`utils/validation_utils.py`)

#### `FormValidator.validate_email(email: str) -> Tuple[bool, str]`
Validate email address format.

**Returns:**
- `Tuple[bool, str]`: (Is valid, Message)

#### `FormValidator.validate_phone(phone: str, country: str = 'US') -> Tuple[bool, str]`
Validate phone number.

**Returns:**
- `Tuple[bool, str]`: (Is valid, Formatted phone or error message)

#### `DataSanitizer.sanitize_phone(phone: str) -> str`
Clean and format phone number.

**Example:**
```python
formatted = DataSanitizer.sanitize_phone('555-123-4567')
# Returns: '(555) 123-4567'
```

### Security (`utils/security_utils.py`)

#### `SecurityManager.hash_password(password: str) -> str`
Hash password for storage.

#### `SecurityManager.verify_password(password: str, hashed: str) -> bool`
Verify password against hash.

#### `SecurityManager.generate_secure_link(length: int = 32) -> str`
Generate cryptographically secure random token.

#### `require_auth(role: str = None)`
Decorator for protecting pages.

**Example:**
```python
@require_auth(role='Administrator')
def admin_only_function():
    # This function requires admin role
    pass
```

### Analytics (`utils/analytics_utils.py`)

#### `MetricsCalculator.calculate_fill_rate(appointments: List[dict], date_range: Tuple[date, date] = None) -> float`
Calculate percentage of cancelled appointments that were filled.

**Parameters:**
- `appointments`: List of appointment dictionaries
- `date_range` (optional): Tuple of (start_date, end_date)

**Returns:**
- `float`: Fill rate percentage

#### `generate_analytics_summary(appointments: List[dict], date_range: Tuple[date, date] = None) -> dict`
Generate comprehensive analytics summary.

**Returns:**
- `dict`: Complete analytics with metrics, insights, and recommendations

## Page Components

### Main App (`app.py`)

Entry point for the application. Handles navigation and page routing.

```python
def main():
    st.set_page_config(
        page_title="CancelFillMD Pro",
        page_icon="🏥",
        layout="wide"
    )
    # Navigation logic
```

### Waitlist Form (`pages/waitlist_form.py`)

Patient-facing form for joining waitlist.

**Key Functions:**
- `validate_email()`: Check email format
- `validate_phone()`: Check phone format
- Form submission handler

### Staff Dashboard (`pages/staff_dashboard.py`)

Main interface for staff operations.

**Key Components:**
- Authentication check
- Real-time metrics display
- Appointment management
- Waitlist view

### Analytics Dashboard (`pages/analytics_dashboard.py`)

Comprehensive analytics and reporting.

**Key Functions:**
- `calculate_metrics()`: Compute KPIs
- `generate_charts()`: Create visualizations
- `export_report()`: Generate PDF/Excel reports

## Configuration

### Config Module (`config.py`)

Central configuration for the application.

```python
# Key settings
APP_NAME = "CancelFillMD Pro"
BUSINESS_HOURS = {
    'monday': {'open': time(8, 0), 'close': time(17, 0)},
    # ...
}

APPOINTMENT_SETTINGS = {
    'min_duration_minutes': 15,
    'max_duration_minutes': 120,
    'min_cancellation_notice_hours': 24
}

NOTIFICATION_SETTINGS = {
    'send_sms': True,
    'send_email': True,
    'booking_link_expiry_hours': 2
}
```

### Environment Variables (`.env`)

Required environment variables:
```bash
# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+15551234567

# SendGrid
SENDGRID_API_KEY=your_api_key
SENDER_EMAIL=noreply@clinic.com

# Security
JWT_SECRET_KEY=random_secret_key
```

## Error Handling

### Custom Exceptions

```python
class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class BookingError(Exception):
    """Raised when booking process fails"""
    pass

class NotificationError(Exception):
    """Raised when notification sending fails"""
    pass
```

### Error Handling Patterns

```python
# Safe database operation
try:
    result = db.add_appointment(appointment_data)
except Exception as e:
    logger.error(f"Failed to add appointment: {e}")
    st.error("Unable to save appointment. Please try again.")
    return None

# Notification with fallback
try:
    sms_result = notifier.send_sms(phone, message)
except Exception as e:
    logger.warning(f"SMS failed, trying email: {e}")
    email_result = notifier.send_email(email, subject, message)
```

## Examples

### Example 1: Complete Cancellation Flow

```python
# 1. Cancel appointment
def process_cancellation(appointment_id: str):
    db = FirebaseDB()
    notifier = NotificationService()
    
    # Update appointment status
    db.update_appointment(appointment_id, {
        'status': 'cancelled',
        'cancelled_at': datetime.now().isoformat()
    })
    
    # Get appointment details
    appointment = db.get_appointment_by_id(appointment_id)
    
    # Find matching waitlist patients
    matches = db.get_waitlist(
        specialty=appointment['specialty'],
        date=appointment['date']
    )
    
    # Notify top matches
    for patient in matches[:10]:
        booking_link = db.create_booking_link(appointment_id, patient['id'])
        notifier.notify_appointment_available(patient, appointment, booking_link)
```

### Example 2: Custom Report Generation

```python
from utils.export_utils import ReportGenerator
from utils.analytics_utils import generate_analytics_summary

def create_monthly_report():
    # Get data
    db = FirebaseDB()
    appointments = db.get_appointments_in_range(
        start_date=date.today().replace(day=1),
        end_date=date.today()
    )
    
    # Generate analytics
    analytics = generate_analytics_summary(appointments)
    
    # Create PDF
    report_gen = ReportGenerator()
    pdf_bytes = report_gen.generate_pdf_report(analytics, 'monthly')
    
    # Offer download
    st.download_button(
        label="Download Monthly Report",
        data=pdf_bytes,
        file_name=f"monthly_report_{date.today().strftime('%Y%m')}.pdf",
        mime="application/pdf"
    )
```

### Example 3: Bulk Waitlist Import

```python
import pandas as pd

def import_waitlist_from_csv(csv_file):
    db = FirebaseDB()
    df = pd.read_csv(csv_file)
    
    success_count = 0
    error_count = 0
    
    for _, row in df.iterrows():
        try:
            patient_data = {
                'name': row['Name'],
                'email': DataSanitizer.sanitize_email(row['Email']),
                'phone': DataSanitizer.sanitize_phone(row['Phone']),
                'specialty': row['Specialty'],
                'preferred_dates': row['Preferred_Dates'].split(';'),
                'time_preferences': row['Time_Preferences'].split(';')
            }
            
            # Validate
            valid_email, _ = FormValidator.validate_email(patient_data['email'])
            valid_phone, _ = FormValidator.validate_phone(patient_data['phone'])
            
            if valid_email and valid_phone:
                db.add_to_waitlist(patient_data)
                success_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            logger.error(f"Failed to import row: {e}")
            error_count += 1
    
    return success_count, error_count
```

## Testing

### Unit Test Example

```python
import pytest
from utils.validation_utils import FormValidator

def test_email_validation():
    # Valid emails
    assert FormValidator.validate_email('user@example.com')[0] == True
    
    # Invalid emails
    assert FormValidator.validate_email('invalid.email')[0] == False
    assert FormValidator.validate_email('')[0] == False
    
    # Typo detection
    valid, msg = FormValidator.validate_email('user@gmial.com')
    assert valid == False
    assert 'gmail.com' in msg
```

### Integration Test Example

```python
def test_complete_booking_flow():
    db = FirebaseDB()
    
    # Add test patient
    patient_id = db.add_to_waitlist({
        'name': 'Test Patient',
        'email': 'test@example.com',
        'phone': '+15551234567',
        'specialty': 'Dermatology',
        'preferred_dates': ['2024-06-10']
    })
    
    # Add test appointment
    apt_id = db.add_appointment({
        'date': '2024-06-10',
        'time': '10:00 AM',
        'doctor': 'Dr. Test',
        'specialty': 'Dermatology',
        'status': 'available'
    })
    
    # Create booking link
    link = db.create_booking_link(apt_id, patient_id)
    assert 'token=' in link
    
    # Cleanup
    db.db.reference(f'waitlist/{patient_id}').delete()
    db.db.reference(f'appointments/{apt_id}').delete()
```

---

## API Best Practices

1. **Always validate input**: Use validation utilities before processing
2. **Handle errors gracefully**: Never expose raw errors to users
3. **Use transactions**: For critical operations that must be atomic
4. **Cache expensive operations**: Use `@st.cache_data` for analytics
5. **Log important events**: For audit trail and debugging
6. **Test edge cases**: Empty lists, None values, network failures

For more examples and advanced usage, see the source code or contact support@cancelfillmd.com