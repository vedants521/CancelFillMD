# pages/analytics_dashboard.py
"""
Analytics and reporting dashboard with real-time KPIs and insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import specific functions from utils modules
from utils.firebase_utils import FirebaseDB
from utils.analytics_utils import generate_analytics_summary, MetricsCalculator
from utils.export_utils import ReportGenerator
import config

st.set_page_config(
    page_title="Analytics Dashboard - CancelFillMD Pro",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Analytics & ROI Dashboard")
    st.markdown("Track performance metrics and measure ROI in real-time")
    
    # Check authentication
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("🔒 Please login through the Staff Dashboard first")
        if st.button("Go to Staff Dashboard"):
            st.switch_page("pages/staff_dashboard.py")
        return
    
    # Initialize database
    db = FirebaseDB()
    
    # Date range selector
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        date_range = st.selectbox(
            "Time Period",
            ["Today", "This Week", "This Month", "Last 30 Days", "Custom"]
        )
    
    if date_range == "Custom":
        with col2:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        with col3:
            end_date = st.date_input("End Date", value=date.today())
    else:
        # Calculate date range
        end_date = date.today()
        if date_range == "Today":
            start_date = end_date
        elif date_range == "This Week":
            start_date = end_date - timedelta(days=end_date.weekday())
        elif date_range == "This Month":
            start_date = end_date.replace(day=1)
        else:  # Last 30 Days
            start_date = end_date - timedelta(days=30)
    
    with col4:
        if st.button("📥 Export Report", type="primary"):
            generate_and_download_report(start_date, end_date, db)
    
    # Get appointments data
    all_appointments = db.get_appointments()
    
    # Filter by date range
    filtered_appointments = []
    for apt in all_appointments:
        try:
            apt_date = datetime.strptime(apt['date'], '%Y-%m-%d').date()
            if start_date <= apt_date <= end_date:
                filtered_appointments.append(apt)
        except:
            continue
    
    if not filtered_appointments:
        st.warning("No data available for the selected date range.")
        
        # Show demo data suggestion
        if config.DEMO_MODE:
            st.info("💡 Tip: Run `python setup_demo_data.py` to generate sample data")
        return
    
    # Generate analytics
    analytics_data = generate_analytics_summary(
        filtered_appointments,
        (start_date, end_date)
    )
    
    # Display KPI Cards
    display_kpi_cards(analytics_data['metrics'])
    
    # Performance Score
    st.markdown("---")
    display_performance_score(analytics_data['performance'])
    
    # Charts Section
    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Trends", 
        "💰 Financial Analysis", 
        "⏱️ Efficiency Metrics",
        "📊 Department Analysis",
        "🎯 Insights & Actions"
    ])
    
    with tab1:
        display_trends(filtered_appointments, start_date, end_date)
    
    with tab2:
        display_financial_analysis(analytics_data['metrics'], filtered_appointments)
    
    with tab3:
        display_efficiency_metrics(analytics_data, filtered_appointments)
    
    with tab4:
        display_department_analysis(filtered_appointments)
    
    with tab5:
        display_insights_and_recommendations(analytics_data)

def display_kpi_cards(metrics: dict):
    """Display key performance indicator cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fill_rate = metrics.get('fill_rate', 0)
        fill_rate_delta = fill_rate - 80  # Compare to target
        st.metric(
            "Fill Rate",
            f"{fill_rate:.1f}%",
            f"{fill_rate_delta:+.1f}% vs target",
            delta_color="normal" if fill_rate_delta >= 0 else "inverse"
        )
    
    with col2:
        revenue_recovered = metrics.get('recovered_revenue', 0)
        st.metric(
            "Revenue Recovered",
            f"${revenue_recovered:,.0f}",
            f"${revenue_recovered/30:.0f}/day avg" if revenue_recovered > 0 and len(metrics) > 0 else "$0/day"
        )
    
    with col3:
        avg_fill_time = metrics.get('avg_fill_time', 0)
        time_vs_target = 30 - avg_fill_time  # Target is 30 minutes
        st.metric(
            "Avg Fill Time",
            f"{avg_fill_time:.0f} min",
            f"{time_vs_target:+.0f} min vs target",
            delta_color="normal" if time_vs_target >= 0 else "inverse"
        )
    
    with col4:
        hours_saved = metrics.get('staff_hours_saved', 0)
        labor_saved = metrics.get('labor_cost_saved', 0)
        st.metric(
            "Staff Time Saved",
            f"{hours_saved:.0f} hrs",
            f"${labor_saved:.0f} labor cost"
        )

