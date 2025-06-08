import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from utils.firebase_utils import FirebaseDB

st.set_page_config(page_title="Upload Schedule - CancelFillMD Pro", page_icon="📤")

def generate_sample_csv():
    """Generate a sample CSV file for reference"""
    sample_data = {
        'Date': ['2025-06-10', '2025-06-10', '2025-06-10'],
        'Time': ['09:00 AM', '10:00 AM', '11:00 AM'],
        'Doctor': ['Dr. Smith', 'Dr. Smith', 'Dr. Smith'],
        'Specialty': ['Dermatology', 'Dermatology', 'Dermatology'],
        'Patient Name': ['John Doe', 'Jane Smith', ''],
        'Patient Email': ['john@email.com', 'jane@email.com', ''],
        'Patient Phone': ['+15551234567', '+15559876543', '']
    }
    
    df = pd.DataFrame(sample_data)
    return df

def main():
    st.title("📤 Upload Appointment Schedule")
    st.markdown("Upload your appointment schedule to sync with CancelFillMD Pro")
    
    # Instructions
    with st.expander("📖 Instructions"):
        st.markdown("""
        ### How to upload your schedule:
        
        1. **Prepare your CSV file** with the following columns:
           - Date (YYYY-MM-DD format)
           - Time (HH:MM AM/PM format)
           - Doctor (Full name)
           - Specialty
           - Patient Name (leave empty for available slots)
           - Patient Email (optional)
           - Patient Phone (optional)
        
        2. **Upload the file** using the uploader below
        
        3. **Review** the imported data
        
        4. **Confirm** to add appointments to the system
        """)
        
        # Download sample
        sample_df = generate_sample_csv()
        csv = sample_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv,
            file_name="appointment_schedule_sample.csv",
            mime="text/csv"
        )
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        st.markdown("### 📊 Preview Uploaded Data")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Validate columns
        required_columns = ['Date', 'Time', 'Doctor', 'Specialty']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
        else:
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Appointments", len(df))
            with col2:
                booked = len(df[df['Patient Name'].notna()])
                st.metric("Booked Slots", booked)
            with col3:
                available = len(df[df['Patient Name'].isna()])
                st.metric("Available Slots", available)
            
            # Date range
            st.info(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
            
            # Import options
            st.markdown("### ⚙️ Import Options")
            
            col1, col2 = st.columns(2)
            with col1:
                overwrite = st.checkbox("Overwrite existing appointments", value=False)
            with col2:
                send_confirmations = st.checkbox("Send confirmation emails to patients", value=True)
            
            # Import button
            if st.button("🚀 Import Appointments", type="primary"):
                with st.spinner("Importing appointments..."):
                    db = FirebaseDB()
                    
                    success_count = 0
                    error_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, row in df.iterrows():
                        try:
                            # Prepare appointment data
                            appointment_data = {
                                'date': row['Date'],
                                'time': row['Time'],
                                'doctor': row['Doctor'],
                                'specialty': row['Specialty'],
                                'status': 'scheduled' if pd.notna(row.get('Patient Name')) else 'available',
                                'patient_name': row.get('Patient Name', ''),
                                'patient_email': row.get('Patient Email', ''),
                                'patient_phone': row.get('Patient Phone', ''),
                                'created_at': datetime.now().isoformat(),
                                'source': 'bulk_upload'
                            }
                            
                            # Add to database
                            apt_id = db.add_appointment(appointment_data)
                            
                            if apt_id:
                                success_count += 1
                            else:
                                error_count += 1
                        
                        except Exception as e:
                            error_count += 1
                            st.error(f"Error in row {idx + 1}: {str(e)}")
                        
                        # Update progress
                        progress = (idx + 1) / len(df)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {idx + 1} of {len(df)} appointments...")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Show results
                    st.success(f"""
                    ✅ Import Complete!
                    - Successfully imported: {success_count} appointments
                    - Errors: {error_count}
                    """)
                    
                    if send_confirmations and success_count > 0:
                        st.info("📧 Sending confirmation emails to patients...")
    
    # Manual entry option
    st.markdown("---")
    st.markdown("### ✏️ Manual Entry")
    
    with st.form("manual_appointment"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", min_value=datetime.now().date())
            time = st.time_input("Time")
            doctor = st.text_input("Doctor Name")
        
        with col2:
            specialties = ["Dermatology", "Rheumatology", "Cardiology", "Orthopedics", "General Practice"]
            specialty = st.selectbox("Specialty", specialties)
            duration = st.selectbox("Duration", ["30 minutes", "1 hour", "1.5 hours", "2 hours"])
        
        if st.form_submit_button("Add Appointment"):
            db = FirebaseDB()
            
            appointment_data = {
                'date': date.strftime("%Y-%m-%d"),
                'time': time.strftime("%I:%M %p"),
                'doctor': doctor,
                'specialty': specialty,
                'duration': duration,
                'status': 'available',
                'created_at': datetime.now().isoformat(),
                'source': 'manual_entry'
            }
            
            apt_id = db.add_appointment(appointment_data)
            
            if apt_id:
                st.success("✅ Appointment added successfully!")
            else:
                st.error("Error adding appointment. Please try again.")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.switch_page("pages/staff_dashboard.py")

if __name__ == "__main__":
    main()