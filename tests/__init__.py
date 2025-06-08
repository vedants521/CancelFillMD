# tests/__init__.py
"""
Test suite for CancelFillMD Pro
Run tests with: python -m pytest tests/
"""

import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test configuration
TEST_CONFIG = {
    'use_test_database': True,
    'test_database_url': 'https://cancelfillmd-test-default-rtdb.firebaseio.com/',
    'mock_notifications': True,  # Don't send real SMS/emails during tests
    'test_timeout': 30,  # seconds
}

# Test data constants
TEST_PATIENT = {
    'name': 'Test Patient',
    'email': 'test@example.com',
    'phone': '+15551234567',
    'specialty': 'Dermatology',
    'preferred_dates': ['2025-06-10', '2025-06-11'],
    'time_preferences': ['morning', 'afternoon']
}

TEST_APPOINTMENT = {
    'date': '2025-06-10',
    'time': '10:00 AM',
    'doctor': 'Dr. Test',
    'specialty': 'Dermatology',
    'status': 'scheduled',
    'patient_name': 'Test Patient',
    'patient_email': 'test@example.com',
    'patient_phone': '+15551234567'
}

# Shared test fixtures and utilities can be added here