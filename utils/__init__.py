# utils/__init__.py
"""
Utils package for CancelFillMD Pro
Provides easy imports for all utility functions
"""

# Firebase utilities
from .firebase_utils import FirebaseDB

# Notification utilities  
from .notification_utils import NotificationService

# Security utilities
from .security_utils import (
    SecurityManager,
    require_auth,
    init_session_state,
    login_user,
    logout_user,
    check_session_timeout,
    RateLimiter
)

# Validation utilities
from .validation_utils import (
    FormValidator,
    DataSanitizer,
    ValidationError,
    DataValidator,
    BusinessRuleValidator
)

# Analytics utilities
from .analytics_utils import (
    MetricsCalculator,
    TrendAnalyzer,
    PerformanceScorer,
    InsightGenerator,
    BenchmarkAnalyzer,
    generate_analytics_summary
)

# Export utilities
from .export_utils import (
    ReportGenerator,
    EmailReportBuilder
)

# Demo utilities
from .demo_utils import (
    DemoDataGenerator,
    DemoScenarios,
    reset_demo_database,
    create_demo_snapshot,
    restore_demo_snapshot
)

# Version
__version__ = '1.0.0'
__author__ = 'CancelFillMD Pro Team'

# Define what should be imported when using "from utils import *"
__all__ = [
    # Firebase utilities
    'FirebaseDB',
    
    # Notification utilities
    'NotificationService',
    
    # Security utilities
    'SecurityManager',
    'require_auth',
    'init_session_state',
    'login_user',
    'logout_user',
    'check_session_timeout',
    'RateLimiter',
    
    # Validation utilities
    'FormValidator',
    'DataSanitizer',
    'ValidationError',
    'DataValidator',
    'BusinessRuleValidator',
    
    # Analytics utilities
    'MetricsCalculator',
    'TrendAnalyzer',
    'PerformanceScorer',
    'InsightGenerator',
    'BenchmarkAnalyzer',
    'generate_analytics_summary',
    
    # Export utilities
    'ReportGenerator',
    'EmailReportBuilder',
    
    # Demo utilities
    'DemoDataGenerator',
    'DemoScenarios',
    'reset_demo_database',
    'create_demo_snapshot',
    'restore_demo_snapshot'
]

# Check environment on import
def check_environment():
    """Check if all required environment variables are set"""
    import os
    
    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_PHONE_NUMBER',
        'SENDGRID_API_KEY',
        'SENDER_EMAIL'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            # In development/demo mode, we can skip these checks
            if os.getenv('ENVIRONMENT') == 'development' or os.getenv('DEMO_MODE') == 'True':
                continue
            missing.append(var)
    
    if missing:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing)}")
        print("Some features may not work properly.")
    
    return len(missing) == 0

# Run environment check when package is imported
check_environment()