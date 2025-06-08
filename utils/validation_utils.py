# utils/validation_utils.py
"""
Validation utilities for form inputs and data integrity
"""
import re
from datetime import datetime, date, time
from typing import List, Tuple, Optional, Union

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class FormValidator:
    """Comprehensive form validation utilities"""
    
    @staticmethod
    def validate_required(value: any, field_name: str) -> bool:
        """Check if a required field has a value"""
        if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
            raise ValidationError(f"{field_name} is required")
        return True
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address format"""
        if not email:
            return False, "Email is required"
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        # Check for common typos
        common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        domain = email.split('@')[1].lower()
        
        # Suggest corrections for common typos
        typo_corrections = {
            'gmial.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com'
        }
        
        if domain in typo_corrections:
            return False, f"Did you mean {typo_corrections[domain]}?"
        
        return True, "Valid email"
    
    @staticmethod
    def validate_phone(phone: str, country: str = 'US') -> Tuple[bool, str]:
        """Validate phone number based on country"""
        if not phone:
            return False, "Phone number is required"
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        if country == 'US':
            # US phone validation
            if len(digits) == 10:
                # Format: XXX-XXX-XXXX
                return True, f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                # Format: 1-XXX-XXX-XXXX
                return True, f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            else:
                return False, "Phone must be 10 digits (or 11 with country code 1)"
        
        # Add more country validations as needed
        return False, "Unsupported country code"
    
    @staticmethod
    def validate_date(date_value: Union[str, date], 
                     min_date: Optional[date] = None,
                     max_date: Optional[date] = None) -> Tuple[bool, str]:
        """Validate date and check if within allowed range"""
        if isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"
        else:
            date_obj = date_value
        
        # Check minimum date
        if min_date and date_obj < min_date:
            return False, f"Date cannot be before {min_date.strftime('%Y-%m-%d')}"
        
        # Check maximum date
        if max_date and date_obj > max_date:
            return False, f"Date cannot be after {max_date.strftime('%Y-%m-%d')}"
        
        return True, "Valid date"
    
    @staticmethod
    def validate_time_slot(time_str: str, 
                          business_hours: Tuple[time, time] = (time(8, 0), time(17, 0))) -> Tuple[bool, str]:
        """Validate appointment time slot"""
        try:
            # Parse time string
            time_obj = datetime.strptime(time_str, '%I:%M %p').time()
        except ValueError:
            return False, "Invalid time format. Use HH:MM AM/PM"
        
        # Check business hours
        start_time, end_time = business_hours
        if time_obj < start_time or time_obj >= end_time:
            return False, f"Time must be between {start_time.strftime('%I:%M %p')} and {end_time.strftime('%I:%M %p')}"
        
        return True, "Valid time"
    
    @staticmethod
    def validate_name(name: str, min_length: int = 2, max_length: int = 50) -> Tuple[bool, str]:
        """Validate person's name"""
        if not name:
            return False, "Name is required"
        
        # Remove extra spaces
        name = ' '.join(name.split())
        
        if len(name) < min_length:
            return False, f"Name must be at least {min_length} characters"
        
        if len(name) > max_length:
            return False, f"Name must not exceed {max_length} characters"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, name.title()  # Return properly capitalized name
    
    @staticmethod
    def validate_insurance_info(provider: str, policy_number: str) -> Tuple[bool, str]:
        """Validate insurance information"""
        errors = []
        
        if not provider:
            errors.append("Insurance provider is required")
        elif len(provider) < 3:
            errors.append("Insurance provider name too short")
        
        if not policy_number:
            errors.append("Policy number is required")
        elif not re.match(r'^[A-Za-z0-9\-]+$', policy_number):
            errors.append("Policy number can only contain letters, numbers, and hyphens")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, "Valid insurance information"
    
    @staticmethod
    def validate_cancellation_reason(reason: str, min_length: int = 10) -> Tuple[bool, str]:
        """Validate cancellation reason"""
        if not reason or len(reason.strip()) < min_length:
            return False, f"Please provide a reason (at least {min_length} characters)"
        
        # Check for placeholder text
        placeholder_texts = ['test', 'asdf', 'xxx', '...', 'n/a']
        if reason.strip().lower() in placeholder_texts:
            return False, "Please provide a meaningful reason"
        
        return True, "Valid reason"

