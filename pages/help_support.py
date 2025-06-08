# pages/help_support.py
"""
Help and support documentation page
"""
import streamlit as st
import config

st.set_page_config(
    page_title="Help & Support - CancelFillMD Pro",
    page_icon="❓",
    layout="wide"
)

def main():
    st.title("❓ Help & Support")
    st.markdown("Everything you need to know about using CancelFillMD Pro")
    
    # Help navigation
    help_section = st.selectbox(
        "What do you need help with?",
        ["Getting Started", "Patient Management", "Appointment Management", 
         "Notifications", "Analytics & Reports", "Troubleshooting", "FAQs"]
    )
    
    if help_section == "Getting Started":
        getting_started()
    elif help_section == "Patient Management":
        patient_management()
    elif help_section == "Appointment Management":
        appointment_management()
    elif help_section == "Notifications":
        notifications_help()
    elif help_section == "Analytics & Reports":
        analytics_help()
    elif help_section == "Troubleshooting":
        troubleshooting()
    elif help_section == "FAQs":
        faqs()

def getting_started():
    st.markdown("## 🚀 Getting Started")
    
    with st.expander("System Overview", expanded=True):
        st.markdown("""
        ### Welcome to CancelFillMD Pro!
        
        CancelFillMD Pro helps you automatically fill cancelled appointments by matching them 
        with waitlisted patients. Here's how it works:
        
        1. **Patients join waitlists** for their preferred dates and specialties
        2. **When appointments are cancelled**, the system automatically identifies matching patients
        3. **Notifications are sent** via SMS and email with secure booking links
        4. **First patient to respond** gets the appointment
        5. **Staff is notified** when slots are filled
        
        ### Key Benefits:
        - 📈 Recover 80%+ of lost revenue from cancellations
        - ⏱️ Fill slots in under 30 minutes instead of hours
        - 💼 Save 2+ hours of staff time per cancellation
        - 😊 Improve patient satisfaction with faster appointments
        """)
    
    with st.expander("First Steps"):
        st.markdown("""
        ### 1. Set Up Your Clinic Information
        Go to **Settings → Clinic Settings** to configure:
        - Clinic name and contact information
        - Business hours
        - Holiday schedule
        
        ### 2. Configure Specialties and Pricing
        Go to **Settings → Pricing & Billing** to set:
        - Appointment values by specialty
        - Default appointment durations
        
        ### 3. Import Your Schedule
        Go to **Upload Schedule** to:
        - Upload existing appointments via CSV
        - Or manually enter appointments
        
        ### 4. Build Your Waitlist
        Direct patients to **Join Waitlist** to:
        - Sign up for appointment notifications
        - Set their preferences
        
        ### 5. Start Filling Cancellations!
        When cancellations occur:
        - Use **Cancel Appointment** to process them
        - Watch as the system automatically fills slots
        """)
    
    with st.expander("User Roles"):
        st.markdown("""
        ### Administrator
        - Full system access
        - User management
        - System settings
        - All reports and analytics
        
        ### Practice Manager
        - Appointment management
        - View analytics
        - Manage waitlists
        - Cannot change system settings
        
        ### Staff Member
        - Cancel appointments
        - View schedules
        - Basic reporting
        - Cannot access settings
        """)

