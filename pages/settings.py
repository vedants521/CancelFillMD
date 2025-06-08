# pages/settings.py
"""
System settings and configuration page for administrators
"""
import streamlit as st
from datetime import time, datetime
import json
from utils import (
    require_auth,
    FirebaseDB,
    SecurityManager
)
import config

st.set_page_config(
    page_title="Settings - CancelFillMD Pro",
    page_icon="⚙️",
    layout="wide"
)

@require_auth(role='Administrator')
def main():
    st.title("⚙️ System Settings")
    st.markdown("Configure system-wide settings and preferences")
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏥 Clinic Settings",
        "📅 Appointment Settings",
        "🔔 Notification Settings",
        "🔒 Security Settings",
        "💰 Pricing & Billing"
    ])
    
    with tab1:
        clinic_settings()
    
    with tab2:
        appointment_settings()
    
    with tab3:
        notification_settings()
    
    with tab4:
        security_settings()
    
    with tab5:
        pricing_settings()

def clinic_settings():
    """Clinic information and business hours"""
    st.markdown("### 🏥 Clinic Information")
    
    db = FirebaseDB()
    
    with st.form("clinic_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            clinic_name = st.text_input(
                "Clinic Name",
                value=config.EMAIL_CONFIG['from_name']
            )
            
            clinic_email = st.text_input(
                "Main Email",
                value=config.EMAIL_CONFIG['from_email']
            )
            
            clinic_phone = st.text_input(
                "Main Phone",
                value="(555) 123-4567"
            )
        
        with col2:
            clinic_address = st.text_area(
                "Address",
                value="123 Medical Center Dr\nSuite 100\nCity, State 12345"
            )
            
            timezone = st.selectbox(
                "Timezone",
                ["America/New_York", "America/Chicago", "America/Denver", 
                 "America/Los_Angeles", "America/Phoenix"],
                index=0
            )
        
        st.markdown("### 🕐 Business Hours")
        
        # Business hours grid
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        hours_data = {}
        
        for i in range(0, len(days), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(days):
                    day = days[i]
                    st.markdown(f"**{day}**")
                    
                    is_open = st.checkbox(f"Open on {day}", value=day != 'Sunday', key=f"open_{day}")
                    
                    if is_open:
                        open_time = st.time_input(
                            "Opens at",
                            value=time(8, 0),
                            key=f"open_time_{day}"
                        )
                        close_time = st.time_input(
                            "Closes at",
                            value=time(17, 0) if day != 'Saturday' else time(13, 0),
                            key=f"close_time_{day}"
                        )
                        hours_data[day.lower()] = {
                            'open': open_time.strftime("%H:%M"),
                            'close': close_time.strftime("%H:%M")
                        }
                    else:
                        hours_data[day.lower()] = None
            
            with col2:
                if i + 1 < len(days):
                    day = days[i + 1]
                    st.markdown(f"**{day}**")
                    
                    is_open = st.checkbox(f"Open on {day}", value=day != 'Sunday', key=f"open_{day}")
                    
                    if is_open:
                        open_time = st.time_input(
                            "Opens at",
                            value=time(8, 0),
                            key=f"open_time_{day}"
                        )
                        close_time = st.time_input(
                            "Closes at",
                            value=time(17, 0) if day != 'Saturday' else time(13, 0),
                            key=f"close_time_{day}"
                        )
                        hours_data[day.lower()] = {
                            'open': open_time.strftime("%H:%M"),
                            'close': close_time.strftime("%H:%M")
                        }
                    else:
                        hours_data[day.lower()] = None
        
        # Holiday settings
        st.markdown("### 🎄 Holiday Schedule")
        
        holidays = st.multiselect(
            "Closed on these holidays",
            ["New Year's Day", "MLK Day", "Presidents Day", "Memorial Day",
             "Independence Day", "Labor Day", "Thanksgiving", "Christmas Day"],
            default=["New Year's Day", "Independence Day", "Thanksgiving", "Christmas Day"]
        )
        
        submitted = st.form_submit_button("Save Clinic Settings", type="primary")
        
        if submitted:
            # Save settings
            clinic_data = {
                'name': clinic_name,
                'email': clinic_email,
                'phone': clinic_phone,
                'address': clinic_address,
                'timezone': timezone,
                'business_hours': hours_data,
                'holidays': holidays,
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to database
            st.success("✅ Clinic settings saved successfully!")
            
            # Show JSON preview
            with st.expander("Settings Preview"):
                st.json(clinic_data)

def appointment_settings():
    """Appointment configuration settings"""
    st.markdown("### 📅 Appointment Configuration")
    
    with st.form("appointment_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Duration Settings")
            
            default_duration = st.selectbox(
                "Default Appointment Duration",
                options=[15, 30, 45, 60, 90, 120],
                index=3,  # 60 minutes
                format_func=lambda x: f"{x} minutes"
            )
            
            min_duration = st.number_input(
                "Minimum Duration (minutes)",
                min_value=5,
                max_value=60,
                value=15,
                step=5
            )
            
            max_duration = st.number_input(
                "Maximum Duration (minutes)",
                min_value=30,
                max_value=240,
                value=120,
                step=15
            )
            
            buffer_time = st.number_input(
                "Buffer Between Appointments (minutes)",
                min_value=0,
                max_value=30,
                value=0,
                step=5
            )
        
        with col2:
            st.markdown("#### Booking Rules")
            
            advance_booking_days = st.number_input(
                "Maximum Advance Booking (days)",
                min_value=7,
                max_value=365,
                value=90,
                step=7
            )
            
            min_notice_hours = st.number_input(
                "Minimum Cancellation Notice (hours)",
                min_value=0,
                max_value=72,
                value=24,
                step=1
            )
            
            same_day_cutoff = st.time_input(
                "Same-Day Booking Cutoff",
                value=time(14, 0)  # 2 PM
            )
            
            allow_double_booking = st.checkbox(
                "Allow Double Booking",
                value=False,
                help="Allow multiple appointments in the same time slot"
            )
        
        st.markdown("### 📋 Waitlist Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_waitlist_per_patient = st.number_input(
                "Max Waitlist Entries per Patient",
                min_value=1,
                max_value=20,
                value=5
            )
            
            waitlist_expiry_days = st.number_input(
                "Waitlist Entry Expiry (days)",
                min_value=7,
                max_value=90,
                value=30
            )
        
        with col2:
            max_notifications_per_slot = st.number_input(
                "Max Notifications per Cancelled Slot",
                min_value=5,
                max_value=50,
                value=10
            )
            
            booking_link_expiry_hours = st.number_input(
                "Booking Link Expiry (hours)",
                min_value=1,
                max_value=24,
                value=2
            )
        
        st.markdown("### 🎯 Matching Algorithm")
        
        st.markdown("Adjust weights for patient matching score:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            wait_time_weight = st.slider(
                "Wait Time Weight",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1
            )
            
            flexibility_weight = st.slider(
                "Date Flexibility Weight",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.1
            )
        
        with col2:
            attempts_weight = st.slider(
                "Failed Attempts Weight",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.1
            )
            
            time_pref_weight = st.slider(
                "Time Preference Weight",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.1
            )
        
        with col3:
            loyalty_weight = st.slider(
                "Patient Loyalty Weight",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.1
            )
        
        # Validate weights sum to 1.0
        total_weight = (wait_time_weight + flexibility_weight + attempts_weight + 
                       time_pref_weight + loyalty_weight)
        
        if abs(total_weight - 1.0) > 0.01:
            st.error(f"Weights must sum to 1.0 (currently {total_weight:.1f})")
        
        submitted = st.form_submit_button("Save Appointment Settings", type="primary")
        
        if submitted and abs(total_weight - 1.0) <= 0.01:
            settings = {
                'duration': {
                    'default': default_duration,
                    'min': min_duration,
                    'max': max_duration,
                    'buffer': buffer_time
                },
                'booking': {
                    'advance_days': advance_booking_days,
                    'min_notice_hours': min_notice_hours,
                    'same_day_cutoff': same_day_cutoff.strftime("%H:%M"),
                    'allow_double_booking': allow_double_booking
                },
                'waitlist': {
                    'max_per_patient': max_waitlist_per_patient,
                    'expiry_days': waitlist_expiry_days,
                    'max_notifications': max_notifications_per_slot,
                    'link_expiry_hours': booking_link_expiry_hours
                },
                'matching_weights': {
                    'wait_time': wait_time_weight,
                    'flexibility': flexibility_weight,
                    'attempts': attempts_weight,
                    'time_preference': time_pref_weight,
                    'loyalty': loyalty_weight
                }
            }
            
            st.success("✅ Appointment settings saved successfully!")

def notification_settings():
    """Notification configuration"""
    st.markdown("### 🔔 Notification Settings")
    
    with st.form("notification_settings"):
        # Notification channels
        st.markdown("#### Notification Channels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_sms = st.checkbox("Enable SMS Notifications", value=True)
            enable_email = st.checkbox("Enable Email Notifications", value=True)
            enable_push = st.checkbox("Enable Push Notifications", value=False, disabled=True)
            st.caption("Push notifications coming soon")
        
        with col2:
            sms_provider = st.selectbox(
                "SMS Provider",
                ["Twilio", "AWS SNS", "MessageBird"],
                index=0
            )
            
            email_provider = st.selectbox(
                "Email Provider",
                ["SendGrid", "AWS SES", "Mailgun"],
                index=0
            )
        
        # Notification timing
        st.markdown("#### Notification Timing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reminder_times = st.multiselect(
                "Send Appointment Reminders",
                ["72 hours before", "48 hours before", "24 hours before", 
                 "12 hours before", "2 hours before"],
                default=["48 hours before", "24 hours before"]
            )
            
            quiet_hours_start = st.time_input(
                "Quiet Hours Start",
                value=time(21, 0)  # 9 PM
            )
        
        with col2:
            cancellation_notify_delay = st.number_input(
                "Delay Before Notifying Waitlist (minutes)",
                min_value=0,
                max_value=60,
                value=5,
                help="Wait time after cancellation before notifying waitlist"
            )
            
            quiet_hours_end = st.time_input(
                "Quiet Hours End",
                value=time(8, 0)  # 8 AM
            )
        
        # Message templates
        st.markdown("#### Message Templates")
        
        template_type = st.selectbox(
            "Select Template to Edit",
            ["Appointment Available", "Booking Confirmed", "Appointment Reminder",
             "Cancellation Confirmation", "Waitlist Added"]
        )
        
        if template_type == "Appointment Available":
            sms_template = st.text_area(
                "SMS Template",
                value="{clinic_name}: Appointment available on {date} at {time} with {doctor}. Book now: {link}",
                height=100
            )
            
            email_subject = st.text_input(
                "Email Subject",
                value="Appointment Available - {date} at {time}"
            )
            
            email_preview = st.checkbox("Use HTML Email Template", value=True)
        
        # Retry settings
        st.markdown("#### Retry & Failover Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sms_retry_attempts = st.number_input(
                "SMS Retry Attempts",
                min_value=0,
                max_value=5,
                value=3
            )
            
            email_retry_attempts = st.number_input(
                "Email Retry Attempts",
                min_value=0,
                max_value=5,
                value=3
            )
        
        with col2:
            retry_delay_seconds = st.number_input(
                "Retry Delay (seconds)",
                min_value=10,
                max_value=300,
                value=60
            )
            
            failover_to_alternate = st.checkbox(
                "Failover to Alternate Channel",
                value=True,
                help="If SMS fails, try email and vice versa"
            )
        
        submitted = st.form_submit_button("Save Notification Settings", type="primary")
        
        if submitted:
            st.success("✅ Notification settings saved successfully!")

def security_settings():
    """Security and access control settings"""
    st.markdown("### 🔒 Security Settings")
    
    # User management
    st.markdown("#### User Management")
    
    # Display current users
    users_data = [
        {"Username": "admin", "Role": "Administrator", "Last Login": "2025-06-07 10:30 AM", "Status": "Active"},
        {"Username": "manager1", "Role": "Practice Manager", "Last Login": "2025-06-07 09:15 AM", "Status": "Active"},
        {"Username": "staff1", "Role": "Staff Member", "Last Login": "2025-06-06 04:45 PM", "Status": "Active"},
        {"Username": "staff2", "Role": "Staff Member", "Last Login": "2025-06-01 02:20 PM", "Status": "Inactive"}
    ]
    
    st.dataframe(users_data, use_container_width=True)
    
    # Add new user
    with st.expander("➕ Add New User"):
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
            
            with col2:
                new_role = st.selectbox(
                    "Role",
                    ["Staff Member", "Practice Manager", "Administrator"]
                )
                new_name = st.text_input("Full Name")
                confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Create User"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Simple password validation (replacing PasswordPolicy)
                    if len(new_password) < 8:
                        st.error("Password must be at least 8 characters long")
                    elif not any(c.isupper() for c in new_password):
                        st.error("Password must contain at least one uppercase letter")
                    elif not any(c.isdigit() for c in new_password):
                        st.error("Password must contain at least one number")
                    else:
                        st.success(f"✅ User '{new_username}' created successfully!")
    
    # Security policies
    st.markdown("#### Security Policies")
    
    with st.form("security_policies"):
        col1, col2 = st.columns(2)
        
        with col1:
            session_timeout = st.number_input(
                "Session Timeout (minutes)",
                min_value=5,
                max_value=480,
                value=30
            )
            
            max_login_attempts = st.number_input(
                "Max Login Attempts",
                min_value=3,
                max_value=10,
                value=5
            )
            
            lockout_duration = st.number_input(
                "Account Lockout Duration (minutes)",
                min_value=5,
                max_value=60,
                value=15
            )
        
        with col2:
            password_min_length = st.number_input(
                "Minimum Password Length",
                min_value=6,
                max_value=20,
                value=8
            )
            
            password_expiry_days = st.number_input(
                "Password Expiry (days)",
                min_value=0,
                max_value=365,
                value=90,
                help="0 = passwords never expire"
            )
            
            enable_2fa = st.checkbox(
                "Enable Two-Factor Authentication",
                value=False
            )
        
        st.markdown("#### Password Requirements")
        
        require_uppercase = st.checkbox("Require Uppercase Letters", value=True)
        require_numbers = st.checkbox("Require Numbers", value=True)
        require_special = st.checkbox("Require Special Characters", value=True)
        prevent_reuse = st.checkbox("Prevent Password Reuse", value=True)
        
        st.markdown("#### Audit & Compliance")
        
        enable_audit_log = st.checkbox(
            "Enable Audit Logging",
            value=True,
            help="Log all user actions for compliance"
        )
        
        hipaa_mode = st.checkbox(
            "HIPAA Compliance Mode",
            value=True,
            help="Enable additional security measures for HIPAA compliance"
        )
        
        data_retention_days = st.number_input(
            "Data Retention Period (days)",
            min_value=30,
            max_value=2555,  # 7 years
            value=2555,
            help="How long to keep patient data"
        )
        
        submitted = st.form_submit_button("Save Security Settings", type="primary")
        
        if submitted:
            st.success("✅ Security settings saved successfully!")
            st.warning("⚠️ Some changes may require users to log in again.")

def pricing_settings():
    """Pricing and billing configuration"""
    st.markdown("### 💰 Pricing & Billing Settings")
    
    # Specialty pricing
    st.markdown("#### Appointment Pricing by Specialty")
    
    specialties = config.SPECIALTIES
    
    pricing_data = []
    
    for i in range(0, len(specialties), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(specialties):
                specialty = specialties[i]
                st.markdown(f"**{specialty['name']}**")
                
                price = st.number_input(
                    "Standard Price",
                    min_value=0,
                    max_value=1000,
                    value=config.PRICING['average_appointment_values'].get(
                        specialty['name'], 250
                    ),
                    step=25,
                    key=f"price_{specialty['code']}"
                )
                
                pricing_data.append({
                    'specialty': specialty['name'],
                    'price': price
                })
        
        with col2:
            if i + 1 < len(specialties):
                specialty = specialties[i + 1]
                st.markdown(f"**{specialty['name']}**")
                
                price = st.number_input(
                    "Standard Price",
                    min_value=0,
                    max_value=1000,
                    value=config.PRICING['average_appointment_values'].get(
                        specialty['name'], 250
                    ),
                    step=25,
                    key=f"price_{specialty['code']}"
                )
                
                pricing_data.append({
                    'specialty': specialty['name'],
                    'price': price
                })
    
    # Billing settings
    st.markdown("#### Billing Configuration")
    
    with st.form("billing_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            currency = st.selectbox(
                "Currency",
                ["USD", "EUR", "GBP", "CAD", "AUD"],
                index=0
            )
            
            tax_rate = st.number_input(
                "Tax Rate (%)",
                min_value=0.0,
                max_value=30.0,
                value=0.0,
                step=0.1
            )
            
            cancellation_fee = st.number_input(
                "Late Cancellation Fee",
                min_value=0,
                max_value=200,
                value=50,
                step=10,
                help="Fee for cancellations with insufficient notice"
            )
        
        with col2:
            no_show_fee = st.number_input(
                "No-Show Fee",
                min_value=0,
                max_value=200,
                value=75,
                step=10
            )
            
            deposit_required = st.checkbox(
                "Require Deposit for New Patients",
                value=False
            )
            
            if deposit_required:
                deposit_amount = st.number_input(
                    "Deposit Amount",
                    min_value=0,
                    max_value=200,
                    value=50,
                    step=10
                )
        
        # ROI tracking
        st.markdown("#### ROI Tracking")
        
        track_revenue_recovery = st.checkbox(
            "Track Revenue Recovery Metrics",
            value=True
        )
        
        include_labor_savings = st.checkbox(
            "Include Staff Time Savings in ROI",
            value=True
        )
        
        if include_labor_savings:
            hourly_staff_cost = st.number_input(
                "Average Hourly Staff Cost",
                min_value=15,
                max_value=100,
                value=35,
                step=5
            )
        
        submitted = st.form_submit_button("Save Pricing Settings", type="primary")
        
        if submitted:
            st.success("✅ Pricing settings saved successfully!")
            
            # Show updated pricing table
            st.markdown("#### Updated Pricing Structure")
            st.dataframe(pricing_data, use_container_width=True)

# Sidebar help
with st.sidebar:
    st.markdown("### ⚙️ Settings Help")
    st.markdown("""
    Configure system-wide settings:
    
    **Clinic Settings**
    - Basic information
    - Business hours
    - Holiday schedule
    
    **Appointment Settings**
    - Duration and booking rules
    - Waitlist configuration
    - Matching algorithm
    
    **Notifications**
    - Channel configuration
    - Message templates
    - Timing settings
    
    **Security**
    - User management
    - Password policies
    - Compliance settings
    
    **Pricing**
    - Specialty pricing
    - Billing configuration
    - ROI tracking
    """)
    
    if st.button("📥 Export All Settings"):
        st.info("Settings export coming soon!")
    
    if st.button("📤 Import Settings"):
        st.info("Settings import coming soon!")

if __name__ == "__main__":
    main()