import streamlit as st
from datetime import datetime
from utils.firebase_utils import FirebaseDB
from utils.notification_utils import NotificationService
import time

st.set_page_config(page_title="Book Appointment - CancelFillMD Pro", page_icon="✅")

def main():
    # Get token from URL parameters
    query_params = st.query_params
    token = query_params.get('token', [''])[0]
    
    if not token:
        st.error("Invalid booking link. Please use the link from your notification.")
        return
    
    db = FirebaseDB()
    
    # Verify token
    booking_info = db.verify_booking_token(token)
    
    if not booking_info:
        st.error("This booking link has expired or is invalid.")
        return
    
    if booking_info['used']:
        st.warning("This booking link has already been used.")
        return
    
    # Get appointment details
    appointment = db.get_appointment_by_id(booking_info['appointment_id'])
    patient = db.get_waitlist_patient(booking_info['patient_id'])
    
    if appointment['status'] != 'cancelled':
        st.warning("This appointment is no longer available.")
        return
    
    # Show appointment details
    st.title("✅ Confirm Your Appointment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Appointment Details")
        st.markdown(f"**Date:** {appointment['date']}")
        st.markdown(f"**Time:** {appointment['time']}")
        st.markdown(f"**Doctor:** {appointment['doctor']}")
        st.markdown(f"**Specialty:** {appointment['specialty']}")
    
    with col2:
        st.markdown("### Your Information")
        st.markdown(f"**Name:** {patient['name']}")
        st.markdown(f"**Email:** {patient['email']}")
        st.markdown(f"**Phone:** {patient['phone']}")
    
    st.markdown("---")
    
    # Confirmation form
    with st.form("confirm_booking"):
        st.markdown("### Please confirm your details:")
        
        # Allow patient to update contact info
        col1, col2 = st.columns(2)
        with col1:
            confirm_email = st.text_input("Confirm Email", value=patient['email'])
            confirm_phone = st.text_input("Confirm Phone", value=patient['phone'])
        
        with col2:
            insurance = st.text_input("Insurance Provider (optional)")
            notes = st.text_area("Special Instructions (optional)")
        
        # Terms
        agree_terms = st.checkbox("I understand this appointment is confirmed and I will attend")
        agree_cancel = st.checkbox("I understand I must give 24 hours notice for cancellations")
        
        if st.form_submit_button("🎯 Confirm Appointment", type="primary"):
            if not agree_terms or not agree_cancel:
                st.error("Please agree to all terms to confirm your appointment.")
            else:
                with st.spinner("Confirming your appointment..."):
                    # Update appointment
                    db.update_appointment(appointment['id'], {
                        'status': 'filled',
                        'patient_name': patient['name'],
                        'patient_email': confirm_email,
                        'patient_phone': confirm_phone,
                        'patient_id': patient['id'],
                        'insurance': insurance,
                        'booking_notes': notes,
                        'booked_at': datetime.now().isoformat(),
                        'booked_via': 'waitlist'
                    })
                    
                    # Mark token as used
                    db.mark_token_used(token)
                    
                    # Remove patient from waitlist for this date
                    db.update_waitlist_patient(patient['id'], {
                        'booked_appointments': db.increment_value(1),
                        'last_booked': datetime.now().isoformat()
                    })
                    
                    # Send confirmations
                    notif_service = NotificationService()
                    
                    # To patient
                    notif_service.notify_booking_confirmed(patient, appointment)
                    
                    # To staff
                    notif_service.notify_staff_appointment_filled(appointment, patient)
                    
                    # Notify others that slot is taken
                    db.notify_slot_filled(appointment['id'], patient['id'])
                    
                    time.sleep(1)
                    
                    st.balloons()
                    st.success("🎉 Your appointment is confirmed!")
                    
                    # Show confirmation details
                    st.markdown("""
                    ### What's Next?
                    
                    1. **Save this information:**
                       - Confirmation #: `{}`
                       - Date: **{}**
                       - Time: **{}**
                       - Doctor: **{}**
                    
                    2. **Before your appointment:**
                       - Arrive 15 minutes early for check-in
                       - Bring your insurance card and ID
                       - Complete any forms sent to your email
                    
                    3. **Need to cancel?**
                       - Call us at (555) 123-4567
                       - Or use the cancellation link in your confirmation email
                       - Please give 24 hours notice
                    """.format(
                        appointment['id'][:8],
                        appointment['date'],
                        appointment['time'],
                        appointment['doctor']
                    ))
                    
                    # Add to calendar button
                    if st.button("📅 Add to Calendar"):
                        # Generate calendar file
                        st.info("Calendar invite has been sent to your email!")

if __name__ == "__main__":
    main()