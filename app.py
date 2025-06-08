# app.py
"""
Main landing page for CancelFillMD Pro
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import config

# Set page config
st.set_page_config(
    page_title="CancelFillMD Pro - Smart Appointment Management",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Hide the default Streamlit header */
    header {visibility: hidden;}
    
    /* Custom styling for the main container */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: 500;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    
    /* Metric card styling */
    [data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Center the header content */
    h1, h2, h3 {
        text-align: center;
    }
    
    /* Fix plotly chart container */
    .js-plotly-plot {
        margin: 0 auto;
    }
    
    /* Remove extra spacing */
    .element-container {
        margin: 0;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align: center;'>
                <h1>📅 CancelFillMD Pro</h1>
                <p style='font-size: 1.2em; color: #888; margin-bottom: 2rem;'>
                    Smart Appointment Management System
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👥 For Patients")
        if st.button("Join Waitlist", key="join_waitlist", use_container_width=True):
            st.switch_page("pages/waitlist_form.py")
        if st.button("Check My Appointments", key="check_appointments", use_container_width=True):
            st.switch_page("pages/patient_portal.py")
    
    with col2:
        st.markdown("### 👩‍⚕️ For Staff")
        if st.button("Staff Dashboard", key="staff_dashboard", use_container_width=True):
            st.switch_page("pages/staff_dashboard.py")
        if st.button("Upload Schedule", key="upload_schedule", use_container_width=True):
            st.switch_page("pages/schedule_upload.py")
    
    with col3:
        st.markdown("### 🔧 Management")
        if st.button("Cancel Appointment", key="cancel_appointment", use_container_width=True):
            st.switch_page("pages/cancel_appointment.py")
        if st.button("System Settings", key="settings", use_container_width=True):
            st.switch_page("pages/settings.py")
    
    # Divider
    st.markdown("---")
    
    # System Statistics - Fixed sizing
    st.markdown("### 📊 System Statistics")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Display key metrics
    with col1:
        st.metric(
            label="Fill Rate",
            value="84%",
            delta="+12% vs last month",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Revenue Recovered",
            value="$125,000",
            delta="+$18,000 this month",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="Active Waitlist",
            value="347",
            delta="+23 today",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Avg Fill Time",
            value="4.2 min",
            delta="-2.1 min improvement",
            delta_color="normal"
        )
    
    # Create smaller, properly sized chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create a simple line chart with fixed dimensions
        fig = go.Figure()
        
        # Sample data for demonstration
        dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(7, -1, -1)]
        fill_rates = [78, 82, 80, 85, 83, 87, 86, 84]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=fill_rates,
            mode='lines+markers',
            name='Fill Rate',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        
        # Update layout with fixed height
        fig.update_layout(
            title="Fill Rate Trend (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Fill Rate (%)",
            height=300,  # Fixed height
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 100]),
            showlegend=False
        )
        
        # Display chart with use_container_width=True
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown("#### Quick Stats")
        st.markdown("""
        - **Today's Cancellations:** 12
        - **Slots Filled:** 10 (83%)
        - **Pending Notifications:** 2
        - **Avg Response Time:** 8 min
        """)
        
        if config.DEMO_MODE:
            st.info("🎮 **Demo Mode Active**")
    
    # Features section
    st.markdown("---")
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🚀 Instant Notifications**
        - SMS & Email alerts
        - Smart patient matching
        - Automated reminders
        """)
    
    with col2:
        st.markdown("""
        **📊 Real-time Analytics**
        - ROI tracking
        - Performance metrics
        - Custom reports
        """)
    
    with col3:
        st.markdown("""
        **🔒 Secure & Compliant**
        - HIPAA compliant
        - Role-based access
        - Audit trails
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
            © 2024 CancelFillMD Pro | 
            <a href="#" style='color: #667eea;'>Help & Support</a> | 
            <a href="#" style='color: #667eea;'>Privacy Policy</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()