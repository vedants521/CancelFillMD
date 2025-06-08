# User Guide - CancelFillMD Pro

## Table of Contents
1. [Getting Started](#getting-started)
2. [For Patients](#for-patients)
3. [For Staff](#for-staff)
4. [For Managers](#for-managers)
5. [For Administrators](#for-administrators)
6. [Common Workflows](#common-workflows)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Login

1. **Navigate to the Application**
   - Open your web browser
   - Go to: `https://your-clinic.cancelfillmd.app`
   - Bookmark the page for easy access

2. **Staff Login**
   - Click "Staff Dashboard"
   - Enter your username and password
   - Click "Login"

3. **Patient Access**
   - Patients don't need to login
   - Direct them to "Join Waitlist" or "Patient Portal"

### Understanding the Interface

```
┌─────────────────────────────────────┐
│         CancelFillMD Pro           │
│     Smart Appointment Management    │
├─────────────────────────────────────┤
│                                     │
│  👥 For Patients  │  🏥 For Staff  │
│  ├─ Join Waitlist │  ├─ Dashboard  │
│  └─ My Portal     │  └─ Upload     │
│                                     │
└─────────────────────────────────────┘
```

## For Patients

### Joining the Waitlist

#### Step 1: Access Waitlist Form
1. Click "Join Waitlist" from home page
2. Or go directly to: `your-clinic.app/waitlist`

#### Step 2: Enter Information
```
Required Fields:
- Full Name: Your complete name
- Email: Valid email for notifications
- Phone: Mobile number for SMS alerts
- Specialty: Select the department
- Preferred Dates: Choose multiple dates
- Time Preferences: Morning/Afternoon/Evening/Any
```

#### Step 3: Set Preferences
- **Preferred Dates**: Select all possible dates
  - More dates = higher chance of getting appointment
  - Can select up to 10 dates
  
- **Time Preferences**: 
  - Morning: 8 AM - 12 PM
  - Afternoon: 12 PM - 5 PM
  - Evening: 5 PM - 8 PM
  - Any: Available for any time

#### Step 4: Consent & Submit
- ✅ Check consent box for notifications
- Click "Join Waitlist"
- Save your confirmation number

### Booking from Notification

#### When You Receive a Notification

**SMS Example:**
```
MedCenter: Appointment available!
June 15, 10:00 AM - Dr. Smith
Book now: https://link.med/abc123
Expires in 2 hours
```

**Email Example:**
```
Subject: Appointment Available - June 15 at 10:00 AM

Dear John,

Good news! An appointment has become available:
- Date: June 15, 2024
- Time: 10:00 AM
- Doctor: Dr. Smith
- Specialty: Dermatology

[BOOK THIS APPOINTMENT] <- Click here

This link expires in 2 hours.
```

#### Booking Process
1. **Click the Link** immediately
2. **Review Details** on confirmation page
3. **Verify Information**:
   - Confirm your email
   - Confirm your phone
   - Add insurance info (optional)
4. **Accept Terms**:
   - ✅ I will attend this appointment
   - ✅ I understand the cancellation policy
5. **Click "Confirm Appointment"**
6. **Save Confirmation**:
   - Screenshot the confirmation
   - Note the confirmation number
   - Add to your calendar

### Using Patient Portal

#### Access Your Information
1. Go to "Patient Portal"
2. Verify with:
   - Email address
   - Last 4 digits of phone

#### Portal Features

**1. My Appointments**
- View upcoming appointments
- See appointment details
- Cancel with 24+ hour notice

**2. Waitlist Status**
- See active waitlist entries
- Update preferences
- Remove from waitlist

**3. Preferences**
- Update contact information
- Change notification settings
- Set availability preferences

**4. Notifications**
- Choose notification methods
- Set quiet hours
- Manage frequency

## For Staff

### Daily Workflow

#### Morning Routine
1. **Login** to Staff Dashboard
2. **Check Today's Appointments**:
   - Review schedule
   - Note any pre-cancellations
3. **Review Waitlist Size**:
   - Ensure adequate coverage
   - Add more patients if needed

#### Processing Cancellations

##### Patient Calls to Cancel
1. Go to **"Cancel Appointment"**
2. Select **"Staff Cancellation"**
3. Find appointment:
   - Search by date
   - Search by patient name
4. Select appointment from dropdown
5. Enter cancellation reason
6. Configure options:
   - ✅ Notify waitlist immediately
   - ✅ Auto-fill from waitlist
7. Click **"Cancel Appointment"**
8. System automatically:
   - Updates status
   - Notifies waitlist
   - Tracks metrics

##### Handling No-Shows
1. Mark as no-show (not cancelled)
2. Apply no-show policy
3. System tracks for patterns

### Managing Schedules

#### Upload Weekly Schedule
1. Go to **"Upload Schedule"**
2. Prepare CSV file:
   ```csv
   Date,Time,Doctor,Specialty,Patient Name,Patient Email,Patient Phone
   2024-06-10,09:00 AM,Dr. Smith,Dermatology,John Doe,john@email.com,555-1234
   2024-06-10,10:00 AM,Dr. Smith,Dermatology,,,
   ```
3. Click **"Choose File"**
4. Review preview
5. Click **"Import Appointments"**

#### Manual Entry
For individual appointments:
1. Scroll to **"Manual Entry"**
2. Fill in:
   - Date
   - Time
   - Doctor
   - Specialty
   - Duration
3. Click **"Add Appointment"**

### Monitoring Fill Status

#### Real-Time Dashboard
- **Today's Metrics**:
  - Fill rate percentage
  - Revenue recovered
  - Time saved
- **Live Updates**:
  - See cancellations as they happen
  - Watch slots get filled
  - Track response times

#### Taking Action
When you see unfilled cancellations:
1. Check if notifications were sent
2. Verify waitlist has matches
3. Consider manual outreach for urgent slots

## For Managers

### Analytics Overview

#### Accessing Analytics
1. Login with manager credentials
2. Navigate to **"Analytics & ROI"**
3. Select date range

#### Key Metrics to Monitor

**1. Fill Rate**
- Target: 80%+
- Formula: Filled Slots ÷ Cancelled Slots
- Action if low: Expand waitlist

**2. Average Fill Time**
- Target: < 30 minutes
- Measures system efficiency
- Action if high: Check notification delivery

**3. Revenue Recovery**
- Daily/Weekly/Monthly totals
- Compare to targets
- Calculate ROI

**4. Department Performance**
- Compare specialties
- Identify problem areas
- Allocate resources

### Running Reports

#### Daily Report
1. Go to Analytics
2. Select "Daily Summary"
3. Review:
   - Today's cancellations
   - Fill success rate
   - Revenue impact
4. Export as PDF/Excel

#### Weekly Analysis
1. Select "Week" view
2. Analyze trends:
   - Best/worst days
   - Peak cancellation times
   - Department comparison
3. Share with team

#### Monthly ROI Report
1. Select "Month" view
2. Review comprehensive metrics
3. Calculate total savings:
   ```
   Revenue Recovered: $XX,XXX
   - System Cost: $XXX
   = Net Benefit: $XX,XXX
   ```
4. Present to leadership

### Staff Management

#### Performance Monitoring
- Review individual metrics
- Track response times
- Identify training needs

#### Best Practices Implementation
1. Regular team meetings
2. Share success stories
3. Address challenges
4. Continuous improvement

## For Administrators

### System Configuration

#### Business Hours
1. Go to **Settings → Clinic Settings**
2. Set hours for each day
3. Mark closed days
4. Add holiday schedule

#### Appointment Rules
1. Go to **Settings → Appointment Settings**
2. Configure:
   - Default duration
   - Cancellation notice
   - Booking limits
   - Buffer times

#### Notification Setup
1. Go to **Settings → Notifications**
2. Configure:
   - Message templates
   - Retry attempts
   - Quiet hours
   - Channel preferences

### User Management

#### Adding New Staff
1. Go to **Settings → Security**
2. Click **"Add New User"**
3. Enter:
   - Username
   - Email
   - Temporary password
   - Role assignment
4. User receives welcome email

#### Role Permissions
- **Administrator**: All access
- **Manager**: Reports + operations
- **Staff**: Basic operations

### Security Settings

#### Password Policy
1. Set minimum length
2. Require complexity
3. Set expiration rules
4. Enable 2FA (recommended)

#### Audit Logging
- All actions logged
- Review weekly
- Export for compliance

## Common Workflows

### Workflow 1: Morning Cancellation Rush

**Scenario**: Multiple cancellations come in Monday morning

1. **Staff Actions**:
   ```
   8:15 AM - Cancel first appointment
   8:16 AM - System sends notifications
   8:18 AM - First slot filled
   8:20 AM - Cancel second appointment
   8:21 AM - More notifications sent
   8:25 AM - Second slot filled
   ```

2. **Result**: All slots filled within 30 minutes

### Workflow 2: Last-Minute Cancellation

**Scenario**: Patient cancels 2 hours before appointment

1. **Immediate Actions**:
   - Process cancellation
   - Enable urgent fill mode
   - Expand notification radius

2. **If Not Filled**:
   - Staff calls top waitlist matches
   - Offer incentive if needed
   - Last resort: Keep slot open

### Workflow 3: Building Waitlist

**Scenario**: New specialty needs waitlist

1. **Marketing**:
   - Email existing patients
   - Add to website
   - Reception promotes

2. **Target Numbers**:
   - Minimum: 10 per specialty
   - Optimal: 15-20
   - Maximum: 30

## Tips & Best Practices

### For Maximum Fill Rate

1. **Maintain Fresh Waitlist**
   - Remove inactive patients monthly
   - Update preferences quarterly
   - Encourage broad date ranges

2. **Optimize Timing**
   - Process cancellations immediately
   - Don't delay notifications
   - Act fast on responses

3. **Message Effectiveness**
   - Clear, urgent language
   - Prominent booking link
   - Show expiration time

### For Patient Satisfaction

1. **Set Expectations**
   - Explain first-come, first-served
   - Clarify notification process
   - Emphasize quick response need

2. **Make It Easy**
   - One-click booking
   - Mobile-friendly
   - Clear confirmation

3. **Follow Through**
   - Send confirmations
   - Provide reminders
   - Thank patients

### For Staff Efficiency

1. **Batch Processing**
   - Handle multiple cancellations together
   - Review patterns
   - Prepare for rush times

2. **Use Templates**
   - Standardize reasons
   - Quick selections
   - Consistent data

3. **Monitor Actively**
   - Keep dashboard visible
   - Respond to alerts
   - Celebrate successes

## Troubleshooting

### Common Issues

#### "Notifications Not Sending"
1. Check notification settings
2. Verify contact information
3. Check SMS/email credits
4. Review error logs

#### "Low Fill Rate"
1. Analyze waitlist size
2. Check match criteria
3. Review notification timing
4. Expand preferences

#### "Patients Can't Book"
1. Verify link hasn't expired
2. Check if slot already filled
3. Clear browser cache
4. Try different device

#### "Data Not Updating"
1. Refresh page (Ctrl+F5)
2. Check internet connection
3. Log out and back in
4. Contact support

### Getting Help

**For Technical Issues**:
- Email: support@cancelfillmd.com
- Phone: (555) 123-4567
- Hours: 9 AM - 5 PM EST

**For Training**:
- Video tutorials: docs.cancelfillmd.com/videos
- Schedule session: training@cancelfillmd.com

**For Emergencies**:
- Critical system issues: (555) 123-4569
- Available 24/7

---

## Quick Reference Card

### Staff Shortcuts
- **Cancel Appointment**: `C` key
- **View Waitlist**: `W` key
- **Today's Schedule**: `T` key
- **Refresh Data**: `F5`

### Important URLs
- Main App: `https://your-clinic.cancelfillmd.app`
- Patient Waitlist: `/waitlist`
- Staff Login: `/staff_dashboard`
- Help Docs: `/help_support`

### Key Metrics Targets
- Fill Rate: > 80%
- Fill Time: < 30 minutes
- Response Rate: > 70%
- Satisfaction: > 4.5/5

Remember: The key to success is quick action and maintaining an engaged waitlist!