# utils/analytics_utils.py
"""
Analytics utilities for calculating KPIs, metrics, and generating insights
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Optional, Union
import statistics
from collections import defaultdict

# Import config if it exists, otherwise use defaults
try:
    import config
except ImportError:
    # Default configuration if config.py is not available
    class config:
        class PRICING:
            average_appointment_values = {
                'Dermatology': 250,
                'Rheumatology': 300,
                'Cardiology': 350,
                'Orthopedics': 275,
                'General Practice': 150,
                'default': 250
            }


class MetricsCalculator:
    """Calculate various performance metrics"""
    
    @staticmethod
    def calculate_fill_rate(appointments: List[Dict], 
                          date_range: Optional[Tuple[date, date]] = None) -> float:
        """Calculate the percentage of cancelled appointments that were filled"""
        if date_range:
            appointments = MetricsCalculator._filter_by_date_range(appointments, date_range)
        
        cancelled = [apt for apt in appointments if apt.get('status') == 'cancelled']
        filled = [apt for apt in appointments if apt.get('status') == 'filled']
        
        if not cancelled:
            return 0.0
        
        return (len(filled) / len(cancelled)) * 100
    
    @staticmethod
    def calculate_utilization_rate(appointments: List[Dict],
                                 total_slots: int) -> float:
        """Calculate the percentage of available slots that were utilized"""
        if total_slots == 0:
            return 0.0
        
        utilized = len([apt for apt in appointments 
                       if apt.get('status') in ['scheduled', 'filled']])
        
        return (utilized / total_slots) * 100
    
    @staticmethod
    def calculate_average_fill_time(appointments: List[Dict]) -> float:
        """Calculate average time to fill cancelled appointments (in minutes)"""
        fill_times = []
        
        for apt in appointments:
            if (apt.get('status') == 'filled' and 
                'cancelled_at' in apt and 'filled_at' in apt):
                try:
                    cancelled_time = datetime.fromisoformat(apt['cancelled_at'])
                    filled_time = datetime.fromisoformat(apt['filled_at'])
                    minutes = (filled_time - cancelled_time).total_seconds() / 60
                    if minutes > 0:
                        fill_times.append(minutes)
                except:
                    continue
        
        return statistics.mean(fill_times) if fill_times else 0.0
    
    @staticmethod
    def calculate_revenue_metrics(appointments: List[Dict],
                                specialty_values: Optional[Dict] = None) -> Dict:
        """Calculate revenue-related metrics"""
        if not specialty_values:
            specialty_values = config.PRICING.average_appointment_values
        
        metrics = {
            'total_potential_revenue': 0,
            'lost_revenue': 0,
            'recovered_revenue': 0,
            'net_recovery_rate': 0,
            'revenue_recovery_rate': 0
        }
        
        for apt in appointments:
            specialty = apt.get('specialty', 'default')
            value = specialty_values.get(specialty, specialty_values.get('default', 250))
            
            if apt.get('status') in ['scheduled', 'filled']:
                metrics['total_potential_revenue'] += value
                
                if apt.get('status') == 'filled':
                    metrics['recovered_revenue'] += value
            
            elif apt.get('status') == 'cancelled':
                metrics['lost_revenue'] += value
        
        # Calculate recovery rates
        total_lost = metrics['lost_revenue'] + metrics['recovered_revenue']
        if total_lost > 0:
            metrics['net_recovery_rate'] = (metrics['recovered_revenue'] / total_lost) * 100
            metrics['revenue_recovery_rate'] = metrics['net_recovery_rate']
        
        return metrics
    
    @staticmethod
    def calculate_staff_time_saved(filled_appointments: int,
                                 manual_time_per_appointment: float = 150) -> Dict:
        """Calculate staff time saved through automation (in minutes)"""
        automated_time_per_appointment = 5
        
        time_saved = filled_appointments * (manual_time_per_appointment - automated_time_per_appointment)
        
        return {
            'total_minutes_saved': time_saved,
            'total_hours_saved': time_saved / 60,
            'labor_cost_saved': (time_saved / 60) * 35
        }
    
    @staticmethod
    def _filter_by_date_range(appointments: List[Dict], 
                            date_range: Tuple[date, date]) -> List[Dict]:
        """Filter appointments by date range"""
        start_date, end_date = date_range
        filtered = []
        
        for apt in appointments:
            try:
                apt_date = datetime.strptime(apt['date'], '%Y-%m-%d').date()
                if start_date <= apt_date <= end_date:
                    filtered.append(apt)
            except:
                continue
        
        return filtered


class TrendAnalyzer:
    """Analyze trends and patterns in appointment data"""
    
    @staticmethod
    def analyze_cancellation_patterns(appointments: List[Dict]) -> Dict:
        """Analyze patterns in cancellations"""
        cancellations = [apt for apt in appointments if apt.get('status') == 'cancelled']
        
        patterns = {
            'by_day_of_week': defaultdict(int),
            'by_time_of_day': defaultdict(int),
            'by_specialty': defaultdict(int),
            'by_advance_notice': defaultdict(int),
            'by_reason': defaultdict(int)
        }
        
        for apt in cancellations:
            # Day of week analysis
            try:
                apt_date = datetime.strptime(apt['date'], '%Y-%m-%d')
                day_name = apt_date.strftime('%A')
                patterns['by_day_of_week'][day_name] += 1
            except:
                pass
            
            # Time of day analysis
            try:
                apt_time = datetime.strptime(apt['time'], '%I:%M %p').time()
                if apt_time.hour < 12:
                    patterns['by_time_of_day']['Morning'] += 1
                elif apt_time.hour < 17:
                    patterns['by_time_of_day']['Afternoon'] += 1
                else:
                    patterns['by_time_of_day']['Evening'] += 1
            except:
                pass
            
            # Specialty analysis
            specialty = apt.get('specialty', 'Unknown')
            patterns['by_specialty'][specialty] += 1
            
            # Advance notice analysis
            if 'cancelled_at' in apt:
                try:
                    cancelled_time = datetime.fromisoformat(apt['cancelled_at'])
                    apt_datetime = datetime.strptime(f"{apt['date']} {apt['time']}", 
                                                   '%Y-%m-%d %I:%M %p')
                    hours_notice = (apt_datetime - cancelled_time).total_seconds() / 3600
                    
                    if hours_notice < 24:
                        patterns['by_advance_notice']['< 24 hours'] += 1
                    elif hours_notice < 48:
                        patterns['by_advance_notice']['24-48 hours'] += 1
                    elif hours_notice < 72:
                        patterns['by_advance_notice']['48-72 hours'] += 1
                    else:
                        patterns['by_advance_notice']['> 72 hours'] += 1
                except:
                    pass
            
            # Reason analysis
            reason = apt.get('cancellation_reason', 'Not specified')
            patterns['by_reason'][reason] += 1
        
        return dict(patterns)
    
    @staticmethod
    def calculate_trend(data_points: List[float]) -> Dict:
        """Calculate trend direction and strength"""
        if len(data_points) < 2:
            return {'direction': 'flat', 'strength': 0, 'change_percent': 0}
        
        # Simple linear regression
        x = list(range(len(data_points)))
        y = data_points
        
        # Calculate slope
        n = len(x)
        xy_sum = sum(x[i] * y[i] for i in range(n))
        x_sum = sum(x)
        y_sum = sum(y)
        x_squared_sum = sum(x[i] ** 2 for i in range(n))
        
        if n * x_squared_sum - x_sum ** 2 == 0:
            slope = 0
        else:
            slope = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum ** 2)
        
        # Determine trend
        if slope > 0.1:
            direction = 'increasing'
        elif slope < -0.1:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        # Calculate percentage change
        if data_points[0] != 0:
            change_percent = ((data_points[-1] - data_points[0]) / data_points[0]) * 100
        else:
            change_percent = 0
        
        return {
            'direction': direction,
            'strength': abs(slope),
            'change_percent': change_percent
        }
    
    @staticmethod
    def identify_peak_times(appointments: List[Dict]) -> Dict:
        """Identify peak cancellation times and booking times"""
        cancellation_times = defaultdict(int)
        booking_times = defaultdict(int)
        
        for apt in appointments:
            time_slot = apt.get('time', 'Unknown')
            
            if apt.get('status') == 'cancelled':
                cancellation_times[time_slot] += 1
            elif apt.get('status') in ['scheduled', 'filled']:
                booking_times[time_slot] += 1
        
        # Sort by frequency
        peak_cancellation_times = sorted(cancellation_times.items(), 
                                       key=lambda x: x[1], reverse=True)[:5]
        peak_booking_times = sorted(booking_times.items(), 
                                  key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'peak_cancellation_times': peak_cancellation_times,
            'peak_booking_times': peak_booking_times
        }


class PerformanceScorer:
    """Calculate performance scores and ratings"""
    
    @staticmethod
    def calculate_overall_score(metrics: Dict) -> float:
        """Calculate overall performance score (0-100)"""
        weights = {
            'fill_rate': 0.3,
            'fill_time': 0.2,
            'utilization_rate': 0.2,
            'revenue_recovery': 0.2,
            'patient_satisfaction': 0.1
        }
        
        scores = {}
        
        # Fill rate score (target: 80%)
        fill_rate = metrics.get('fill_rate', 0)
        scores['fill_rate'] = min(100, (fill_rate / 80) * 100)
        
        # Fill time score (target: 30 minutes)
        fill_time = metrics.get('avg_fill_time', 60)
        scores['fill_time'] = max(0, 100 - ((fill_time - 30) * 2))
        
        # Utilization rate score (target: 85%)
        utilization = metrics.get('utilization_rate', 0)
        scores['utilization_rate'] = min(100, (utilization / 85) * 100)
        
        # Revenue recovery score (based on recovery rate)
        recovery_rate = metrics.get('revenue_recovery_rate', 0)
        scores['revenue_recovery'] = min(100, recovery_rate)
        
        # Patient satisfaction score (scale to 100)
        satisfaction = metrics.get('patient_satisfaction', 0)
        scores['patient_satisfaction'] = (satisfaction / 5) * 100
        
        # Calculate weighted average
        total_score = sum(scores.get(key, 0) * weights[key] for key in weights)
        
        return round(total_score, 1)
    
    @staticmethod
    def get_performance_grade(score: float) -> Tuple[str, str]:
        """Get letter grade and description for performance score"""
        if score >= 90:
            return 'A+', 'Exceptional Performance'
        elif score >= 85:
            return 'A', 'Excellent Performance'
        elif score >= 80:
            return 'B+', 'Very Good Performance'
        elif score >= 75:
            return 'B', 'Good Performance'
        elif score >= 70:
            return 'C+', 'Above Average Performance'
        elif score >= 65:
            return 'C', 'Average Performance'
        elif score >= 60:
            return 'D', 'Below Average Performance'
        else:
            return 'F', 'Needs Improvement'


class InsightGenerator:
    """Generate actionable insights from analytics data"""
    
    @staticmethod
    def generate_insights(metrics: Dict, patterns: Dict) -> List[Dict]:
        """Generate actionable insights based on metrics and patterns"""
        insights = []
        
        # Fill rate insights
        fill_rate = metrics.get('fill_rate', 0)
        if fill_rate < 50:
            insights.append({
                'type': 'critical',
                'category': 'fill_rate',
                'title': 'Low Fill Rate Alert',
                'message': f'Fill rate is only {fill_rate:.1f}%. Consider expanding waitlist or improving notification strategy.',
                'action': 'Increase waitlist size by 50% and enable multi-channel notifications'
            })
        elif fill_rate > 85:
            insights.append({
                'type': 'positive',
                'category': 'fill_rate',
                'title': 'Excellent Fill Rate',
                'message': f'Fill rate of {fill_rate:.1f}% exceeds target. Current strategy is working well.',
                'action': 'Maintain current approach and document best practices'
            })
        
        # Time-based insights
        peak_times_data = patterns.get('peak_times', {})
        peak_cancellation_times = peak_times_data.get('peak_cancellation_times', [])
        if peak_cancellation_times and len(peak_cancellation_times) > 0:
            peak_time, peak_count = peak_cancellation_times[0]
            if peak_count > 10:
                insights.append({
                    'type': 'warning',
                    'category': 'scheduling',
                    'title': 'High Cancellation Time Identified',
                    'message': f'Most cancellations occur at {peak_time}. Consider double-booking.',
                    'action': f'Enable overbooking for {peak_time} slots'
                })
        
        # Revenue insights
        recovery_rate = metrics.get('revenue_recovery_rate', 0)
        if recovery_rate < 70:
            lost_revenue = metrics.get('lost_revenue', 0)
            insights.append({
                'type': 'warning',
                'category': 'revenue',
                'title': 'Revenue Recovery Opportunity',
                'message': f'Currently recovering only {recovery_rate:.1f}% of lost revenue (${lost_revenue:,.0f} at risk).',
                'action': 'Implement automated reminders and expand waitlist outreach'
            })
        
        # Specialty-specific insights
        specialty_cancellations = patterns.get('by_specialty', {})
        for specialty, count in specialty_cancellations.items():
            if count > 20:
                insights.append({
                    'type': 'info',
                    'category': 'specialty',
                    'title': f'High Cancellations in {specialty}',
                    'message': f'{specialty} has {count} cancellations. May need specialized approach.',
                    'action': f'Create targeted waitlist campaign for {specialty} patients'
                })
        
        return insights
    
    @staticmethod
    def generate_recommendations(insights: List[Dict]) -> List[Dict]:
        """Generate prioritized recommendations based on insights"""
        recommendations = []
        
        # Group insights by impact
        critical_insights = [i for i in insights if i['type'] == 'critical']
        warning_insights = [i for i in insights if i['type'] == 'warning']
        
        # Generate recommendations
        if critical_insights:
            for insight in critical_insights[:3]:
                recommendations.append({
                    'priority': 'high',
                    'timeframe': 'immediate',
                    'action': insight['action'],
                    'expected_impact': 'High',
                    'effort': 'Medium'
                })
        
        if warning_insights:
            for insight in warning_insights[:2]:
                recommendations.append({
                    'priority': 'medium',
                    'timeframe': 'this_week',
                    'action': insight['action'],
                    'expected_impact': 'Medium',
                    'effort': 'Low'
                })
        
        return recommendations


class BenchmarkAnalyzer:
    """Compare performance against industry benchmarks"""
    
    # Industry benchmarks
    BENCHMARKS = {
        'fill_rate': {'excellent': 80, 'good': 60, 'average': 40, 'poor': 20},
        'avg_fill_time': {'excellent': 30, 'good': 60, 'average': 120, 'poor': 240},
        'utilization_rate': {'excellent': 90, 'good': 80, 'average': 70, 'poor': 60},
        'no_show_rate': {'excellent': 5, 'good': 10, 'average': 15, 'poor': 25},
        'patient_satisfaction': {'excellent': 4.5, 'good': 4.0, 'average': 3.5, 'poor': 3.0}
    }
    
    @staticmethod
    def compare_to_benchmarks(metrics: Dict) -> Dict:
        """Compare metrics against industry benchmarks"""
        comparisons = {}
        
        for metric, benchmarks in BenchmarkAnalyzer.BENCHMARKS.items():
            if metric in metrics:
                value = metrics[metric]
                
                # Determine performance level
                if metric in ['fill_rate', 'utilization_rate', 'patient_satisfaction']:
                    # Higher is better
                    if value >= benchmarks['excellent']:
                        level = 'excellent'
                    elif value >= benchmarks['good']:
                        level = 'good'
                    elif value >= benchmarks['average']:
                        level = 'average'
                    else:
                        level = 'poor'
                else:
                    # Lower is better (avg_fill_time, no_show_rate)
                    if value <= benchmarks['excellent']:
                        level = 'excellent'
                    elif value <= benchmarks['good']:
                        level = 'good'
                    elif value <= benchmarks['average']:
                        level = 'average'
                    else:
                        level = 'poor'
                
                # Get next target
                level_progression = {
                    'poor': 'average',
                    'average': 'good',
                    'good': 'excellent',
                    'excellent': 'excellent'
                }
                next_level = level_progression.get(level, 'excellent')
                
                comparisons[metric] = {
                    'value': value,
                    'level': level,
                    'benchmark': benchmarks[level],
                    'next_target': benchmarks[next_level]
                }
        
        return comparisons


def generate_analytics_summary(appointments: List[Dict], 
                             date_range: Optional[Tuple[date, date]] = None) -> Dict:
    """Generate comprehensive analytics summary"""
    
    # Calculate basic metrics
    metrics = {
        'fill_rate': MetricsCalculator.calculate_fill_rate(appointments, date_range),
        'avg_fill_time': MetricsCalculator.calculate_average_fill_time(appointments),
        'utilization_rate': MetricsCalculator.calculate_utilization_rate(
            appointments, len(appointments)
        ),
        'patient_satisfaction': 4.5  # Placeholder - would come from surveys
    }
    
    # Add revenue metrics
    revenue_metrics = MetricsCalculator.calculate_revenue_metrics(appointments)
    metrics.update(revenue_metrics)
    
    # Add staff time saved metrics
    filled_count = len([a for a in appointments if a.get('status') == 'filled'])
    staff_metrics = MetricsCalculator.calculate_staff_time_saved(filled_count)
    metrics['staff_hours_saved'] = staff_metrics['total_hours_saved']
    metrics['labor_cost_saved'] = staff_metrics['labor_cost_saved']
    
    # Analyze patterns
    patterns = TrendAnalyzer.analyze_cancellation_patterns(appointments)
    
    # Add peak times analysis
    peak_times = TrendAnalyzer.identify_peak_times(appointments)
    patterns['peak_times'] = peak_times
    
    # Generate insights
    insights = InsightGenerator.generate_insights(metrics, patterns)
    
    # Calculate performance score
    overall_score = PerformanceScorer.calculate_overall_score(metrics)
    grade, description = PerformanceScorer.get_performance_grade(overall_score)
    
    # Compare to benchmarks
    benchmark_comparison = BenchmarkAnalyzer.compare_to_benchmarks(metrics)
    
    # Generate recommendations
    recommendations = InsightGenerator.generate_recommendations(insights)
    
    return {
        'metrics': metrics,
        'patterns': patterns,
        'insights': insights,
        'performance': {
            'score': overall_score,
            'grade': grade,
            'description': description
        },
        'benchmarks': benchmark_comparison,
        'recommendations': recommendations,
        'summary': {
            'total_appointments': len(appointments),
            'date_range': date_range,
            'generated_at': datetime.now().isoformat()
        }
    }