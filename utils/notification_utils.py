# utils/notification_utils.py
"""
Notification utilities for sending SMS and Email notifications
"""
import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
import streamlit as st

class NotificationService:
    """Handle all notification sending (SMS and Email)"""
    
    def __init__(self):
        # Initialize Twilio
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Initialize SendGrid
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.sender_email = os.getenv("SENDER_EMAIL")
        
        # Initialize clients only if credentials are available
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except Exception as e:
                print(f"Failed to initialize Twilio: {e}")
                self.twilio_client = None
        else:
            self.twilio_client = None
            
        if self.sendgrid_api_key:
            try:
                self.sg_client = SendGridAPIClient(self.sendgrid_api_key)
            except Exception as e:
                print(f"Failed to initialize SendGrid: {e}")
                self.sg_client = None
        else:
            self.sg_client = None
    
    def send_sms(self, to_number, message):
        """Send SMS notification"""
        if not self.twilio_client:
            return False, "SMS service not configured"
        
        try:
            # Ensure message is not too long
            if len(message) > 160:
                message = message[:157] + "..."
            
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to_number
            )
            
            return True, message_obj.sid
            
        except Exception as e:
            return False, str(e)
    
    def send_email(self, to_email, subject, html_content):
        """Send email notification"""
        if not self.sg_client:
            return False, "Email service not configured"
        
        try:
            message = Mail(
                from_email=self.sender_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sg_client.send(message)
            
            return True, response.status_code
            
        except Exception as e:
            return False, str(e)
    
    def notify_appointment_available(self, patient, appointment, booking_link):
        """Notify patient about available appointment"""
        clinic_name = os.getenv("CLINIC_NAME", "Medical Center")
        
        # SMS Message
        sms_message = f"{clinic_name}: Appointment available on {appointment.get('date')} at {appointment.get('time')} with {appointment.get('doctor')}. Book now: {booking_link} (expires in 2 hours)"
        
        # Email HTML
        email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Appointment Available!</h2>
                
                <p>Dear {patient.get('name')},</p>
                
                <p>Good news! An appointment has become available that matches your preferences:</p>
                
                <div style="background-color: #f0f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Date:</strong> {appointment.get('date')}</p>
                    <p><strong>Time:</strong> {appointment.get('time')}</p>
                    <p><strong>Doctor:</strong> {appointment.get('doctor')}</p>
                    <p><strong>Specialty:</strong> {appointment.get('specialty')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{booking_link}" style="background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Book This Appointment</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">This link will expire in 2 hours. First come, first served.</p>
                
                <hr style="border: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    If you no longer wish to receive these notifications, 
                    please reply STOP to any SMS or contact us at {self.sender_email}
                </p>
            </div>
        </body>
        </html>
        """
        
        # Send notifications
        sms_result = self.send_sms(patient.get('phone'), sms_message)
        email_result = self.send_email(
            patient.get('email'), 
            f"Appointment Available - {appointment.get('date')} at {appointment.get('time')}", 
            email_html
        )
        
        return {
            'sms': {'success': sms_result[0], 'result': sms_result[1]},
            'email': {'success': email_result[0], 'result': email_result[1]}
        }
    
    def notify_booking_confirmed(self, patient, appointment):
        """Send booking confirmation to patient"""
        clinic_name = os.getenv("CLINIC_NAME", "Medical Center")
        
        sms_message = f"{clinic_name}: Your appointment is confirmed for {appointment.get('date')} at {appointment.get('time')} with {appointment.get('doctor')}. Please arrive 15 minutes early."
        
        return self.send_sms(patient.get('phone'), sms_message)
    
    def notify_staff_appointment_filled(self, appointment, patient):
        """Notify staff that appointment was filled"""
        staff_email = os.getenv("STAFF_NOTIFICATION_EMAIL", self.sender_email)
        
        email_html = f"""
        <html>
        <body>
            <h3>Appointment Filled via Waitlist</h3>
            <p>The following cancelled appointment has been filled:</p>
            <ul>
                <li><strong>Date:</strong> {appointment.get('date')}</li>
                <li><strong>Time:</strong> {appointment.get('time')}</li>
                <li><strong>Doctor:</strong> {appointment.get('doctor')}</li>
                <li><strong>New Patient:</strong> {patient.get('name')}</li>
                <li><strong>Phone:</strong> {patient.get('phone')}</li>
                <li><strong>Email:</strong> {patient.get('email')}</li>
            </ul>
            <p>Please update the appointment in your system.</p>
        </body>
        </html>
        """
        
        return self.send_email(
            staff_email,
            f"Appointment Filled - {appointment.get('date')} at {appointment.get('time')}",
            email_html
        )
    
    def send_appointment_reminder(self, patient, appointment, hours_before):
        """Send appointment reminder"""
        clinic_name = os.getenv("CLINIC_NAME", "Medical Center")
        
        sms_message = f"{clinic_name} Reminder: Your appointment is in {hours_before} hours - {appointment.get('date')} at {appointment.get('time')} with {appointment.get('doctor')}."
        
        email_html = f"""
        <html>
        <body>
            <h2>Appointment Reminder</h2>
            <p>Dear {patient.get('name')},</p>
            <p>This is a reminder that you have an appointment in {hours_before} hours:</p>
            <ul>
                <li><strong>Date:</strong> {appointment.get('date')}</li>
                <li><strong>Time:</strong> {appointment.get('time')}</li>
                <li><strong>Doctor:</strong> {appointment.get('doctor')}</li>
            </ul>
            <p>Please arrive 15 minutes early for check-in.</p>
            <p>If you need to cancel or reschedule, please call us at (555) 123-4567.</p>
        </body>
        </html>
        """
        
        sms_result = self.send_sms(patient.get('phone'), sms_message)
        email_result = self.send_email(
            patient.get('email'),
            f"Appointment Reminder - {appointment.get('date')} at {appointment.get('time')}",
            email_html
        )
        
        return {
            'sms': sms_result,
            'email': email_result
        }
