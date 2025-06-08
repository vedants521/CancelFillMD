# config.py
"""
Centralized configuration for CancelFillMD Pro
All app-wide settings and constants in one place
"""
import os
import streamlit as st
from datetime import time

# App Information
APP_NAME = "CancelFillMD Pro"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Smart Appointment Management System for Healthcare"

# Environment Detection
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development') == 'production'
DEMO_MODE = os.getenv('DEMO_MODE', 'True') == 'True'

# Firebase Configuration
FIREBASE_CONFIG = {
    'databaseURL': os.getenv('FIREBASE_URL', 'https://cancelfillmd-demo-default-rtdb.firebaseio.com/')
}

# Business Hours
BUSINESS_HOURS = {
    'monday': {'open': time(8, 0), 'close': time(17, 0)},
    'tuesday': {'open': time(8, 0), 'close': time(17, 0)},
    'wednesday': {'open': time(8, 0), 'close': time(17, 0)},
    'thursday': {'open': time(8, 0), 'close': time(17, 0)},
    'friday': {'open': time(8, 0), 'close': time(17, 0)},
    'saturday': {'open': time(9, 0), 'close': time(13, 0)},
    'sunday': None  # Closed
}

# Appointment Settings
APPOINTMENT_SETTINGS = {
    'min_duration_minutes': 15,
    'max_duration_minutes': 120,
    'default_duration_minutes': 60,
    'buffer_between_appointments': 0,  # minutes
    'max_advance_booking_days': 90,
    'min_cancellation_notice_hours': 24,
    'slot_intervals': [15, 30, 45, 60, 90, 120]  # Available duration options
}

# Waitlist Settings
WAITLIST_SETTINGS = {
    'max_entries_per_patient': 5,
    'max_preferred_dates': 10,
    'notification_limit_per_slot': 10,  # Max patients to notify for one slot
    'booking_link_expiry_hours': 2,
    'priority_score_factors': {
        'wait_time': 0.3,         # 30% weight for how long they've waited
        'failed_attempts': 0.2,    # 20% weight for previous unsuccessful attempts
        'date_flexibility': 0.2,   # 20% weight for date flexibility
        'time_flexibility': 0.2,   # 20% weight for time flexibility
        'loyalty': 0.1            # 10% weight for patient loyalty
    }
}

# Notification Settings
NOTIFICATION_SETTINGS = {
    'send_sms': True,
    'send_email': True,
    'sms_retry_attempts': 3,
    'email_retry_attempts': 3,
    'reminder_hours_before': [48, 24],  # Send reminders at these intervals
    'confirmation_required': True,
    'notification_templates': {
        'appointment_available': 'templates/appointment_available.html',
        'booking_confirmed': 'templates/booking_confirmed.html',
        'appointment_cancelled': 'templates/appointment_cancelled.html',
        'reminder': 'templates/reminder.html'
    }
}

# Security Settings
SECURITY_SETTINGS = {
    'session_timeout_minutes': 30,
    'max_login_attempts': 5,
    'lockout_duration_minutes': 15,
    'password_min_length': 8,
    'password_require_uppercase': True,
    'password_require_numbers': True,
    'password_require_special': True,
    'enable_2fa': False,  # Two-factor authentication
    'audit_logging': True,
    'encryption_enabled': True
}

# Demo Mode Settings
DEMO_SETTINGS = {
    'reset_interval_hours': 24,
    'demo_accounts': {
        'admin': {
            'username': 'demo_admin',
            'password': 'DemoPass2025',
            'role': 'Administrator',
            'full_name': 'Admin Demo'
        },
        'manager': {
            'username': 'demo_manager',
            'password': 'ManagerDemo2025',
            'role': 'Practice Manager',
            'full_name': 'Manager Demo'
        },
        'staff': {
            'username': 'demo_staff',
            'password': 'StaffDemo2025',
            'role': 'Staff Member',
            'full_name': 'Staff Demo'
        }
    },
    'demo_data_size': {
        'waitlist_patients': 75,
        'appointments_days': 14,
        'historical_days': 30
    }
}

# Analytics Settings
ANALYTICS_SETTINGS = {
    'default_date_range_days': 30,
    'comparison_periods': ['week', 'month', 'quarter', 'year'],
    'export_formats': ['pdf', 'excel', 'csv'],
    'kpi_targets': {
        'fill_rate': 80,          # Target 80% fill rate
        'fill_time_minutes': 30,   # Target 30 min fill time
        'utilization_rate': 85,    # Target 85% utilization
        'patient_satisfaction': 4.5 # Target 4.5/5 rating
    }
}

# UI Settings
UI_SETTINGS = {
    'theme': 'light',
    'primary_color': '#667eea',
    'secondary_color': '#764ba2',
    'success_color': '#10b981',
    'warning_color': '#f59e0b',
    'error_color': '#ef4444',
    'page_icon': '🏥',
    'sidebar_state': 'expanded',
    'show_footer': True,
    'enable_animations': True
}

