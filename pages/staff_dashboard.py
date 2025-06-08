# pages/staff_dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firebase_utils import FirebaseDB
from utils.security_utils import init_session_state, login_user, logout_user
import config

st.set_page_config(
    page_title="Staff Dashboard - CancelFillMD Pro",
    page_icon="📊",
    layout="wide"
)

def check_authentication():
    """Check if user is authenticated"""
    init_session_state()
    
    if not st.session_state.authenticated:
        show_login_form()
        return False
    
    return True

def show_login_form():
    """Display login form"""
    st.title("🔐 Staff Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### Please Login to Continue")
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            with col2:
                if st.form_submit_button("Back to Home", use_container_width=True):
                    st.switch_page("app.py")
            
            if submitted:
                # Simple authentication for demo
                if username == "admin" and password == "admin123":
                    login_user(username, 'Administrator')
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        # Demo credentials hint
        if config.DEMO_MODE:
            st.info("""
            **Demo Credentials:**
            - Username: `admin`
            - Password: `admin123`
            """)

def main():
    if not check_authentication():
        return
    
    # Header with logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("📊 Staff Dashboard")
        st.markdown(f"Welcome, {st.session_state.get('user_id', 'Staff')}")
    with col2:
        if st.button("Logout"):
            logout_user()
            st.rerun()
    
    # Initialize database
    db = FirebaseDB()
    
    # Date filter
    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        selected_date = st.date_input("Select Date", value=date.today())
    
    # Get appointments for selected date
    appointments = db.get_appointments(date=selected_date.strftime('%Y-%m-%d'))
    
    # Summary metrics
    st.markdown("### 📈 Today's Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_appointments = len(appointments)
    scheduled = len([a for a in appointments if a.get('status') == 'scheduled'])
    cancelled = len([a for a in appointments if a.get('status') == 'cancelled'])
    filled = len([a for a in appointments if a.get('status') == 'filled'])
    
    with col1:
        st.metric("Total Appointments", total_appointments)
    
    with col2:
        st.metric("Scheduled", scheduled)
    
    with col3:
        st.metric("Cancelled", cancelled, delta=f"-{cancelled}")
    
    with col4:
        st.metric("Filled via Waitlist", filled, delta=f"+{filled}")
    
    # Calculate fill rate
    fill_rate = (filled / cancelled * 100) if cancelled > 0 else 0
    st.metric("Fill Rate", f"{fill_rate:.1f}%", delta=f"{fill_rate-50:.1f}% vs baseline")
    
    # Appointment list
    st.markdown("### 📅 Appointment Schedule")
    
    if appointments:
        # Convert to DataFrame for display
        df_data = []
        for apt in appointments:
            df_data.append({
                'Time': apt.get('time', ''),
                'Doctor': apt.get('doctor', ''),
                'Specialty': apt.get('specialty', ''),
                'Status': apt.get('status', '').title(),
                'Patient': apt.get('patient_name', 'Available'),
                'ID': apt.get('id', '')[:8]
            })
        
        df = pd.DataFrame(df_data)
        
        # Display dataframe
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No appointments scheduled for this date.")
    
    # Waitlist overview
    st.markdown("### 👥 Waitlist Overview")
    
    waitlist = db.get_waitlist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Waitlist Patients", len(waitlist))
        
        # Specialty breakdown
        specialty_counts = {}
        for patient in waitlist:
            spec = patient.get('specialty', 'Unknown')
            specialty_counts[spec] = specialty_counts.get(spec, 0) + 1
        
        if specialty_counts:
            fig = px.pie(
                values=list(specialty_counts.values()),
                names=list(specialty_counts.keys()),
                title="Waitlist by Specialty"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Recent activity
        st.markdown("#### Recent Activity")
        
        # Show some demo activity
        activities = [
            "📧 Notified 5 patients - 15 min ago",
            "✅ Slot filled - 45 min ago",
            "❌ Appointment cancelled - 1 hour ago",
            "📧 Notified 3 patients - 2 hours ago",
            "✅ Slot filled - 3 hours ago"
        ]
        
        for activity in activities:
            st.markdown(activity)
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload Schedule", use_container_width=True):
            st.switch_page("pages/schedule_upload.py")
    
    with col2:
        if st.button("❌ Process Cancellation", use_container_width=True):
            st.switch_page("pages/cancel_appointment.py")
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/analytics_dashboard.py")

if __name__ == "__main__":
    main()