def patient_management():
    st.markdown("## 👥 Patient Management")
    
    with st.expander("Waitlist Management", expanded=True):
        st.markdown("""
        ### Adding Patients to Waitlist
        
        **Option 1: Patient Self-Service**
        1. Direct patients to the **Join Waitlist** page
        2. They enter their information and preferences
        3. System automatically adds them to appropriate waitlists
        
        **Option 2: Staff Entry**
        1. Go to **Join Waitlist** page
        2. Enter patient information on their behalf
        3. Select their preferences
        
        ### Managing Waitlist Entries
        
        **View Waitlist:**
        - Go to **Staff Dashboard → Waitlist** tab
        - Filter by specialty, date, or patient name
        - See notification history for each patient
        
        **Remove from Waitlist:**
        - Find patient in waitlist view
        - Click "Remove" button
        - Patient won't receive future notifications
        
        ### Waitlist Best Practices
        - Keep waitlist fresh - remove inactive patients monthly
        - Encourage specific date preferences for better matching
        - Monitor waitlist size - aim for 10-15 patients per specialty
        """)
    
    with st.expander("Patient Preferences"):
        st.markdown("""
        ### Understanding Patient Preferences
        
        **Date Preferences:**
        - Patients can select multiple preferred dates
        - More dates = higher chance of getting notified
        - System prioritizes exact date matches
        
        **Time Preferences:**
        - Morning (8 AM - 12 PM)
        - Afternoon (12 PM - 5 PM)
        - Evening (5 PM - 8 PM)
        - Any time
        
        **Matching Score Factors:**
        1. **Wait Time (30%)** - How long they've been waiting
        2. **Date Match (20%)** - Appointment matches preferred date
        3. **Time Match (20%)** - Appointment matches preferred time
        4. **Previous Attempts (20%)** - Failed booking attempts
        5. **Patient Loyalty (10%)** - Length of patient relationship
        """)

def appointment_management():
    st.markdown("## 📅 Appointment Management")
    
    with st.expander("Uploading Schedules", expanded=True):
        st.markdown("""
        ### CSV Upload Format
        
        Your CSV file should have these columns:
        ```
        Date,Time,Doctor,Specialty,Patient Name,Patient Email,Patient Phone
        2025-06-10,09:00 AM,Dr. Smith,Dermatology,John Doe,john@email.com,+15551234567
        2025-06-10,10:00 AM,Dr. Smith,Dermatology,,,
        ```
        
        **Required Fields:**
        - Date (YYYY-MM-DD format)
        - Time (HH:MM AM/PM format)
        - Doctor (Full name)
        - Specialty
        
        **Optional Fields:**
        - Patient Name (leave blank for available slots)
        - Patient Email
        - Patient Phone
        
        ### Manual Entry
        Use for adding individual appointments:
        1. Go to **Upload Schedule**
        2. Scroll to "Manual Entry" section
        3. Fill in appointment details
        4. Click "Add Appointment"
        """)
    
    with st.expander("Cancelling Appointments"):
        st.markdown("""
        ### Staff Cancellation Process
        
        1. Go to **Cancel Appointment**
        2. Select "Staff Cancellation"
        3. Choose appointment from dropdown
        4. Enter cancellation reason (optional)
        5. Configure notification options:
           - ✅ Notify waitlist immediately
           - ✅ Auto-fill from waitlist
           - ✅ Use priority matching
        6. Click "Cancel Appointment"
        
        ### What Happens Next
        
        1. **Appointment Status Changes** to "cancelled"
        2. **Matching Algorithm Runs** to find best waitlist matches
        3. **Notifications Sent** to top 10 matches
        4. **Booking Links Created** with 2-hour expiry
        5. **First Patient Books** and gets confirmation
        6. **Others Notified** that slot is filled
        7. **Staff Alerted** about new booking
        
        ### Cancellation Rules
        - Minimum notice period: 24 hours (configurable)
        - Late cancellations may incur fees
        - No-shows tracked separately
        """)

