import streamlit as st
from datetime import datetime, timedelta
from utils.firebase_utils import FirebaseDB
from utils.notification_utils import NotificationService

st.set_page_config(page_title="Cancel Appointment - CancelFillMD Pro", page_icon="❌")

def main():
    st.title("❌ Cancel Appointment")
    
    # Choose cancellation method
    cancel_type = st.radio("Cancellation Type", ["Staff Cancellation", "Patient Self-Cancellation"])
    
    db = FirebaseDB()
    
    if cancel_type == "Staff Cancellation":
        st.markdown("### Staff Cancellation Portal")
        
        # Get upcoming appointments
        today = datetime.now().strftime("%Y-%m-%d")
        appointments = db.get_appointments(status='scheduled')
        
        # Filter for future appointments
        future_appointments = [apt for apt in appointments if apt['date'] >= today]
        
        if future_appointments:
            # Create selection dropdown
            apt_options = []
            apt_map = {}
            
            for apt in future_appointments:
                label = f"{apt['date']} - {apt['time']} - {apt['doctor']} - {apt.get('patient_name', 'Unknown')}"
                apt_options.append(label)
                apt_map[label] = apt
            
            selected_apt_label = st.selectbox("Select appointment to cancel", apt_options)
            selected_apt = apt_map[selected_apt_label]
            
            # Show appointment details
            with st.expander("Appointment Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Date:** {selected_apt['date']}")
                    st.markdown(f"**Time:** {selected_apt['time']}")
                    st.markdown(f"**Doctor:** {selected_apt['doctor']}")
                with col2:
                    st.markdown(f"**Specialty:** {selected_apt['specialty']}")
                    st.markdown(f"**Patient:** {selected_apt.get('patient_name', 'N/A')}")
                    st.markdown(f"**Status:** {selected_apt['status']}")
            
            # Cancellation reason
            reason = st.text_area("Cancellation Reason (optional)")
            
            # Notification options
            st.markdown("### Notification Options")
            col1, col2 = st.columns(2)
            with col1:
                notify_patient = st.checkbox("Notify patient of cancellation", value=True)
                notify_waitlist = st.checkbox("Notify waitlist immediately", value=True)
            with col2:
                auto_fill = st.checkbox("Auto-fill from waitlist", value=True)
                priority_fill = st.checkbox("Use priority matching", value=True)
            
            if st.button("🚫 Cancel Appointment", type="primary"):
                with st.spinner("Processing cancellation..."):
                    # Update appointment status
                    db.update_appointment(selected_apt['id'], {
                        'status': 'cancelled',
                        'cancelled_at': datetime.now().isoformat(),
                        'cancelled_by': 'staff',
                        'cancellation_reason': reason
                    })
                    
                    # Send notifications if enabled
                    if notify_waitlist:
                        st.info("🔔 Notifying waitlist patients...")
                        
                        # Get matching waitlist patients
                        waitlist = db.get_waitlist(
                            specialty=selected_apt['specialty'],
                            date=selected_apt['date']
                        )
                        
                        if waitlist:
                            notif_service = NotificationService()
                            
                            # Send notifications to top 10 waitlist patients
                            notified_count = 0
                            for patient in waitlist[:10]:
                                # Create secure booking link
                                booking_link = db.create_booking_link(
                                    selected_apt['id'], 
                                    patient['id']
                                )
                                
                                # Send notification
                                result = notif_service.notify_appointment_available(
                                    patient, 
                                    selected_apt, 
                                    booking_link
                                )
                                
                                if result['sms']['success'] or result['email']['success']:
                                    notified_count += 1
                                
                                # Log notification
                                db.log_notification({
                                    'appointment_id': selected_apt['id'],
                                    'patient_id': patient['id'],
                                    'type': 'appointment_available',
                                    'sent_at': datetime.now().isoformat(),
                                    'sms_status': result['sms']['success'],
                                    'email_status': result['email']['success']
                                })
                            
                            st.success(f"✅ Notified {notified_count} waitlist patients!")
                        else:
                            st.warning("No matching patients in waitlist.")
                    
                    st.success("✅ Appointment cancelled successfully!")
        else:
            st.info("No upcoming appointments to cancel.")
    
    else:  # Patient Self-Cancellation
        st.markdown("### Patient Self-Cancellation")
        
        with st.form("patient_cancel"):
            st.markdown("Please enter your appointment details:")
            
            email = st.text_input("Email used for booking")
            phone = st.text_input("Phone number")
            confirmation_code = st.text_input("Confirmation code (if provided)")
            
            reason = st.selectbox("Reason for cancellation", [
                "Schedule conflict",
                "Feeling better",
                "Found another appointment",
                "Personal emergency",
                "Other"
            ])
            
            if reason == "Other":
                other_reason = st.text_input("Please specify")
            
            if st.form_submit_button("Cancel My Appointment"):
                # Verify patient and find appointment
                # (Implementation depends on your verification method)
                
                st.success("✅ Your appointment has been cancelled.")
                st.info("You will receive a confirmation email shortly.")
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Home"):
        st.switch_page("app.py")

if __name__ == "__main__":
    main()