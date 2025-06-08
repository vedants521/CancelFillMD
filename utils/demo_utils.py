# utils/demo_utils.py
"""
Demo utilities for generating realistic demo data and scenarios
"""
import random
from datetime import datetime, timedelta, date, time
from typing import List, Dict, Tuple
import names  # You may need to install: pip install names

class DemoDataGenerator:
    """Generate realistic demo data for presentations"""
    
    # Common medical specialties
    SPECIALTIES = [
        'Dermatology', 'Rheumatology', 'Cardiology', 'Orthopedics',
        'Neurology', 'Gastroenterology', 'Endocrinology', 'Pulmonology'
    ]
    
    # Common cancellation reasons
    CANCELLATION_REASONS = [
        'Personal emergency',
        'Work conflict',
        'Feeling better',
        'Transportation issues',
        'Insurance issues',
        'Scheduling conflict',
        'Family emergency',
        'Weather conditions'
    ]
    
    # Insurance providers
    INSURANCE_PROVIDERS = [
        'Blue Cross Blue Shield',
        'Aetna',
        'UnitedHealth',
        'Cigna',
        'Humana',
        'Kaiser Permanente',
        'Anthem',
        'Medicare'
    ]
    
    @staticmethod
    def generate_patient() -> Dict:
        """Generate a realistic patient record"""
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        
        # Generate email from name
        email_providers = ['gmail.com', 'yahoo.com', 'outlook.com', 'email.com']
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(email_providers)}"
        
        # Generate phone number
        area_codes = ['415', '510', '650', '408', '925', '707', '831', '209']
        phone = f"+1{random.choice(area_codes)}{random.randint(1000000, 9999999)}"
        
        # Generate preferences
        num_dates = random.randint(2, 5)
        preferred_dates = []
        for i in range(num_dates):
            future_date = date.today() + timedelta(days=random.randint(1, 30))
            preferred_dates.append(future_date.strftime('%Y-%m-%d'))
        
        time_preferences = random.choice([
            ['morning'],
            ['afternoon'],
            ['morning', 'afternoon'],
            ['afternoon', 'evening'],
            ['any']
        ])
        
        return {
            'name': f"{first_name} {last_name}",
            'email': email,
            'phone': phone,
            'specialty': random.choice(DemoDataGenerator.SPECIALTIES),
            'preferred_dates': preferred_dates,
            'time_preferences': time_preferences,
            'insurance_provider': random.choice(DemoDataGenerator.INSURANCE_PROVIDERS),
            'insurance_id': f"{random.choice(['A', 'B', 'C'])}{random.randint(10000000, 99999999)}",
            'created_at': (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
            'active': True,
            'notified_count': random.randint(0, 3)
        }
    
    @staticmethod
    def generate_appointment(date_obj: date, time_slot: str, doctor: str, specialty: str) -> Dict:
        """Generate a realistic appointment record"""
        # 70% chance of being booked
        is_booked = random.random() < 0.7
        
        appointment = {
            'date': date_obj.strftime('%Y-%m-%d'),
            'time': time_slot,
            'doctor': doctor,
            'specialty': specialty,
            'duration': random.choice(['30 minutes', '1 hour']),
            'status': 'scheduled' if is_booked else 'available',
            'created_at': (datetime.now() - timedelta(days=random.randint(7, 30))).isoformat()
        }
        
        if is_booked:
            patient = DemoDataGenerator.generate_patient()
            appointment.update({
                'patient_name': patient['name'],
                'patient_email': patient['email'],
                'patient_phone': patient['phone'],
                'insurance_provider': patient['insurance_provider'],
                'insurance_id': patient['insurance_id']
            })
        
        return appointment
    
    @staticmethod
    def generate_schedule(start_date: date, num_days: int = 7) -> List[Dict]:
        """Generate a full appointment schedule"""
        appointments = []
        
        doctors = [
            ('Dr. Sarah Johnson', 'Dermatology'),
            ('Dr. Michael Chen', 'Rheumatology'),
            ('Dr. Emily Williams', 'Cardiology'),
            ('Dr. James Martinez', 'Orthopedics')
        ]
        
        time_slots = [
            '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
            '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM'
        ]
        
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            for doctor, specialty in doctors:
                for time_slot in time_slots:
                    # Random chance to skip slot (doctor availability)
                    if random.random() < 0.1:
                        continue
                    
                    appointment = DemoDataGenerator.generate_appointment(
                        current_date, time_slot, doctor, specialty
                    )
                    appointments.append(appointment)
        
        return appointments
    
    @staticmethod
    def generate_waitlist(size: int = 50) -> List[Dict]:
        """Generate a waitlist of patients"""
        return [DemoDataGenerator.generate_patient() for _ in range(size)]
    
    @staticmethod
    def generate_historical_data(days: int = 30) -> List[Dict]:
        """Generate historical appointment data for analytics"""
        history = []
        
        for day_offset in range(days):
            date_obj = date.today() - timedelta(days=day_offset)
            
            # Skip weekends
            if date_obj.weekday() >= 5:
                continue
            
            # Generate daily statistics
            total_appointments = random.randint(80, 120)
            cancelled = random.randint(8, 15)
            
            # Fill rate increases over time (showing improvement)
            base_fill_rate = 0.4 + (days - day_offset) * 0.01  # Gradual improvement
            fill_rate = min(0.85, base_fill_rate + random.uniform(-0.1, 0.1))
            filled = int(cancelled * fill_rate)
            
            # Calculate metrics
            revenue_per_appointment = random.randint(200, 350)
            revenue_recovered = filled * revenue_per_appointment
            revenue_lost = (cancelled - filled) * revenue_per_appointment
            
            # Average fill time decreases over time (showing improvement)
            base_fill_time = 60 - (days - day_offset) * 0.5
            avg_fill_time = max(15, base_fill_time + random.randint(-10, 10))
            
            history.append({
                'date': date_obj.strftime('%Y-%m-%d'),
                'total_appointments': total_appointments,
                'cancelled': cancelled,
                'filled': filled,
                'no_shows': random.randint(0, 3),
                'fill_rate': round(fill_rate * 100, 1),
                'revenue_recovered': revenue_recovered,
                'revenue_lost': revenue_lost,
                'avg_fill_time_minutes': avg_fill_time,
                'notifications_sent': filled * random.randint(3, 8),
                'waitlist_size': random.randint(40, 80)
            })
        
        return history
    
    @staticmethod
    def generate_notification_log(num_entries: int = 20) -> List[Dict]:
        """Generate notification history"""
        notifications = []
        
        for i in range(num_entries):
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            notification_type = random.choice(['sms', 'email', 'both'])
            status = random.choice(['sent', 'delivered', 'opened', 'clicked', 'booked'])
            
            notifications.append({
                'timestamp': timestamp.isoformat(),
                'type': notification_type,
                'recipient': DemoDataGenerator.generate_patient()['name'],
                'appointment_date': (timestamp + timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d'),
                'appointment_time': random.choice(['9:00 AM', '10:00 AM', '2:00 PM', '3:00 PM']),
                'specialty': random.choice(DemoDataGenerator.SPECIALTIES),
                'status': status,
                'response_time_minutes': random.randint(5, 120) if status == 'booked' else None
            })
        
        return sorted(notifications, key=lambda x: x['timestamp'], reverse=True)

class DemoScenarios:
    """Pre-configured demo scenarios for presentations"""
    
    @staticmethod
    def morning_cancellation_rush() -> Dict:
        """Scenario: Multiple morning cancellations"""
        current_date = date.today()
        
        cancellations = [
            {
                'time': '9:00 AM',
                'doctor': 'Dr. Sarah Johnson',
                'specialty': 'Dermatology',
                'original_patient': 'John Smith',
                'reason': 'Personal emergency'
            },
            {
                'time': '10:00 AM',
                'doctor': 'Dr. Sarah Johnson',
                'specialty': 'Dermatology',
                'original_patient': 'Mary Davis',
                'reason': 'Feeling better'
            },
            {
                'time': '11:00 AM',
                'doctor': 'Dr. Michael Chen',
                'specialty': 'Rheumatology',
                'original_patient': 'Robert Wilson',
                'reason': 'Transportation issues'
            }
        ]
        
        # Generate matching waitlist patients
        waitlist_matches = []
        for cancellation in cancellations:
            matches = []
            for i in range(random.randint(3, 8)):
                patient = DemoDataGenerator.generate_patient()
                patient['specialty'] = cancellation['specialty']
                patient['preferred_dates'] = [current_date.strftime('%Y-%m-%d')]
                patient['match_score'] = random.randint(70, 95)
                matches.append(patient)
            
            waitlist_matches.append({
                'appointment': cancellation,
                'matches': sorted(matches, key=lambda x: x['match_score'], reverse=True)
            })
        
        return {
            'scenario_name': 'Morning Cancellation Rush',
            'description': 'Three morning cancellations need to be filled quickly',
            'cancellations': cancellations,
            'waitlist_matches': waitlist_matches,
            'expected_outcome': {
                'fill_rate': 100,
                'avg_fill_time': 18,
                'revenue_recovered': 750
            }
        }
    
    @staticmethod
    def weekly_performance_review() -> Dict:
        """Scenario: Weekly performance metrics"""
        return {
            'scenario_name': 'Weekly Performance Review',
            'description': 'Review of last week\'s appointment management performance',
            'metrics': {
                'total_appointments': 480,
                'cancellations': 42,
                'filled': 36,
                'fill_rate': 85.7,
                'revenue_recovered': 9000,
                'revenue_lost': 1500,
                'avg_fill_time': 22,
                'staff_hours_saved': 87.5,
                'patient_satisfaction': 4.8
            },
            'department_breakdown': [
                {'department': 'Dermatology', 'cancellations': 15, 'filled': 14, 'fill_rate': 93.3},
                {'department': 'Rheumatology', 'cancellations': 12, 'filled': 10, 'fill_rate': 83.3},
                {'department': 'Cardiology', 'cancellations': 8, 'filled': 7, 'fill_rate': 87.5},
                {'department': 'Orthopedics', 'cancellations': 7, 'filled': 5, 'fill_rate': 71.4}
            ],
            'recommendations': [
                'Increase Orthopedics waitlist by 20%',
                'Enable double-booking for Tuesday afternoons',
                'Send reminder SMS 48 hours before high-risk appointments'
            ]
        }
    
    @staticmethod
    def roi_demonstration() -> Dict:
        """Scenario: ROI calculation demonstration"""
        practice_size = 'medium'  # small, medium, large
        
        scenarios = {
            'small': {
                'monthly_appointments': 800,
                'cancellation_rate': 0.12,
                'current_fill_rate': 0.15,
                'avg_appointment_value': 200
            },
            'medium': {
                'monthly_appointments': 2000,
                'cancellation_rate': 0.10,
                'current_fill_rate': 0.10,
                'avg_appointment_value': 250
            },
            'large': {
                'monthly_appointments': 5000,
                'cancellation_rate': 0.08,
                'current_fill_rate': 0.08,
                'avg_appointment_value': 300
            }
        }
        
        data = scenarios[practice_size]
        monthly_cancellations = data['monthly_appointments'] * data['cancellation_rate']
        
        current_recovery = monthly_cancellations * data['current_fill_rate'] * data['avg_appointment_value']
        projected_recovery = monthly_cancellations * 0.84 * data['avg_appointment_value']  # 84% fill rate
        additional_revenue = projected_recovery - current_recovery
        
        return {
            'scenario_name': 'ROI Demonstration',
            'description': f'Financial impact for a {practice_size} practice',
            'inputs': data,
            'calculations': {
                'monthly_cancellations': int(monthly_cancellations),
                'current_monthly_recovery': round(current_recovery, 2),
                'projected_monthly_recovery': round(projected_recovery, 2),
                'additional_monthly_revenue': round(additional_revenue, 2),
                'additional_annual_revenue': round(additional_revenue * 12, 2),
                'roi_percentage': round((additional_revenue * 12 / 6000) * 100, 1)  # Assuming $500/month cost
            }
        }

# Demo mode helpers
def reset_demo_database(db_reference):
    """Reset database with fresh demo data"""
    # Clear existing data
    db_reference.delete()
    
    # Generate new demo data
    print("Generating demo patients...")
    waitlist = DemoDataGenerator.generate_waitlist(75)
    for patient in waitlist:
        db_reference.child('waitlist').push(patient)
    
    print("Generating appointment schedule...")
    schedule = DemoDataGenerator.generate_schedule(date.today(), 14)
    for appointment in schedule:
        db_reference.child('appointments').push(appointment)
    
    print("Generating historical data...")
    history = DemoDataGenerator.generate_historical_data(30)
    for entry in history:
        db_reference.child('analytics').push(entry)
    
    print("Demo database reset complete!")

def create_demo_snapshot(db_reference) -> Dict:
    """Create a snapshot of current data for demo rollback"""
    return {
        'timestamp': datetime.now().isoformat(),
        'waitlist': db_reference.child('waitlist').get(),
        'appointments': db_reference.child('appointments').get(),
        'analytics': db_reference.child('analytics').get()
    }

def restore_demo_snapshot(db_reference, snapshot: Dict):
    """Restore database to a previous snapshot"""
    db_reference.delete()
    
    if snapshot.get('waitlist'):
        db_reference.child('waitlist').set(snapshot['waitlist'])
    
    if snapshot.get('appointments'):
        db_reference.child('appointments').set(snapshot['appointments'])
    
    if snapshot.get('analytics'):
        db_reference.child('analytics').set(snapshot['analytics'])
    
    print(f"Restored snapshot from {snapshot['timestamp']}")