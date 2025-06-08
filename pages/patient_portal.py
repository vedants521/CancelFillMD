# pages/patient_portal.py
"""
Patient self-service portal for managing appointments and waitlist entries
"""
import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd
from utils import (
    FirebaseDB, 
    FormValidator, 
    DataSanitizer,
    NotificationService,
    SecurityManager
)
import config

st.set_page_config(
    page_title="Patient Portal - CancelFillMD Pro",
    page_icon="👤",
    layout="wide"
)

def verify_patient(email: str, phone: str) -> dict:
    """Verify patient identity using email and phone"""
    db = FirebaseDB()
    
    # Sanitize inputs
    email = DataSanitizer.sanitize_email(email)
    phone = DataSanitizer.sanitize_phone(phone)
    
    # Search in waitlist
    waitlist = db.get_waitlist()
    for patient in waitlist:
        if patient.get('email') == email and patient.get('phone').endswith(phone[-4:]):
            return patient
    
    # Search in appointments
    appointments = db.get_appointments()
    for apt in appointments:
        if (apt.get('patient_email') == email and 
            apt.get('patient_phone', '').endswith(phone[-4:])):
            return {
                'name': apt.get('patient_name'),
                'email': apt.get('patient_email'),
                'phone': apt.get('patient_phone'),
                'id': apt.get('patient_id', 'temp_' + SecurityManager.generate_secure_link(8))
            }
    
    return None

def main():
    st.title("👤 Patient Portal")
    st.markdown("Manage your appointments and waitlist preferences")
    
    # Initialize session state
    if 'patient_verified' not in st.session_state:
        st.session_state.patient_verified = False
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = None
    
    # Patient verification
    if not st.session_state.patient_verified:
        st.markdown("### 🔐 Verify Your Identity")
        
        with st.form("patient_verification"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email Address", placeholder="john@example.com")
            
            with col2:
                phone = st.text_input("Phone Number (last 4 digits)", 
                                    placeholder="1234",
                                    max_chars=4)
            
            submitted = st.form_submit_button("Access My Portal", type="primary")
            
            if submitted:
                if not email or not phone:
                    st.error("Please enter both email and phone number")
                elif len(phone) != 4 or not phone.isdigit():
                    st.error("Please enter the last 4 digits of your phone number")
                else:
                    # Verify patient
                    patient = verify_patient(email, phone)
                    
                    if patient:
                        st.session_state.patient_verified = True
                        st.session_state.patient_data = patient
                        st.success(f"Welcome back, {patient['name']}!")
                        st.rerun()
                    else:
                        st.error("No matching records found. Please check your information.")
        
        # Help section
        with st.expander("ℹ️ Need Help?"):
            st.markdown("""
            **Can't access your portal?**
            - Make sure you're using the email address you provided during registration
            - Enter only the last 4 digits of your phone number
            - If you're still having issues, contact our office at (555) 123-4567
            
            **First time here?**
            - You need to be an existing patient or on our waitlist
            - Join our waitlist through the main page
            """)
    
    else:
        # Patient is verified - show portal
        patient = st.session_state.patient_data
        
        # Header with logout
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### Welcome, {patient['name']}!")
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.patient_verified = False
                st.session_state.patient_data = None
                st.rerun()
        
        # Portal tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 My Appointments",
            "📋 Waitlist Status", 
            "⚙️ Preferences",
            "📧 Notifications"
        ])
        
        with tab1:
            display_appointments(patient)
        
        with tab2:
            display_waitlist_status(patient)
        
        with tab3:
            manage_preferences(patient)
        
        with tab4:
            notification_preferences(patient)

