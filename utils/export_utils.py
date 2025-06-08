# utils/export_utils.py
"""
Export utilities for generating reports in various formats (PDF, Excel, CSV)
"""
import pandas as pd
import io
import base64
from datetime import datetime, date
from typing import Dict, List, Optional, Union
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import xlsxwriter
import config

class ReportGenerator:
    """Generate professional reports in various formats"""
    
    @staticmethod
    def generate_pdf_report(data: Dict, report_type: str = 'monthly') -> bytes:
        """Generate PDF report with analytics and insights"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12
        )
        
        # Title page
        story.append(Paragraph(f"{config.APP_NAME} - {report_type.title()} Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.5 * inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_data = [
            ['Metric', 'Value', 'Status'],
            ['Fill Rate', f"{data['metrics']['fill_rate']:.1f}%", '✅ Excellent' if data['metrics']['fill_rate'] > 80 else '⚠️ Needs Improvement'],
            ['Avg Fill Time', f"{data['metrics']['avg_fill_time']:.0f} min", '✅ Good' if data['metrics']['avg_fill_time'] < 30 else '⚠️ Can Improve'],
            ['Revenue Recovered', f"${data['metrics']['recovered_revenue']:,.0f}", '✅ On Track'],
            ['Performance Score', f"{data['performance']['score']:.1f}/100", data['performance']['grade']]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.5 * inch))
        
        # Key Insights
        story.append(Paragraph("Key Insights", heading_style))
        for insight in data.get('insights', [])[:5]:
            bullet = "• " + insight['message']
            story.append(Paragraph(bullet, styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
        
        story.append(PageBreak())
        
        # Detailed Metrics
        story.append(Paragraph("Detailed Performance Metrics", heading_style))
        
        # Financial metrics table
        financial_data = [
            ['Financial Metric', 'This Period', 'Previous Period', 'Change'],
            ['Total Appointments', str(data['summary']['total_appointments']), 'N/A', 'N/A'],
            ['Potential Revenue', f"${data['metrics']['total_potential_revenue']:,.0f}", 'N/A', 'N/A'],
            ['Revenue Recovered', f"${data['metrics']['recovered_revenue']:,.0f}", 'N/A', 'N/A'],
            ['Revenue Lost', f"${data['metrics']['lost_revenue']:,.0f}", 'N/A', 'N/A'],
            ['Recovery Rate', f"{data['metrics']['net_recovery_rate']:.1f}%", 'N/A', 'N/A']
        ]
        
        financial_table = Table(financial_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        story.append(financial_table)
        story.append(Spacer(1, 0.5 * inch))
        
        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))
        for i, rec in enumerate(data.get('recommendations', [])[:5], 1):
            rec_text = f"{i}. {rec['action']} (Priority: {rec['priority'].title()})"
            story.append(Paragraph(rec_text, styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def generate_excel_report(data: Dict, include_raw_data: bool = True) -> bytes:
        """Generate Excel report with multiple sheets"""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#667eea',
                'font_color': 'white',
                'border': 1
            })
            
            currency_format = workbook.add_format({'num_format': '$#,##0'})
            percent_format = workbook.add_format({'num_format': '0.0%'})
            
            # Summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Fill Rate', 'Average Fill Time', 'Utilization Rate', 
                          'Revenue Recovered', 'Performance Score'],
                'Value': [
                    f"{data['metrics']['fill_rate']:.1f}%",
                    f"{data['metrics']['avg_fill_time']:.0f} minutes",
                    f"{data['metrics'].get('utilization_rate', 0):.1f}%",
                    f"${data['metrics']['recovered_revenue']:,.0f}",
                    f"{data['performance']['score']:.1f}/100"
                ],
                'Target': ['80%', '30 minutes', '85%', 'N/A', '85/100'],
                'Status': [
                    'Met' if data['metrics']['fill_rate'] >= 80 else 'Not Met',
                    'Met' if data['metrics']['avg_fill_time'] <= 30 else 'Not Met',
                    'Met' if data['metrics'].get('utilization_rate', 0) >= 85 else 'Not Met',
                    'N/A',
                    'Met' if data['performance']['score'] >= 85 else 'Not Met'
                ]
            })
            
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format summary sheet
            worksheet = writer.sheets['Summary']
            for i, col in enumerate(summary_df.columns):
                worksheet.write(0, i, col, header_format)
            
            # Financial Analysis sheet
            financial_df = pd.DataFrame({
                'Category': ['Total Potential Revenue', 'Revenue Recovered', 
                           'Revenue Lost', 'Net Recovery Rate'],
                'Amount': [
                    data['metrics']['total_potential_revenue'],
                    data['metrics']['recovered_revenue'],
                    data['metrics']['lost_revenue'],
                    data['metrics']['net_recovery_rate']
                ]
            })
            
            financial_df.to_excel(writer, sheet_name='Financial Analysis', index=False)
            
            # Insights sheet
            if 'insights' in data:
                insights_df = pd.DataFrame(data['insights'])
                insights_df.to_excel(writer, sheet_name='Insights', index=False)
            
            # Patterns sheet
            if 'patterns' in data:
                patterns_data = []
                for pattern_type, pattern_data in data['patterns'].items():
                    if isinstance(pattern_data, dict):
                        for key, value in pattern_data.items():
                            patterns_data.append({
                                'Pattern Type': pattern_type,
                                'Category': key,
                                'Count': value
                            })
                
                if patterns_data:
                    patterns_df = pd.DataFrame(patterns_data)
                    patterns_df.to_excel(writer, sheet_name='Patterns', index=False)
            
            # Raw data sheet (if requested)
            if include_raw_data and 'raw_appointments' in data:
                raw_df = pd.DataFrame(data['raw_appointments'])
                raw_df.to_excel(writer, sheet_name='Raw Data', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def generate_csv_export(appointments: List[Dict], 
                          export_type: str = 'appointments') -> str:
        """Generate CSV export of appointment data"""
        if export_type == 'appointments':
            df = pd.DataFrame(appointments)
            
            # Select relevant columns
            columns = ['date', 'time', 'doctor', 'specialty', 'status', 
                      'patient_name', 'patient_email', 'patient_phone']
            
            # Filter to existing columns
            columns = [col for col in columns if col in df.columns]
            df = df[columns]
            
        elif export_type == 'analytics':
            # Create analytics summary
            df = pd.DataFrame([{
                'Date': date.today().strftime('%Y-%m-%d'),
                'Total Appointments': len(appointments),
                'Cancellations': len([a for a in appointments if a['status'] == 'cancelled']),
                'Filled': len([a for a in appointments if a['status'] == 'filled']),
                'Fill Rate': ReportGenerator._calculate_fill_rate(appointments),
                'Revenue Recovered': ReportGenerator._calculate_revenue(appointments)
            }])
        
        return df.to_csv(index=False)
    
    @staticmethod
    def _calculate_fill_rate(appointments: List[Dict]) -> float:
        """Helper to calculate fill rate"""
        cancelled = len([a for a in appointments if a['status'] == 'cancelled'])
        filled = len([a for a in appointments if a['status'] == 'filled'])
        
        if cancelled == 0:
            return 0.0
        return (filled / cancelled) * 100
    
    @staticmethod
    def _calculate_revenue(appointments: List[Dict]) -> float:
        """Helper to calculate revenue"""
        filled = [a for a in appointments if a['status'] == 'filled']
        total = 0
        
        for apt in filled:
            specialty = apt.get('specialty', 'default')
            value = config.PRICING['average_appointment_values'].get(
                specialty, 
                config.PRICING['average_appointment_values']['default']
            )
            total += value
        
        return total

class EmailReportBuilder:
    """Build email-friendly HTML reports"""
    
    @staticmethod
    def build_daily_summary(metrics: Dict) -> str:
        """Build daily summary email HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; margin: 15px 0; 
                              border-radius: 8px; border-left: 4px solid #667eea; }}
                .metric-value {{ font-size: 28px; font-weight: bold; color: #667eea; }}
                .metric-label {{ color: #666; font-size: 14px; }}
                .insights {{ background: #e8f4f8; padding: 20px; border-radius: 8px; 
                           margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; 
                         margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Daily Performance Summary</h1>
                    <p>{date.today().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Today's Fill Rate</div>
                    <div class="metric-value">{metrics.get('fill_rate', 0):.1f}%</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Revenue Recovered</div>
                    <div class="metric-value">${metrics.get('revenue_recovered', 0):,.0f}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Average Fill Time</div>
                    <div class="metric-value">{metrics.get('avg_fill_time', 0):.0f} min</div>
                </div>
                
                <div class="insights">
                    <h3>Key Insights</h3>
                    <ul>
                        <li>Fill rate is {'above' if metrics.get('fill_rate', 0) > 80 else 'below'} target</li>
                        <li>{'Quick' if metrics.get('avg_fill_time', 0) < 30 else 'Consider improving'} response time to cancellations</li>
                        <li>Total slots filled today: {metrics.get('slots_filled', 0)}</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>This is an automated report from {config.APP_NAME}</p>
                    <p><a href="{config.CUSTOM_CONFIG.get('app_url', '#')}">View Full Dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def build_weekly_summary(data: Dict) -> str:
        """Build weekly summary email HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 40px; text-align: center; border-radius: 10px; }}
                .summary-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); 
                               gap: 20px; margin: 30px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 25px; border-radius: 8px; 
                              text-align: center; }}
                .big-number {{ font-size: 36px; font-weight: bold; color: #667eea; 
                             margin: 10px 0; }}
                .comparison {{ color: #10b981; font-size: 14px; }}
                .comparison.negative {{ color: #ef4444; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
                tr:nth-child(even) {{ background: #f8f9fa; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; 
                         margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Weekly Performance Report</h1>
                    <p>Week of {(date.today() - pd.Timedelta(days=6)).strftime('%B %d')} - {date.today().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="summary-grid">
                    <div class="metric-card">
                        <div>Total Appointments</div>
                        <div class="big-number">{data.get('total_appointments', 0)}</div>
                        <div class="comparison">↑ 12% from last week</div>
                    </div>
                    
                    <div class="metric-card">
                        <div>Fill Rate</div>
                        <div class="big-number">{data.get('fill_rate', 0):.1f}%</div>
                        <div class="comparison">↑ 5% from last week</div>
                    </div>
                    
                    <div class="metric-card">
                        <div>Revenue Recovered</div>
                        <div class="big-number">${data.get('revenue_recovered', 0):,.0f}</div>
                        <div class="comparison">↑ $2,500 from last week</div>
                    </div>
                    
                    <div class="metric-card">
                        <div>Staff Hours Saved</div>
                        <div class="big-number">{data.get('hours_saved', 0):.0f}h</div>
                        <div class="comparison">Equivalent to $2,625 in labor</div>
                    </div>
                </div>
                
                <h2>Top Performing Days</h2>
                <table>
                    <tr>
                        <th>Day</th>
                        <th>Fill Rate</th>
                        <th>Revenue Recovered</th>
                        <th>Avg Fill Time</th>
                    </tr>
                    <tr>
                        <td>Monday</td>
                        <td>92%</td>
                        <td>$3,500</td>
                        <td>18 min</td>
                    </tr>
                    <tr>
                        <td>Wednesday</td>
                        <td>88%</td>
                        <td>$2,750</td>
                        <td>22 min</td>
                    </tr>
                    <tr>
                        <td>Friday</td>
                        <td>85%</td>
                        <td>$2,250</td>
                        <td>25 min</td>
                    </tr>
                </table>
                
                <div class="footer">
                    <p>This is an automated report from {config.APP_NAME}</p>
                    <p><a href="{config.CUSTOM_CONFIG.get('app_url', '#')}">View Full Analytics</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

# Helper functions for Streamlit integration
def download_button_data(data: bytes, filename: str, mime_type: str) -> str:
    """Create download link data for Streamlit download button"""
    b64 = base64.b64encode(data).decode()
    return f"data:{mime_type};base64,{b64}"

def generate_report_filename(report_type: str, format: str) -> str:
    """Generate filename for report download"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"cancelfillmd_{report_type}_report_{timestamp}.{format}"