def display_performance_score(performance: dict):
    """Display overall performance score"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=performance.get('score', 0),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Performance Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 60], 'color': "#fee2e2"},
                    {'range': [60, 80], 'color': "#fef3c7"},
                    {'range': [80, 100], 'color': "#d1fae5"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        grade = performance.get('grade', 'B')
        description = performance.get('description', 'Good Performance')
        st.markdown(f"### {grade} - {description}")
        
        # Show tips based on score
        score = performance.get('score', 0)
        if score < 60:
            st.warning("💡 **Improvement Needed**: Focus on expanding your waitlist and reducing notification response time")
        elif score < 80:
            st.info("💡 **Good Progress**: Consider optimizing your matching algorithm and time preferences")
        else:
            st.success("💡 **Excellent Performance**: Keep up the great work! Minor optimizations can still help")

def display_trends(appointments: list, start_date: date, end_date: date):
    """Display trend charts"""
    # Prepare daily data
    daily_data = {}
    current = start_date
    
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        daily_data[date_str] = {
            'scheduled': 0,
            'cancelled': 0,
            'filled': 0,
            'available': 0
        }
        current += timedelta(days=1)
    
    # Count appointments by date and status
    for apt in appointments:
        if apt['date'] in daily_data:
            status = apt.get('status', 'unknown')
            if status in daily_data[apt['date']]:
                daily_data[apt['date']][status] += 1
    
    # Convert to DataFrame
    dates = []
    scheduled = []
    cancelled = []
    filled = []
    
    for date_str, counts in sorted(daily_data.items()):
        dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
        scheduled.append(counts['scheduled'])
        cancelled.append(counts['cancelled'])
        filled.append(counts['filled'])
    
    # Create line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=scheduled,
        mode='lines+markers',
        name='Scheduled',
        line=dict(color='#3b82f6', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=cancelled,
        mode='lines+markers',
        name='Cancelled',
        line=dict(color='#ef4444', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=filled,
        mode='lines+markers',
        name='Filled',
        line=dict(color='#10b981', width=2)
    ))
    
    fig.update_layout(
        title="Appointment Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Appointments",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Fill rate trend
    fill_rates = []
    for i in range(len(dates)):
        if cancelled[i] > 0:
            rate = (filled[i] / cancelled[i]) * 100
        else:
            rate = 0
        fill_rates.append(rate)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=dates, y=fill_rates,
        mode='lines+markers',
        name='Fill Rate',
        line=dict(color='#667eea', width=3)
    ))
    
    # Add target line
    fig2.add_hline(y=80, line_dash="dash", line_color="gray",
                   annotation_text="Target: 80%")
    
    fig2.update_layout(
        title="Fill Rate Trend",
        xaxis_title="Date",
        yaxis_title="Fill Rate (%)",
        yaxis_range=[0, 100],
        height=300
    )
    
    st.plotly_chart(fig2, use_container_width=True)

def display_financial_analysis(metrics: dict, appointments: list):
    """Display financial metrics and analysis"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue breakdown pie chart
        recovered = metrics.get('recovered_revenue', 0)
        lost = metrics.get('lost_revenue', 0)
        
        if recovered > 0 or lost > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Revenue Recovered', 'Revenue Lost'],
                values=[recovered, lost],
                hole=.3,
                marker_colors=['#10b981', '#ef4444']
            )])
            
            fig.update_layout(
                title="Revenue Recovery Breakdown",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue data available for this period")
    
    with col2:
        # Financial summary
        st.markdown("### Financial Impact Summary")
        
        total_potential = metrics.get('total_potential_revenue', 0)
        recovered = metrics.get('recovered_revenue', 0)
        lost = metrics.get('lost_revenue', 0)
        recovery_rate = metrics.get('net_recovery_rate', 0)
        
        # Calculate daily average based on date range
        num_days = max(1, len(set(apt['date'] for apt in appointments)))
        
        st.markdown(f"""
        - **Total Potential Revenue:** ${total_potential:,.0f}
        - **Revenue Recovered:** ${recovered:,.0f}
        - **Revenue Lost:** ${lost:,.0f}
        - **Recovery Rate:** {recovery_rate:.1f}%
        - **Daily Average:** ${recovered / num_days:,.0f}
        - **Monthly Projection:** ${recovered / num_days * 30:,.0f}
        - **Annual Projection:** ${recovered / num_days * 365:,.0f}
        """)
    
    # ROI Calculator
    st.markdown("### ROI Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_cost = st.number_input(
            "Monthly System Cost ($)",
            value=500,
            min_value=0,
            step=100
        )
    
    with col2:
        current_fill_rate = st.number_input(
            "Current Fill Rate (%)",
            value=10,
            min_value=0,
            max_value=100,
            step=5
        )
    
    with col3:
        projected_fill_rate = st.number_input(
            "Projected Fill Rate (%)",
            value=84,
            min_value=0,
            max_value=100,
            step=5
        )
    
    if st.button("Calculate ROI"):
        # Get actual data for calculation
        monthly_cancellations = len([a for a in appointments if a['status'] == 'cancelled'])
        avg_appointment_value = 250  # Default
        
        if monthly_cancellations > 0:
            current_recovery = monthly_cancellations * (current_fill_rate / 100) * avg_appointment_value
            projected_recovery = monthly_cancellations * (projected_fill_rate / 100) * avg_appointment_value
            additional_revenue = projected_recovery - current_recovery
            
            roi = ((additional_revenue - monthly_cost) / monthly_cost * 100) if monthly_cost > 0 else 0
            payback_months = monthly_cost / additional_revenue if additional_revenue > 0 else float('inf')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Additional Monthly Revenue", f"${additional_revenue:,.0f}")
            
            with col2:
                st.metric("ROI", f"{roi:.0f}%")
            
            with col3:
                if payback_months < float('inf'):
                    st.metric("Payback Period", f"{payback_months:.1f} months")
                else:
                    st.metric("Payback Period", "N/A")

def display_efficiency_metrics(analytics_data: dict, appointments: list):
    """Display efficiency and time-saving metrics"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Time saved per task
        tasks = ['Phone Calls', 'Schedule Review', 'Patient Matching', 'Follow-ups']
        time_saved = [45, 30, 40, 35]  # Minutes per filled appointment
        
        fig = go.Figure(data=[
            go.Bar(
                x=tasks,
                y=time_saved,
                marker_color=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']
            )
        ])
        
        fig.update_layout(
            title="Time Saved Per Task (Minutes/Appointment)",
            yaxis_title="Minutes Saved",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Efficiency metrics
        st.markdown("### Efficiency Gains")
        
        filled_count = len([a for a in appointments if a['status'] == 'filled'])
        total_time_saved = filled_count * 150 / 60  # 150 minutes per filled appointment
        labor_cost_saved = total_time_saved * 35  # $35/hour
        
        st.markdown(f"""
        - **Appointments Filled:** {filled_count}
        - **Total Time Saved:** {total_time_saved:.0f} hours
        - **Labor Cost Saved:** ${labor_cost_saved:,.0f}
        - **Avg Processing Time:** 5 min vs 150 min manual
        - **Efficiency Gain:** 96.7%
        """)
        
        # Create efficiency comparison
        fig = go.Figure(data=[
            go.Bar(
                x=['Manual Process', 'With CancelFillMD'],
                y=[150, 5],
                marker_color=['#ef4444', '#10b981'],
                text=[150, 5],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Time Per Cancellation (Minutes)",
            yaxis_title="Minutes",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_department_analysis(appointments: list):
    """Display analysis by department/specialty"""
    # Group by specialty
    specialty_data = {}
    
    for apt in appointments:
        specialty = apt.get('specialty', 'Unknown')
        if specialty not in specialty_data:
            specialty_data[specialty] = {
                'total': 0,
                'cancelled': 0,
                'filled': 0,
                'revenue': 0
            }
        
        specialty_data[specialty]['total'] += 1
        
        if apt.get('status') == 'cancelled':
            specialty_data[specialty]['cancelled'] += 1
        elif apt.get('status') == 'filled':
            specialty_data[specialty]['filled'] += 1
            # Get appointment value
            value = config.PRICING['average_appointment_values'].get(
                specialty,
                config.PRICING['average_appointment_values']['default']
            )
            specialty_data[specialty]['revenue'] += value
    
    # Convert to DataFrame
    data = []
    for specialty, metrics in specialty_data.items():
        if metrics['cancelled'] > 0:
            fill_rate = (metrics['filled'] / metrics['cancelled']) * 100
        else:
            fill_rate = 0
        
        data.append({
            'Specialty': specialty,
            'Total Appointments': metrics['total'],
            'Cancellations': metrics['cancelled'],
            'Filled': metrics['filled'],
            'Fill Rate (%)': round(fill_rate, 1),
            'Revenue Recovered': metrics['revenue']
        })
    
    if data:
        df = pd.DataFrame(data)
        df = df.sort_values('Revenue Recovered', ascending=False)
        
        # Display table
        st.markdown("### Performance by Specialty")
        
        # Format the dataframe for display
        display_df = df.copy()
        display_df['Revenue Recovered'] = display_df['Revenue Recovered'].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Fill rate by specialty
            fig = px.bar(
                df,
                x='Specialty',
                y='Fill Rate (%)',
                title='Fill Rate by Specialty',
                color='Fill Rate (%)',
                color_continuous_scale='Viridis'
            )
            
            # Add target line
            fig.add_hline(y=80, line_dash="dash", line_color="red",
                         annotation_text="Target: 80%")
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue by specialty
            if df['Revenue Recovered'].sum() > 0:
                fig = px.pie(
                    df,
                    values='Revenue Recovered',
                    names='Specialty',
                    title='Revenue Recovery by Specialty'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No revenue data to display")
    else:
        st.info("No specialty data available for this period")

def display_insights_and_recommendations(analytics_data: dict):
    """Display AI-generated insights and recommendations"""
    st.markdown("### 🎯 Key Insights")
    
    # Display insights
    insights = analytics_data.get('insights', [])
    
    if insights:
        for insight in insights[:5]:  # Top 5 insights
            insight_type = insight.get('type', 'info')
            
            if insight_type == 'critical':
                st.error(f"⚠️ **{insight.get('title', 'Critical Issue')}**\n\n{insight.get('message', '')}")
            elif insight_type == 'warning':
                st.warning(f"⚡ **{insight.get('title', 'Warning')}**\n\n{insight.get('message', '')}")
            elif insight_type == 'positive':
                st.success(f"✅ **{insight.get('title', 'Success')}**\n\n{insight.get('message', '')}")
            else:
                st.info(f"ℹ️ **{insight.get('title', 'Information')}**\n\n{insight.get('message', '')}")
    else:
        # Default insights if none generated
        st.info("ℹ️ **Tip**: Maintain at least 15 patients per specialty in your waitlist for optimal fill rates")
        st.info("ℹ️ **Tip**: Process cancellations within 5 minutes for best results")
        st.info("ℹ️ **Tip**: Send notifications during business hours for better response rates")
    
    # Display recommendations
    st.markdown("### 📋 Recommendations")
    
    recommendations = analytics_data.get('recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations[:5], 1):
            priority = rec.get('priority', 'medium')
            
            # Priority badge
            if priority == 'high':
                badge = "🔴 High Priority"
            elif priority == 'medium':
                badge = "🟡 Medium Priority"
            else:
                badge = "🟢 Low Priority"
            
            with st.expander(f"{badge} - {rec.get('action', 'Action needed')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Timeframe:** {rec.get('timeframe', 'N/A').replace('_', ' ').title()}")
                
                with col2:
                    st.markdown(f"**Expected Impact:** {rec.get('expected_impact', 'N/A')}")
                
                with col3:
                    st.markdown(f"**Effort Required:** {rec.get('effort', 'N/A')}")
                
                # Additional details if available
                if 'details' in rec:
                    st.markdown(rec['details'])
    else:
        # Default recommendations
        st.markdown("""
        🟡 **Medium Priority** - Expand your waitlist
        - **Timeframe:** This Week
        - **Expected Impact:** High
        - **Effort Required:** Low
        
        🟡 **Medium Priority** - Optimize notification timing
        - **Timeframe:** This Week
        - **Expected Impact:** Medium
        - **Effort Required:** Low
        """)

def generate_and_download_report(start_date: date, end_date: date, db: FirebaseDB):
    """Generate and offer download of comprehensive report"""
    with st.spinner("Generating report..."):
        # Get appointments for date range
        all_appointments = db.get_appointments()
        
        # Filter by date range
        filtered = []
        for apt in all_appointments:
            try:
                apt_date = datetime.strptime(apt['date'], '%Y-%m-%d').date()
                if start_date <= apt_date <= end_date:
                    filtered.append(apt)
            except:
                continue
        
        if not filtered:
            st.warning("No data available for report generation")
            return
        
        # Generate analytics
        analytics_data = generate_analytics_summary(filtered, (start_date, end_date))
        
        # Add raw appointments to analytics data for export
        analytics_data['raw_appointments'] = filtered
        analytics_data['summary'] = analytics_data.get('summary', {})
        analytics_data['summary']['date_range'] = f"{start_date} to {end_date}"
        
        # Generate reports
        report_gen = ReportGenerator()
        
        # Generate PDF
        try:
            pdf_bytes = report_gen.generate_pdf_report(
                analytics_data,
                report_type=f"Analytics Report"
            )
            
            # Offer download
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"cancelfillmd_report_{start_date}_{end_date}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
        
        # Generate Excel
        try:
            excel_bytes = report_gen.generate_excel_report(analytics_data)
            
            st.download_button(
                label="📊 Download Excel Report",
                data=excel_bytes,
                file_name=f"cancelfillmd_report_{start_date}_{end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error generating Excel: {str(e)}")
        
        # Generate CSV
        try:
            csv_data = report_gen.generate_csv_export(filtered, 'analytics')
            
            st.download_button(
                label="📋 Download CSV Data",
                data=csv_data,
                file_name=f"cancelfillmd_data_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error generating CSV: {str(e)}")

if __name__ == "__main__":
    main()