class DataValidator:
    """Validate data integrity and business rules"""
    
    @staticmethod
    def validate_appointment_availability(appointment_date: date, 
                                        appointment_time: str,
                                        existing_appointments: List[dict]) -> Tuple[bool, str]:
        """Check if appointment slot is available"""
        # Check if the slot is already booked
        for apt in existing_appointments:
            if (apt['date'] == appointment_date.strftime('%Y-%m-%d') and 
                apt['time'] == appointment_time and 
                apt['status'] in ['scheduled', 'filled']):
                return False, "This time slot is already booked"
        
        # Check if appointment is in the past
        appointment_datetime = datetime.combine(
            appointment_date,
            datetime.strptime(appointment_time, '%I:%M %p').time()
        )
        
        if appointment_datetime < datetime.now():
            return False, "Cannot book appointments in the past"
        
        return True, "Slot is available"
    
    @staticmethod
    def validate_waitlist_preferences(preferences: dict) -> Tuple[bool, str]:
        """Validate waitlist preferences"""
        errors = []
        
        # Check preferred dates
        if 'preferred_dates' not in preferences or not preferences['preferred_dates']:
            errors.append("At least one preferred date is required")
        else:
            # Validate each date
            for date_str in preferences['preferred_dates']:
                valid, msg = FormValidator.validate_date(
                    date_str, 
                    min_date=date.today()
                )
                if not valid:
                    errors.append(f"Invalid date {date_str}: {msg}")
        
        # Check time preferences
        if 'time_preferences' not in preferences or not preferences['time_preferences']:
            errors.append("At least one time preference is required")
        else:
            valid_times = ['morning', 'afternoon', 'evening', 'any']
            for time_pref in preferences['time_preferences']:
                if time_pref not in valid_times:
                    errors.append(f"Invalid time preference: {time_pref}")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, "Valid preferences"
    
    @staticmethod
    def validate_booking_eligibility(patient: dict, appointment: dict) -> Tuple[bool, str]:
        """Check if patient is eligible to book the appointment"""
        # Check specialty match
        if patient.get('specialty') != appointment.get('specialty'):
            return False, "Specialty mismatch"
        
        # Check if date is in patient's preferences
        apt_date = appointment.get('date')
        if apt_date not in patient.get('preferred_dates', []):
            return False, "Date not in patient's preferences"
        
        # Check time preference
        apt_time = datetime.strptime(appointment.get('time'), '%I:%M %p').time()
        patient_time_prefs = patient.get('time_preferences', [])
        
        if 'any' not in patient_time_prefs:
            if apt_time.hour < 12 and 'morning' not in patient_time_prefs:
                return False, "Morning appointment not preferred"
            elif 12 <= apt_time.hour < 17 and 'afternoon' not in patient_time_prefs:
                return False, "Afternoon appointment not preferred"
            elif apt_time.hour >= 17 and 'evening' not in patient_time_prefs:
                return False, "Evening appointment not preferred"
        
        return True, "Patient eligible for this appointment"

class BusinessRuleValidator:
    """Validate business-specific rules"""
    
    @staticmethod
    def validate_cancellation_window(appointment_datetime: datetime, 
                                   min_hours_notice: int = 24) -> Tuple[bool, str]:
        """Check if cancellation is within allowed window"""
        hours_until_appointment = (appointment_datetime - datetime.now()).total_seconds() / 3600
        
        if hours_until_appointment < min_hours_notice:
            return False, f"Cancellations require at least {min_hours_notice} hours notice"
        
        return True, "Cancellation allowed"
    
    @staticmethod
    def validate_max_waitlist_entries(patient_email: str, 
                                    current_waitlist: List[dict],
                                    max_entries: int = 5) -> Tuple[bool, str]:
        """Check if patient has exceeded max waitlist entries"""
        patient_entries = [entry for entry in current_waitlist 
                          if entry.get('email') == patient_email and entry.get('active', True)]
        
        if len(patient_entries) >= max_entries:
            return False, f"Maximum {max_entries} active waitlist entries allowed per patient"
        
        return True, "Can add to waitlist"
    
    @staticmethod
    def validate_appointment_duration(duration: str, 
                                    specialty: str) -> Tuple[bool, str]:
        """Validate appointment duration based on specialty"""
        duration_limits = {
            'Dermatology': {'min': 15, 'max': 60},
            'Rheumatology': {'min': 30, 'max': 90},
            'Cardiology': {'min': 20, 'max': 60},
            'General Practice': {'min': 15, 'max': 45}
        }
        
        try:
            duration_minutes = int(duration.split()[0])
        except:
            return False, "Invalid duration format"
        
        if specialty in duration_limits:
            limits = duration_limits[specialty]
            if duration_minutes < limits['min']:
                return False, f"Minimum duration for {specialty} is {limits['min']} minutes"
            if duration_minutes > limits['max']:
                return False, f"Maximum duration for {specialty} is {limits['max']} minutes"
        
        return True, "Valid duration"

# Sanitization utilities
class DataSanitizer:
    """Clean and sanitize user inputs"""
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Clean and format phone number"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Format as (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't format
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """Clean and properly capitalize name"""
        # Remove extra spaces
        name = ' '.join(name.split())
        
        # Proper capitalization
        return name.title()
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Clean and lowercase email"""
        return email.strip().lower()
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 500) -> str:
        """Clean general text input"""
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text