def notifications_help():
    st.markdown("## 🔔 Notifications")
    
    with st.expander("Notification Types", expanded=True):
        st.markdown("""
        ### 1. Appointment Available
        **When sent:** Immediately after cancellation
        **Recipients:** Top matching waitlist patients
        **Channels:** SMS + Email
        **Contents:**
        - Appointment date/time
        - Doctor and specialty
        - Secure booking link
        - Expiry time
        
        ### 2. Booking Confirmation
        **When sent:** After successful booking
        **Recipients:** Patient who booked
        **Channels:** SMS + Email
        **Contents:**
        - Confirmation number
        - Appointment details
        - Cancellation policy
        - Add to calendar link
        
        ### 3. Slot Filled Notice
        **When sent:** After slot is filled
        **Recipients:** Other notified patients
        **Channels:** SMS + Email
        **Contents:**
        - Slot no longer available
        - Remain on waitlist message
        - Encouragement to try next time
        
        ### 4. Appointment Reminders
        **When sent:** 48 and 24 hours before
        **Recipients:** All confirmed patients
        **Channels:** SMS + Email
        **Contents:**
        - Appointment details
        - Arrival instructions
        - Cancellation link
        """)
    
    with st.expander("Customizing Messages"):
        st.markdown("""
        ### Message Templates
        
        Go to **Settings → Notification Settings** to customize:
        
        **Available Variables:**
        - `{patient_name}` - Patient's full name
        - `{date}` - Appointment date
        - `{time}` - Appointment time
        - `{doctor}` - Doctor's name
        - `{specialty}` - Medical specialty
        - `{clinic_name}` - Your clinic name
        - `{link}` - Booking/cancellation link
        - `{phone}` - Clinic phone number
        
        **Example SMS Template:**
        ```
        Hi {patient_name}, appointment available on {date} at {time} 
        with {doctor}. Book now: {link} -Reply STOP to opt out
        ```
        
        ### Best Practices
        - Keep SMS under 160 characters
        - Include opt-out instructions
        - Make links prominent
        - Use clear call-to-action
        """)

def analytics_help():
    st.markdown("## 📊 Analytics & Reports")
    
    with st.expander("Understanding Metrics", expanded=True):
        st.markdown("""
        ### Key Performance Indicators (KPIs)
        
        **Fill Rate**
        - Formula: (Filled Appointments / Cancelled Appointments) × 100
        - Target: 80%+
        - Measures effectiveness of waitlist system
        
        **Average Fill Time**
        - Time from cancellation to booking
        - Target: Under 30 minutes
        - Measures system efficiency
        
        **Revenue Recovery**
        - Dollar value of filled appointments
        - Compare to potential loss
        - ROI calculation included
        
        **Utilization Rate**
        - (Used Slots / Total Slots) × 100
        - Target: 85%+
        - Measures overall efficiency
        
        **Patient Satisfaction**
        - Based on feedback surveys
        - Target: 4.5/5.0
        - Measures patient experience
        """)
    
    with st.expander("Generating Reports"):
        st.markdown("""
        ### Available Reports
        
        **Daily Summary**
        - Today's cancellations and fills
        - Revenue impact
        - Staff time saved
        - Action items
        
        **Weekly Performance**
        - Trend analysis
        - Department comparisons
        - Top performing days
        - Improvement opportunities
        
        **Monthly Analytics**
        - Comprehensive KPIs
        - Financial summary
        - Pattern analysis
        - Recommendations
        
        ### Export Options
        
        1. **PDF Reports**
           - Professional formatting
           - Charts and graphs
           - Executive summary
           - Email-ready
        
        2. **Excel Exports**
           - Raw data access
           - Multiple sheets
           - Pivot table ready
           - Custom analysis
        
        3. **CSV Downloads**
           - Simple data format
           - Easy integration
           - Historical records
        """)

def troubleshooting():
    st.markdown("## 🔧 Troubleshooting")
    
    common_issues = {
        "Notifications not sending": {
            "causes": [
                "SMS/Email credits exhausted",
                "Invalid phone numbers or emails",
                "Notification settings disabled",
                "API keys incorrect"
            ],
            "solutions": [
                "Check Twilio/SendGrid account balance",
                "Verify patient contact information",
                "Check Settings → Notifications",
                "Verify API keys in environment settings"
            ]
        },
        "Appointments not appearing": {
            "causes": [
                "CSV format incorrect",
                "Date format mismatch",
                "Upload failed silently",
                "Filter settings hiding appointments"
            ],
            "solutions": [
                "Download and use sample CSV template",
                "Use YYYY-MM-DD date format",
                "Check for error messages after upload",
                "Reset filters in dashboard"
            ]
        },
        "Patients can't book appointments": {
            "causes": [
                "Booking link expired",
                "Appointment already filled",
                "Browser compatibility issues",
                "Session timeout"
            ],
            "solutions": [
                "Links expire after 2 hours",
                "First-come, first-served basis",
                "Recommend Chrome/Safari/Firefox",
                "Ask patient to try again"
            ]
        },
        "Reports showing incorrect data": {
            "causes": [
                "Date range filters",
                "Timezone differences",
                "Cached data",
                "Incomplete data entry"
            ],
            "solutions": [
                "Check date range selection",
                "Verify timezone settings",
                "Refresh the page",
                "Ensure all appointments have required fields"
            ]
        }
    }
    
    for issue, details in common_issues.items():
        with st.expander(f"❗ {issue}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Possible Causes")
                for cause in details['causes']:
                    st.markdown(f"• {cause}")
            
            with col2:
                st.markdown("### Solutions")
                for solution in details['solutions']:
                    st.markdown(f"✓ {solution}")

