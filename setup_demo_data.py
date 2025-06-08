# setup_demo_data.py
"""
Script to set up demo data for CancelFillMD Pro
Run this to populate your Firebase database with realistic demo data
"""
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta, date
import random
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Demo patient names and data
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
    "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
]

INSURANCE_PROVIDERS = [
    "Blue Cross Blue Shield", "Aetna", "UnitedHealth", "Cigna", "Humana",
    "Kaiser Permanente", "Anthem", "Medicare", "Medicaid", "Tricare"
]

CANCELLATION_REASONS = [
    "Personal emergency", "Work conflict", "Feeling better", "Transportation issues",
    "Insurance issues", "Scheduling conflict", "Family emergency", "Weather conditions",
    "Found another appointment", "Financial reasons"
]

class DemoDataGenerator:
    def __init__(self, db_reference):
        self.db = db_reference
        self.generated_emails = set()
        self.generated_phones = set()
        
    def generate_unique_email(self, first_name, last_name):
        """Generate unique email address"""
        base_email = f"{first_name.lower()}.{last_name.lower()}"
        providers = ["gmail.com", "yahoo.com", "outlook.com", "email.com", "mail.com"]
        
        email = f"{base_email}@{random.choice(providers)}"
        counter = 1
        
        while email in self.generated_emails:
            email = f"{base_email}{counter}@{random.choice(providers)}"
            counter += 1
        
        self.generated_emails.add(email)
        return email
    
    def generate_unique_phone(self):
        """Generate unique phone number"""
        area_codes = ["415", "510", "650", "408", "925", "707", "831", "209", "916", "530"]
        
        while True:
            phone = f"+1{random.choice(area_codes)}{random.randint(1000000, 9999999)}"
            if phone not in self.generated_phones:
                self.generated_phones.add(phone)
                return phone
    
    def generate_patient(self):
        """Generate a realistic patient record"""
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
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
            'email': self.generate_unique_email(first_name, last_name),
            'phone': self.generate_unique_phone(),
            'specialty': random.choice(['Dermatology', 'Rheumatology', 'Cardiology', 'Orthopedics']),
            'preferred_dates': preferred_dates,
            'time_preferences': time_preferences,
            'insurance_provider': random.choice(INSURANCE_PROVIDERS),
            'insurance_id': f"{random.choice(['A', 'B', 'C'])}{random.randint(10000000, 99999999)}",
            'created_at': (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
            'active': True,
            'notified_count': random.randint(0, 3)
        }
    
    def generate_appointments(self, num_days=14):
        """Generate appointment schedule"""
        appointments = []
        
        doctors = [
            ('Dr. Sarah Johnson', 'Dermatology'),
            ('Dr. Michael Chen', 'Rheumatology'),
            ('Dr. Emily Williams', 'Cardiology'),
            ('Dr. James Martinez', 'Orthopedics'),
            ('Dr. Lisa Anderson', 'Dermatology'),
            ('Dr. Robert Taylor', 'Cardiology')
        ]
        
        time_slots = [
            '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM',
            '11:00 AM', '11:30 AM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
            '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM'
        ]
        
        for day_offset in range(num_days):
            current_date = date.today() + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            for doctor, specialty in doctors:
                # Random subset of time slots for each doctor
                doctor_slots = random.sample(time_slots, random.randint(10, 14))
                
                for time_slot in doctor_slots:
                    # 70% chance of being booked
                    is_booked = random.random() < 0.7
                    
                    appointment = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'time': time_slot,
                        'doctor': doctor,
                        'specialty': specialty,
                        'duration': random.choice(['30 minutes', '45 minutes', '1 hour']),
                        'status': 'scheduled' if is_booked else 'available',
                        'created_at': (datetime.now() - timedelta(days=random.randint(7, 30))).isoformat()
                    }
                    
                    if is_booked:
                        patient = self.generate_patient()
                        appointment.update({
                            'patient_name': patient['name'],
                            'patient_email': patient['email'],
                            'patient_phone': patient['phone'],
                            'insurance_provider': patient['insurance_provider'],
                            'insurance_id': patient['insurance_id']
                        })
                    
                    appointments.append(appointment)
        
        return appointments
    
    def generate_historical_data(self, num_days=30):
        """Generate historical analytics data"""
        history = []
        
        for day_offset in range(num_days):
            current_date = date.today() - timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Generate daily statistics
            total_appointments = random.randint(80, 120)
            cancelled = random.randint(8, 15)
            
            # Fill rate improves over time
            base_fill_rate = 0.4 + (num_days - day_offset) * 0.01
            fill_rate = min(0.85, base_fill_rate + random.uniform(-0.1, 0.1))
            filled = int(cancelled * fill_rate)
            
            # Calculate metrics
            revenue_per_appointment = random.randint(200, 350)
            revenue_recovered = filled * revenue_per_appointment
            revenue_lost = (cancelled - filled) * revenue_per_appointment
            
            # Average fill time decreases over time
            base_fill_time = 60 - (num_days - day_offset) * 0.5
            avg_fill_time = max(15, base_fill_time + random.randint(-10, 10))
            
            daily_stats = {
                'date': current_date.strftime('%Y-%m-%d'),
                'total_appointments': total_appointments,
                'cancelled': cancelled,
                'filled': filled,
                'no_shows': random.randint(0, 3),
                'fill_rate': round(fill_rate * 100, 1),
                'revenue_recovered': revenue_recovered,
                'revenue_lost': revenue_lost,
                'avg_fill_time_minutes': round(avg_fill_time, 0),
                'notifications_sent': filled * random.randint(3, 8),
                'waitlist_size': random.randint(40, 80),
                'staff_hours_saved': round(filled * 2.5 / 60, 1)
            }
            
            history.append(daily_stats)
        
        return history
    
    def simulate_cancellations(self, appointments):
        """Simulate some cancellations in the schedule"""
        scheduled_appointments = [apt for apt in appointments 
                                if apt['status'] == 'scheduled' 
                                and apt['date'] >= date.today().strftime('%Y-%m-%d')]
        
        # Cancel 10-15% of future appointments
        num_to_cancel = random.randint(
            int(len(scheduled_appointments) * 0.1),
            int(len(scheduled_appointments) * 0.15)
        )
        
        to_cancel = random.sample(scheduled_appointments, num_to_cancel)
        
        for apt in to_cancel:
            apt['status'] = 'cancelled'
            apt['cancelled_at'] = datetime.now().isoformat()
            apt['cancellation_reason'] = random.choice(CANCELLATION_REASONS)
            apt['cancelled_by'] = random.choice(['patient', 'staff'])
        
        # Fill some of the cancelled appointments
        cancelled = [apt for apt in appointments if apt['status'] == 'cancelled']
        num_to_fill = int(len(cancelled) * 0.3)  # Fill 30% immediately
        
        to_fill = random.sample(cancelled, num_to_fill)
        
        for apt in to_fill:
            # Generate new patient for filled slot
            new_patient = self.generate_patient()
            apt['status'] = 'filled'
            apt['filled_at'] = (datetime.fromisoformat(apt['cancelled_at']) + 
                               timedelta(minutes=random.randint(10, 60))).isoformat()
            apt['original_patient'] = apt.get('patient_name', 'Unknown')
            apt['patient_name'] = new_patient['name']
            apt['patient_email'] = new_patient['email']
            apt['patient_phone'] = new_patient['phone']