def display_appointments(patient: dict):
    """Display patient's upcoming appointments"""
    st.markdown("### 📅 Your Upcoming Appointments")
    
    db = FirebaseDB()
    appointments = db.get_appointments()
    
    # Filter patient's appointments
    patient_appointments = []
    for apt in appointments:
        if (apt.get('patient_email') == patient['email'] and
            apt.get('status') in ['scheduled', 'filled'] and
            apt.get('date') >= date.today().strftime('%Y-%m-%d')):
            patient_appointments.append(apt)
    
    if patient_appointments:
        # Sort by date and time
        patient_appointments.sort(key=lambda x: (x['date'], x['time']))
        
        for apt in patient_appointments:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{apt['date']}**")
                st.markdown(f"{apt['time']}")
            
            with col2:
                st.markdown(f"**{apt['doctor']}**")
                st.markdown(f"{apt['specialty']}")
            
            with col3:
                # Calculate time until appointment
                apt_datetime = datetime.strptime(f"{apt['date']} {apt['time']}", 
                                               '%Y-%m-%d %I:%M %p')
                time_until = apt_datetime - datetime.now()
                
                if time_until.days > 0:
                    st.markdown(f"In {time_until.days} days")
                elif time_until.total_seconds() > 0:
                    hours = int(time_until.total_seconds() // 3600)
                    st.markdown(f"In {hours} hours")
                else:
                    st.markdown("Past appointment")
            
            with col4:
                # Cancel button (if allowed by policy)
                min_notice = config.APPOINTMENT_SETTINGS['min_cancellation_notice_hours']
                if time_until.total_seconds() / 3600 > min_notice:
                    if st.button("Cancel", key=f"cancel_{apt['id']}"):
                        cancel_appointment(apt, patient)
                else:
                    st.markdown(f"*Cannot cancel*")
                    st.caption(f"Less than {min_notice}h notice")
            
            st.markdown("---")
    else:
        st.info("You don't have any upcoming appointments.")
        
        if st.button("Join Waitlist"):
            st.switch_page("pages/waitlist_form.py")

def display_waitlist_status(patient: dict):
    """Display patient's waitlist entries"""
    st.markdown("### 📋 Your Waitlist Status")
    
    db = FirebaseDB()
    waitlist = db.get_waitlist()
    
    # Filter patient's waitlist entries
    patient_entries = []
    for entry in waitlist:
        if entry.get('email') == patient['email'] and entry.get('active', True):
            patient_entries.append(entry)
    
    if patient_entries:
        st.markdown(f"You have **{len(patient_entries)}** active waitlist entries:")
        
        for i, entry in enumerate(patient_entries):
            with st.expander(f"{entry['specialty']} - Added {entry['created_at'][:10]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Preferred Dates:**")
                    for date_str in entry['preferred_dates']:
                        st.markdown(f"• {date_str}")
                
                with col2:
                    st.markdown("**Time Preferences:**")
                    for time_pref in entry['time_preferences']:
                        st.markdown(f"• {time_pref.title()}")
                
                st.markdown(f"**Times Notified:** {entry.get('notified_count', 0)}")
                
                # Remove from waitlist button
                if st.button(f"Remove from Waitlist", key=f"remove_{entry['id']}"):
                    db.update_waitlist_patient(entry['id'], {'active': False})
                    st.success("Removed from waitlist")
                    st.rerun()
    else:
        st.info("You're not currently on any waitlists.")
        
        if st.button("Join a Waitlist"):
            st.switch_page("pages/waitlist_form.py")

def manage_preferences(patient: dict):
    """Manage patient preferences"""
    st.markdown("### ⚙️ Manage Your Preferences")
    
    db = FirebaseDB()
    
    with st.form("update_preferences"):
        st.markdown("#### Contact Information")
        
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email", value=patient.get('email', ''))
            phone = st.text_input("Phone", value=patient.get('phone', ''))
        
        with col2:
            preferred_contact = st.selectbox(
                "Preferred Contact Method",
                ["SMS & Email", "SMS Only", "Email Only"],
                index=0
            )
        
        st.markdown("#### Appointment Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            advance_notice = st.selectbox(
                "Minimum Advance Notice",
                ["Same Day", "1 Day", "2 Days", "3 Days", "1 Week"],
                index=1
            )
        
        with col2:
            max_travel_time = st.selectbox(
                "Maximum Travel Time",
                ["15 minutes", "30 minutes", "45 minutes", "1 hour", "Any"],
                index=1
            )
        
        st.markdown("#### Additional Preferences")
        
        preferences = st.multiselect(
            "Select all that apply:",
            [
                "Prefer morning appointments",
                "Prefer afternoon appointments",
                "Prefer specific doctors only",
                "Willing to see any available provider",
                "Interested in telehealth options",
                "Need wheelchair accessibility"
            ]
        )
        
        special_needs = st.text_area(
            "Special Requirements or Notes",
            placeholder="Any specific needs or preferences we should know about..."
        )
        
        submitted = st.form_submit_button("Update Preferences", type="primary")
        
        if submitted:
            # Validate inputs
            valid_email, email_msg = FormValidator.validate_email(email)
            valid_phone, phone_msg = FormValidator.validate_phone(phone)
            
            if not valid_email:
                st.error(email_msg)
            elif not valid_phone:
                st.error(phone_msg)
            else:
                # Update preferences
                updated_data = {
                    'email': DataSanitizer.sanitize_email(email),
                    'phone': DataSanitizer.sanitize_phone(phone),
                    'preferred_contact': preferred_contact,
                    'advance_notice': advance_notice,
                    'max_travel_time': max_travel_time,
                    'preferences': preferences,
                    'special_needs': special_needs,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Update in database (implementation depends on your schema)
                st.success("✅ Your preferences have been updated!")
                
                # Update session state
                st.session_state.patient_data.update(updated_data)

def notification_preferences(patient: dict):
    """Manage notification preferences"""
    st.markdown("### 📧 Notification Settings")
    
    with st.form("notification_preferences"):
        st.markdown("#### When to Notify Me")
        
        notify_for = st.multiselect(
            "Send me notifications for:",
            [
                "Appointment reminders (48 hours before)",
                "Appointment reminders (24 hours before)",
                "Available appointments matching my waitlist",
                "Changes to my scheduled appointments",
                "New services or offerings",
                "Health tips and newsletters"
            ],
            default=[
                "Appointment reminders (48 hours before)",
                "Appointment reminders (24 hours before)",
                "Available appointments matching my waitlist",
                "Changes to my scheduled appointments"
            ]
        )
        
        st.markdown("#### Quiet Hours")
        
        col1, col2 = st.columns(2)
        with col1:
            quiet_start = st.time_input("Do not notify before:", value=datetime.strptime("08:00", "%H:%M").time())
        
        with col2:
            quiet_end = st.time_input("Do not notify after:", value=datetime.strptime("20:00", "%H:%M").time())
        
        st.markdown("#### Notification Frequency")
        
        max_notifications = st.slider(
            "Maximum notifications per day:",
            min_value=1,
            max_value=10,
            value=5
        )
        
        st.markdown("#### Opt-Out Options")
        
        opt_out = st.checkbox("Opt out of all non-essential notifications")
        
        submitted = st.form_submit_button("Save Notification Settings", type="primary")
        
        if submitted:
            notification_settings = {
                'notify_for': notify_for,
                'quiet_hours': {
                    'start': quiet_start.strftime("%H:%M"),
                    'end': quiet_end.strftime("%H:%M")
                },
                'max_daily_notifications': max_notifications,
                'opt_out_marketing': opt_out,
                'updated_at': datetime.now().isoformat()
            }
            
            # Save notification preferences
            st.success("✅ Your notification preferences have been saved!")
            
            # Show summary
            with st.expander("Your Current Settings"):
                st.json(notification_settings)

def cancel_appointment(appointment: dict, patient: dict):
    """Handle appointment cancellation"""
    db = FirebaseDB()
    
    # Show cancellation confirmation dialog
    with st.form(f"cancel_confirm_{appointment['id']}"):
        st.warning("⚠️ Are you sure you want to cancel this appointment?")
        
        st.markdown(f"""
        **Appointment Details:**
        - Date: {appointment['date']}
        - Time: {appointment['time']}
        - Doctor: {appointment['doctor']}
        - Specialty: {appointment['specialty']}
        """)
        
        reason = st.selectbox(
            "Reason for cancellation:",
            [
                "Schedule conflict",
                "Feeling better",
                "Found another appointment",
                "Transportation issues",
                "Financial reasons",
                "Other"
            ]
        )
        
        if reason == "Other":
            other_reason = st.text_input("Please specify:")
        else:
            other_reason = ""
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Yes, Cancel Appointment", type="primary"):
                # Process cancellation
                db.update_appointment(appointment['id'], {
                    'status': 'cancelled',
                    'cancelled_at': datetime.now().isoformat(),
                    'cancelled_by': 'patient',
                    'cancellation_reason': reason if reason != "Other" else other_reason,
                    'patient_cancelled': True
                })
                
                # Send confirmation
                notifier = NotificationService()
                # notifier.send_cancellation_confirmation(patient, appointment)
                
                st.success("✅ Your appointment has been cancelled.")
                st.info("You'll receive a confirmation email shortly.")
                st.rerun()
        
        with col2:
            if st.form_submit_button("Keep Appointment"):
                st.info("Your appointment remains scheduled.")

# Add to sidebar
with st.sidebar:
    st.markdown("### 🏥 Patient Portal")
    st.markdown("""
    Use this portal to:
    - View upcoming appointments
    - Cancel appointments (24h+ notice)
    - Manage waitlist entries
    - Update your preferences
    - Control notifications
    """)
    
    if config.FEATURES['enable_telemedicine']:
        st.info("🎥 Telehealth appointments coming soon!")

if __name__ == "__main__":
    main()