def faqs():
    st.markdown("## ❓ Frequently Asked Questions")
    
    faqs_list = [
        {
            "question": "How quickly do cancelled slots typically get filled?",
            "answer": "On average, slots are filled within 21 minutes. However, this depends on your waitlist size and patient responsiveness. Popular time slots often fill within 5-10 minutes."
        },
        {
            "question": "How many patients should I notify for each cancellation?",
            "answer": "The system notifies 10 patients by default. This provides a good balance between filling slots quickly and not over-notifying. You can adjust this in Settings."
        },
        {
            "question": "What happens if multiple patients try to book the same slot?",
            "answer": "Only the first patient to click the link and confirm gets the appointment. Others see a message that the slot has been filled and remain on the waitlist."
        },
        {
            "question": "Can patients cancel appointments they booked through the system?",
            "answer": "Yes, patients can cancel with 24+ hours notice through the Patient Portal or by calling your office. The system will then try to fill that slot again."
        },
        {
            "question": "How do I handle last-minute cancellations?",
            "answer": "The system works best with 2+ hours notice. For very last-minute cancellations, you may want to call waitlist patients directly or leave the slot open."
        },
        {
            "question": "What's the ROI of using CancelFillMD Pro?",
            "answer": "Most practices see ROI within the first week. With an average fill rate of 84%, practices recover $20,000-50,000 per month in previously lost revenue."
        },
        {
            "question": "Do I need to integrate with my existing scheduling system?",
            "answer": "No integration required! CancelFillMD Pro works alongside your current system. Staff manually updates your main calendar when slots are filled."
        },
        {
            "question": "How do I ensure HIPAA compliance?",
            "answer": "The system includes HIPAA-compliant features like encrypted data storage, audit logs, and secure communication. Enable HIPAA mode in Security Settings."
        },
        {
            "question": "Can I customize which staff members get notifications?",
            "answer": "Yes! In Settings, you can configure which staff members receive notifications for fills, cancellations, and other events."
        },
        {
            "question": "What if our internet goes down?",
            "answer": "The cloud-based system continues working. Notifications still go out. You can access the system from any device with internet, including mobile phones."
        }
    ]
    
    for faq in faqs_list:
        with st.expander(faq["question"]):
            st.markdown(faq["answer"])

# Sidebar
with st.sidebar:
    st.markdown("### 🆘 Quick Help")
    
    st.markdown("""
    **Need immediate help?**
    
    📧 Email: support@cancelfillmd.com
    📞 Phone: (555) 123-4567
    💬 Chat: Available 9 AM - 5 PM EST
    
    **Training Resources:**
    - [Video Tutorials](https://cancelfillmd.com/tutorials)
    - [User Manual](https://docs.cancelfillmd.com)
    - [Best Practices Guide](https://cancelfillmd.com/best-practices)
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Pro Tips")
    
    tips = [
        "Keep waitlists between 10-15 patients per specialty for optimal fill rates",
        "Send notifications within 5 minutes of cancellation for best results",
        "Update patient preferences quarterly to keep them current",
        "Review analytics weekly to identify patterns and optimize",
        "Train all staff on the cancellation process for consistency"
    ]
    
    import random
    st.info(f"💡 **Tip:** {random.choice(tips)}")

if __name__ == "__main__":
    main()