def setup_demo_database():
    """Main function to set up demo database"""
    print("🚀 Starting CancelFillMD Pro demo data setup...")
    
    # Initialize Firebase
    try:
        if not firebase_admin._apps:
            # Try to use service account file
            if os.path.exists('firebase-key.json'):
                cred = credentials.Certificate('firebase-key.json')
            else:
                # Use environment variable
                firebase_config = json.loads(os.getenv('FIREBASE_CONFIG', '{}'))
                cred = credentials.Certificate(firebase_config)
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_URL', 'https://cancelfillmd-demo-default-rtdb.firebaseio.com/')
            })
        
        db_ref = db.reference()
        
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        print("Please check your Firebase configuration.")
        return
    
    # Clear existing data
    print("🗑️  Clearing existing data...")
    db_ref.delete()
    
    # Initialize generator
    generator = DemoDataGenerator(db_ref)
    
    # Generate waitlist patients
    print("👥 Generating waitlist patients...")
    waitlist_size = 75
    waitlist_patients = []
    
    for i in range(waitlist_size):
        patient = generator.generate_patient()
        waitlist_ref = db_ref.child('waitlist').push(patient)
        waitlist_patients.append((waitlist_ref.key, patient))
        
        if (i + 1) % 10 == 0:
            print(f"   Generated {i + 1}/{waitlist_size} patients...")
    
    print(f"✅ Created {waitlist_size} waitlist patients")
    
    # Generate appointments
    print("📅 Generating appointment schedule...")
    appointments = generator.generate_appointments(num_days=14)
    
    # Simulate cancellations and fills
    generator.simulate_cancellations(appointments)
    
    # Save appointments to database
    for apt in appointments:
        db_ref.child('appointments').push(apt)
    
    print(f"✅ Created {len(appointments)} appointments")
    
    # Count statistics
    scheduled = len([a for a in appointments if a['status'] == 'scheduled'])
    cancelled = len([a for a in appointments if a['status'] == 'cancelled'])
    filled = len([a for a in appointments if a['status'] == 'filled'])
    available = len([a for a in appointments if a['status'] == 'available'])
    
    print(f"   - Scheduled: {scheduled}")
    print(f"   - Cancelled: {cancelled}")
    print(f"   - Filled: {filled}")
    print(f"   - Available: {available}")
    
    # Generate historical analytics data
    print("📊 Generating historical analytics data...")
    history = generator.generate_historical_data(num_days=30)
    
    for entry in history:
        db_ref.child('analytics').child('daily_stats').push(entry)
    
    print(f"✅ Created {len(history)} days of historical data")
    
    # Generate notification logs
    print("🔔 Generating notification history...")
    notifications = []
    
    for i in range(50):
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        notification = {
            'timestamp': timestamp.isoformat(),
            'type': random.choice(['sms', 'email', 'both']),
            'recipient_name': random.choice([p[1]['name'] for p in waitlist_patients[:20]]),
            'recipient_email': random.choice([p[1]['email'] for p in waitlist_patients[:20]]),
            'appointment_date': (timestamp + timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d'),
            'appointment_time': random.choice(['9:00 AM', '10:00 AM', '2:00 PM', '3:00 PM']),
            'specialty': random.choice(['Dermatology', 'Rheumatology', 'Cardiology', 'Orthopedics']),
            'status': random.choice(['sent', 'delivered', 'opened', 'clicked', 'booked']),
            'response_time_minutes': random.randint(5, 120) if random.random() > 0.5 else None
        }
        
        notifications.append(notification)
        db_ref.child('notifications').push(notification)
    
    print(f"✅ Created {len(notifications)} notification logs")
    
    # Create demo accounts
    print("👤 Setting up demo accounts...")
    demo_accounts = {
        'demo_admin': {
            'username': 'demo_admin',
            'password_hash': 'demo_hash_admin',  # In production, use proper hashing
            'role': 'Administrator',
            'full_name': 'Admin Demo',
            'email': 'admin@cancelfillmd-demo.com',
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat()
        },
        'demo_manager': {
            'username': 'demo_manager',
            'password_hash': 'demo_hash_manager',
            'role': 'Practice Manager',
            'full_name': 'Manager Demo',
            'email': 'manager@cancelfillmd-demo.com',
            'created_at': datetime.now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=2)).isoformat()
        },
        'demo_staff': {
            'username': 'demo_staff',
            'password_hash': 'demo_hash_staff',
            'role': 'Staff Member',
            'full_name': 'Staff Demo',
            'email': 'staff@cancelfillmd-demo.com',
            'created_at': datetime.now().isoformat(),
            'last_login': (datetime.now() - timedelta(days=1)).isoformat()
        }
    }
    
    for username, account_data in demo_accounts.items():
        db_ref.child('users').child(username).set(account_data)
    
    print("✅ Created demo user accounts")
    
    # Create system configuration
    print("⚙️  Setting up system configuration...")
    system_config = {
        'clinic': {
            'name': 'Demo Medical Center',
            'email': 'info@demo-medical.com',
            'phone': '(555) 123-4567',
            'address': '123 Medical Center Dr\nSuite 100\nDemo City, ST 12345',
            'timezone': 'America/New_York'
        },
        'business_hours': {
            'monday': {'open': '08:00', 'close': '17:00'},
            'tuesday': {'open': '08:00', 'close': '17:00'},
            'wednesday': {'open': '08:00', 'close': '17:00'},
            'thursday': {'open': '08:00', 'close': '17:00'},
            'friday': {'open': '08:00', 'close': '17:00'},
            'saturday': {'open': '09:00', 'close': '13:00'},
            'sunday': None
        },
        'features': {
            'sms_enabled': True,
            'email_enabled': True,
            'auto_fill_enabled': True,
            'waitlist_enabled': True
        },
        'demo_mode': True,
        'last_reset': datetime.now().isoformat()
    }
    
    db_ref.child('config').set(system_config)
    print("✅ System configuration set")
    
    # Generate some "today" appointments for demo
    print("🎯 Creating today's appointments for live demo...")
    today = date.today()
    today_appointments = []
    
    doctors_today = [
        ('Dr. Sarah Johnson', 'Dermatology'),
        ('Dr. Michael Chen', 'Rheumatology')
    ]
    
    times_today = ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM', '4:00 PM']
    
    for doctor, specialty in doctors_today:
        for time_slot in times_today:
            apt = {
                'date': today.strftime('%Y-%m-%d'),
                'time': time_slot,
                'doctor': doctor,
                'specialty': specialty,
                'duration': '1 hour',
                'status': 'scheduled',
                'created_at': (datetime.now() - timedelta(days=7)).isoformat()
            }
            
            # Make some appointments cancellable for demo
            if time_slot in ['10:00 AM', '2:00 PM', '3:00 PM']:
                patient = generator.generate_patient()
                apt.update({
                    'patient_name': patient['name'],
                    'patient_email': patient['email'],
                    'patient_phone': patient['phone'],
                    'demo_cancellable': True  # Flag for demo
                })
            
            db_ref.child('appointments').push(apt)
            today_appointments.append(apt)
    
    print(f"✅ Created {len(today_appointments)} appointments for today's demo")
    
    # Create summary statistics
    print("📈 Calculating summary statistics...")
    
    total_patients = waitlist_size
    total_appointments = len(appointments)
    total_revenue_recovered = sum(entry['revenue_recovered'] for entry in history)
    total_hours_saved = sum(entry['staff_hours_saved'] for entry in history)
    avg_fill_rate = sum(entry['fill_rate'] for entry in history) / len(history)
    
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_waitlist_patients': total_patients,
        'total_appointments': total_appointments,
        'total_revenue_recovered_30d': total_revenue_recovered,
        'total_hours_saved_30d': total_hours_saved,
        'average_fill_rate_30d': round(avg_fill_rate, 1),
        'demo_accounts': {
            'admin': 'demo_admin / DemoPass2025',
            'manager': 'demo_manager / ManagerDemo2025',
            'staff': 'demo_staff / StaffDemo2025'
        }
    }
    
    db_ref.child('demo_summary').set(summary)
    
    # Print summary
    print("\n" + "="*60)
    print("✅ DEMO DATA SETUP COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   - Waitlist Patients: {total_patients}")
    print(f"   - Total Appointments: {total_appointments}")
    print(f"   - Historical Data: {len(history)} days")
    print(f"   - Notifications: {len(notifications)}")
    print(f"   - Revenue Recovered (30d): ${total_revenue_recovered:,.0f}")
    print(f"   - Staff Hours Saved (30d): {total_hours_saved:.0f}")
    print(f"   - Average Fill Rate: {avg_fill_rate:.1f}%")
    print(f"\n👤 Demo Accounts:")
    print(f"   - Admin: demo_admin / DemoPass2025")
    print(f"   - Manager: demo_manager / ManagerDemo2025")
    print(f"   - Staff: demo_staff / StaffDemo2025")
    print(f"\n🔗 Demo URL: {os.getenv('APP_URL', 'http://localhost:8501')}")
    print("\n" + "="*60)

def reset_demo_data():
    """Quick function to reset demo data"""
    print("🔄 Resetting demo data...")
    setup_demo_database()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_demo_data()
    else:
        setup_demo_database()