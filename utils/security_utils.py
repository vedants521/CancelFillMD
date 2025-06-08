# utils/security_utils.py
"""
Security utilities for authentication, authorization, and data protection
"""
import hashlib
import secrets
import streamlit as st
from datetime import datetime, timedelta
import jwt
import re
from functools import wraps
import os

# Secret key for JWT tokens (in production, use environment variable)
try:
    SECRET_KEY = st.secrets.get('JWT_SECRET_KEY', 'your-secret-key-change-this')
except:
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')

class SecurityManager:
    """Handles all security-related operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return SecurityManager.hash_password(password) == hashed
    
    @staticmethod
    def generate_token(user_id: str, expiry_hours: int = 24) -> str:
        """Generate a JWT token for user authentication"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return {'valid': True, 'user_id': payload['user_id']}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    @staticmethod
    def generate_secure_link(length: int = 32) -> str:
        """Generate a secure random link for booking confirmations"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove any potential HTML/script tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove any potential SQL injection attempts
        text = text.replace("'", "''")
        text = text.replace('"', '""')
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (US format)"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        # Check if it's 10 or 11 digits (with or without country code)
        return len(digits) in [10, 11]
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
        """Mask sensitive data like phone numbers or emails"""
        if len(data) <= visible_chars:
            return mask_char * len(data)
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)

# Authentication decorator for Streamlit pages
def require_auth(role=None):
    """Decorator to require authentication for certain pages"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'authenticated' not in st.session_state or not st.session_state.authenticated:
                st.error("🔒 Please login to access this page")
                st.stop()
            
            if role and st.session_state.get('user_role') != role:
                st.error(f"🚫 Access denied. Required role: {role}")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Session management functions
def init_session_state():
    """Initialize session state variables for security"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None

def login_user(user_id: str, role: str):
    """Log in a user and set session state"""
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.user_role = role
    st.session_state.login_time = datetime.now()
    st.session_state.session_token = SecurityManager.generate_token(user_id)

def logout_user():
    """Log out a user and clear session state"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.login_time = None
    st.session_state.session_token = None

def check_session_timeout(timeout_minutes: int = 30):
    """Check if the session has timed out"""
    if st.session_state.login_time:
        elapsed = datetime.now() - st.session_state.login_time
        if elapsed > timedelta(minutes=timeout_minutes):
            logout_user()
            st.warning("⏱️ Session timed out. Please login again.")
            return True
    return False

# Rate limiting for API calls
class RateLimiter:
    """Simple rate limiter for preventing abuse"""
    
    def __init__(self):
        if 'rate_limits' not in st.session_state:
            st.session_state.rate_limits = {}
    
    def check_limit(self, action: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Check if an action has exceeded rate limits"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if action not in st.session_state.rate_limits:
            st.session_state.rate_limits[action] = []
        
        # Remove old attempts outside the window
        st.session_state.rate_limits[action] = [
            attempt for attempt in st.session_state.rate_limits[action]
            if attempt > window_start
        ]
        
        # Check if limit exceeded
        if len(st.session_state.rate_limits[action]) >= max_attempts:
            return False
        
        # Record this attempt
        st.session_state.rate_limits[action].append(now)
        return True

# HIPAA compliance helpers
class HIPAACompliance:
    """Helper functions for HIPAA compliance"""
    
    @staticmethod
    def log_access(user_id: str, patient_id: str, action: str):
        """Log access to patient data for audit trail"""
        # In production, this would write to a secure audit log
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'patient_id': patient_id,
            'action': action,
            'ip_address': 'Not available in Streamlit'  # Would get from request in production
        }
        # For demo, just print (in production, write to secure log)
        print(f"AUDIT LOG: {log_entry}")
        return log_entry
    
    @staticmethod
    def encrypt_pii(data: str) -> str:
        """Encrypt personally identifiable information"""
        # In production, use proper encryption like AES
        # This is a simple example for demo
        return hashlib.sha256(data.encode()).hexdigest()[:16] + "..."
    
    @staticmethod
    def redact_pii_for_display(text: str) -> str:
        """Redact PII from text for display purposes"""
        # Redact email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REDACTED]', text)
        # Redact phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE REDACTED]', text)
        # Redact SSN-like patterns
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN REDACTED]', text)
        return text

# Password policy enforcement
class PasswordPolicy:
    """Enforce password policies for security"""
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password against security policy"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common passwords (in production, use a comprehensive list)
        common_passwords = ['password', '12345678', 'qwerty', 'admin123', 'letmein']
        if password.lower() in common_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, "Password is strong"
    
    @staticmethod
    def generate_strong_password(length: int = 12) -> str:
        """Generate a strong random password"""
        import string
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

# Two-factor authentication helpers
class TwoFactorAuth:
    """Simple 2FA implementation"""
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP"""
        return str(secrets.randbelow(900000) + 100000)
    
    @staticmethod
    def send_otp(phone: str, otp: str) -> bool:
        """Send OTP via SMS (placeholder for demo)"""
        # In production, this would actually send SMS
        print(f"DEBUG: OTP {otp} would be sent to {phone}")
        # Store OTP in session for verification
        st.session_state.pending_otp = otp
        st.session_state.otp_timestamp = datetime.now()
        return True
    
    @staticmethod
    def verify_otp(user_otp: str) -> bool:
        """Verify the OTP entered by user"""
        if 'pending_otp' not in st.session_state:
            return False
        
        # Check if OTP is expired (5 minutes)
        if datetime.now() - st.session_state.otp_timestamp > timedelta(minutes=5):
            return False
        
        # Verify OTP
        if user_otp == st.session_state.pending_otp:
            # Clear OTP from session
            del st.session_state.pending_otp
            del st.session_state.otp_timestamp
            return True
        
        return False