# Specialty Configuration
SPECIALTIES = [
    {
        'name': 'Dermatology',
        'code': 'DERM',
        'default_duration': 30,
        'color': '#3b82f6'
    },
    {
        'name': 'Rheumatology',
        'code': 'RHEU',
        'default_duration': 45,
        'color': '#8b5cf6'
    },
    {
        'name': 'Cardiology',
        'code': 'CARD',
        'default_duration': 60,
        'color': '#ef4444'
    },
    {
        'name': 'Orthopedics',
        'code': 'ORTH',
        'default_duration': 45,
        'color': '#10b981'
    },
    {
        'name': 'General Practice',
        'code': 'GP',
        'default_duration': 30,
        'color': '#f59e0b'
    },
    {
        'name': 'Dentistry',
        'code': 'DENT',
        'default_duration': 60,
        'color': '#6366f1'
    }
]

# Pricing Configuration (for ROI calculations)
PRICING = {
    'currency': 'USD',
    'currency_symbol': '$',
    'average_appointment_values': {
        'Dermatology': 250,
        'Rheumatology': 300,
        'Cardiology': 350,
        'Orthopedics': 275,
        'General Practice': 150,
        'Dentistry': 200,
        'default': 250
    }
}

# Email Templates Base Configuration
EMAIL_CONFIG = {
    'from_name': os.getenv('CLINIC_NAME', 'CancelFillMD Clinic'),
    'from_email': os.getenv('SENDER_EMAIL', 'noreply@cancelfillmd.com'),
    'reply_to': os.getenv('REPLY_TO_EMAIL', 'support@cancelfillmd.com'),
    'footer_text': 'This is an automated message. Please do not reply directly to this email.',
    'unsubscribe_link': True,
    'include_logo': True
}

# SMS Configuration
SMS_CONFIG = {
    'from_number': os.getenv('TWILIO_PHONE_NUMBER', '+15555555555'),
    'max_length': 160,
    'include_clinic_name': True,
    'url_shortening': True,
    'opt_out_message': 'Reply STOP to unsubscribe'
}

# Rate Limiting Configuration
RATE_LIMITS = {
    'login_attempts': {'max': 5, 'window_minutes': 15},
    'password_reset': {'max': 3, 'window_minutes': 60},
    'api_calls': {'max': 100, 'window_minutes': 1},
    'bulk_operations': {'max': 10, 'window_minutes': 60},
    'notifications': {'max': 50, 'window_minutes': 1}
}

# Feature Flags
FEATURES = {
    'enable_waitlist': True,
    'enable_auto_fill': True,
    'enable_sms': True,
    'enable_email': True,
    'enable_analytics': True,
    'enable_export': True,
    'enable_patient_portal': True,
    'enable_two_way_sync': False,  # Future: sync with EMR
    'enable_payments': False,      # Future: payment processing
    'enable_telemedicine': False,  # Future: video appointments
    'enable_ai_predictions': False # Future: AI features
}

# Logging Configuration
LOGGING = {
    'level': 'INFO' if IS_PRODUCTION else 'DEBUG',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'cancelfillmd.log',
    'max_size_mb': 100,
    'backup_count': 5,
    'log_to_console': True,
    'log_to_file': IS_PRODUCTION
}

# Helper Functions
def get_specialty_info(specialty_name: str) -> dict:
    """Get configuration for a specific specialty"""
    for specialty in SPECIALTIES:
        if specialty['name'] == specialty_name:
            return specialty
    return {
        'name': specialty_name,
        'code': 'OTHER',
        'default_duration': 30,
        'color': '#6b7280'
    }

def get_appointment_value(specialty: str) -> float:
    """Get average appointment value for a specialty"""
    return PRICING['average_appointment_values'].get(
        specialty, 
        PRICING['average_appointment_values']['default']
    )

def is_business_hours(check_time: time, day_of_week: int) -> bool:
    """Check if a time falls within business hours"""
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_name = days[day_of_week]
    
    if day_name not in BUSINESS_HOURS or BUSINESS_HOURS[day_name] is None:
        return False
    
    hours = BUSINESS_HOURS[day_name]
    return hours['open'] <= check_time <= hours['close']

def get_feature_flag(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURES.get(feature_name, False)

# Load custom configuration from environment
def load_custom_config():
    """Load any custom configuration from environment variables"""
    custom_config = {}
    
    # Override any settings from environment variables
    for key, value in os.environ.items():
        if key.startswith('CANCELFILLMD_'):
            config_key = key.replace('CANCELFILLMD_', '').lower()
            custom_config[config_key] = value
    
    return custom_config

# Initialize custom config on import
CUSTOM_CONFIG = load_custom_config()