# pages/waitlist_form.py
import streamlit as st
from datetime import datetime, timedelta, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firebase_utils import FirebaseDB
from utils.validation_utils import FormValidator, DataSanitizer
import config

st.set_page_config(
    page_title="Join Waitlist - CancelFillMD Pro",
    page_icon="📝",
    layout="centered"
)

def main():
    st.title("📝 Join Our Appointment Waitlist")
    st.markdown("""
    Get notified immediately when appointments matching your preferences become available.
    Notifications are sent via SMS and email on a first-come, first-served basis.
    """)
    
    with st.form("waitlist_form", clear_on_submit=True):
        st.markdown("### Contact Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name *",
                placeholder="John Doe",
                help="Enter your full legal name"
            )
            
            email = st.text_input(
                "Email Address *",
                placeholder="john@example.com",
                help="We'll send appointment notifications here"
            )
            
            phone = st.text_input(
                "Phone Number *",
                placeholder="(555) 123-4567",
                help="We'll send SMS notifications here"
            )
        
        with col2:
            specialty = st.selectbox(
                "Specialty *",
                options=[s['name'] for s in config.SPECIALTIES],
                help="Select the medical specialty you need"
            )
            
            insurance = st.text_input(
                "Insurance Provider",
                placeholder="Blue Cross Blue Shield",
                help="Optional - helps us verify coverage"
            )
        
        # Date preferences
        st.markdown("### Appointment Preferences")
        st.markdown("Select all dates when you could attend an appointment:")
        
        # Generate available dates (weekdays only)
        available_dates = []
        current_date = date.today()
        end_date = current_date + timedelta(days=30)
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                available_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Display dates in columns
        date_cols = st.columns(5)
        selected_dates = []
        
        for i, date_option in enumerate(available_dates):
            col_index = i % 5
            with date_cols[col_index]:
                if st.checkbox(
                    date_option.strftime("%b %d"),
                    key=f"date_{date_option}"
                ):
                    selected_dates.append(date_option)
        
        # Time preferences
        st.markdown("### Time Preferences")
        st.markdown("Select your preferred appointment times:")
        
        time_col1, time_col2, time_col3, time_col4 = st.columns(4)
        
        with time_col1:
            morning = st.checkbox("Morning (8 AM - 12 PM)")
        with time_col2:
            afternoon = st.checkbox("Afternoon (12 PM - 5 PM)")
        with time_col3:
            evening = st.checkbox("Evening (5 PM - 8 PM)")
        with time_col4:
            any_time = st.checkbox("Any Time")
        
        # Additional preferences
        st.markdown("### Additional Information")
        
        notes = st.text_area(
            "Special Requirements or Notes",
            placeholder="e.g., Wheelchair accessible, specific doctor preference, etc.",
            help="Optional - any special needs we should know about"
        )
        
        # Consent
        st.markdown("### Consent")
        
        consent = st.checkbox(
            "I agree to receive SMS and email notifications about appointment availability. "
            "I understand that appointments are offered on a first-come, first-served basis "
            "and I must book quickly when notified."
        )
        
        # Submit button
        submitted = st.form_submit_button(
            "Join Waitlist",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validate form
            errors = []
            
            if not name:
                errors.append("Please enter your full name")
            
            # Email validation
            if not email:
                errors.append("Please enter your email address")
            else:
                valid, msg = FormValidator.validate_email(email)
                if not valid:
                    errors.append(msg)
            
            # Phone validation
            if not phone:
                errors.append("Please enter your phone number")
            else:
                valid, msg = FormValidator.validate_phone(phone)
                if not valid:
                    errors.append("Please enter a valid 10-digit phone number")
            
            # Date selection
            if not selected_dates:
                errors.append("Please select at least one preferred date")
            
            # Time preferences
            if not any([morning, afternoon, evening, any_time]):
                errors.append("Please select at least one time preference")
            
            # Consent
            if not consent:
                errors.append("Please agree to receive notifications")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Process registration
                try:
                    # Initialize database
                    db = FirebaseDB()
                    
                    # Build time preferences
                    time_preferences = []
                    if any_time:
                        time_preferences = ["any"]
                    else:
                        if morning:
                            time_preferences.append("morning")
                        if afternoon:
                            time_preferences.append("afternoon")
                        if evening:
                            time_preferences.append("evening")
                    
                    # Create patient data
                    patient_data = {
                        'name': DataSanitizer.sanitize_name(name),
                        'email': DataSanitizer.sanitize_email(email),
                        'phone': DataSanitizer.sanitize_phone(phone) if valid else phone,
                        'specialty': specialty,
                        'insurance': insurance if insurance else None,
                        'preferred_dates': [d.strftime('%Y-%m-%d') for d in selected_dates],
                        'time_preferences': time_preferences,
                        'notes': DataSanitizer.sanitize_text_input(notes) if notes else None,
                        'created_at': datetime.now().isoformat(),
                        'active': True,
                        'notified_count': 0
                    }
                    
                    # Add to waitlist
                    patient_id = db.add_to_waitlist(patient_data)
                    
                    if patient_id:
                        st.success("✅ You've been successfully added to the waitlist!")
                        st.info(f"Your waitlist ID: {patient_id[:8]}")
                        
                        st.markdown("""
                        ### What Happens Next?
                        
                        1. **You'll receive notifications** when appointments matching your preferences become available
                        2. **Check your phone and email** - we'll notify you via both channels
                        3. **Act quickly** - appointments are first-come, first-served
                        4. **Click the secure link** in the notification to book instantly
                        5. **Get confirmation** immediately after booking
                        
                        ### Important Tips:
                        
                        - 🚀 **Response time matters** - most appointments are filled within 30 minutes
                        - 📱 **Keep notifications on** - enable SMS and email alerts
                        - ⏰ **Booking links expire** after 2 hours for security
                        - 🔄 **Stay active** - update your preferences anytime through the Patient Portal
                        """)
                        
                        st.balloons()
                    else:
                        st.error("Failed to add to waitlist. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.error("Please try again or contact support.")
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Home"):
        st.switch_page("app.py")

if __name__ == "__main__":
    main()