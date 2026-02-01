import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from backend.utils.logger import logger

class PDFService:
    @staticmethod
    def generate_loan_report(user_data, analysis_result, output_path):
        """
        Generates a professional PDF report for loan eligibility.
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.hexColor("#16a34a"),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.black,
                spaceBefore=12,
                spaceAfter=6,
                borderPadding=4,
                backColor=colors.hexColor("#e6f4ea")
            )

            normal_style = styles['Normal']
            
            elements = []

            # 1. Header / Logo Placeholder
            elements.append(Paragraph("AgriTech Financial Solutions", title_style))
            elements.append(Paragraph(f"Loan Eligibility Assessment Report", styles['Heading2']))
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 20))

            # 2. Farmer Details Section
            elements.append(Paragraph("Farmer Details", header_style))
            farmer_info = [
                ["Field", "Value"],
                ["Loan Type", user_data.get('loan_type', 'N/A')],
                ["Requested Amount", f"₹{user_data.get('amount', 'N/A')}"],
                ["Duration", f"{user_data.get('duration', 'N/A')} months"],
                ["Purpose", user_data.get('purpose', 'N/A')]
            ]
            
            t = Table(farmer_info, colWidths=[150, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#16a34a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            # 3. Analysis Result
            elements.append(Paragraph("Detailed Analysis", header_style))
            
            # Clean up analysis_result (Gemini might return markdown)
            # Simple conversion: replace markdown headings/bullets for PDF rendering
            cleaned_result = analysis_result.replace("**", "").replace("##", "")
            lines = cleaned_result.split('\n')
            
            for line in lines:
                if line.strip():
                    if line.startswith('- '):
                        elements.append(Paragraph(f"• {line[2:]}", normal_style))
                    else:
                        elements.append(Paragraph(line, normal_style))
                    elements.append(Spacer(1, 6))

            # 4. Footer
            elements.append(Spacer(1, 40))
            footer_text = "Disclaimer: This is an AI-generated assessment based on the information provided. Please consult with your bank for final approval."
            elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))

            doc.build(elements)
            return True
        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}")
            return False
    
    @staticmethod
    def generate_asset_integrity_report(asset_data, maintenance_history, prediction_data, output_path):
        """
        Generates a comprehensive PDF report for farm asset health and maintenance.
        
        Args:
            asset_data: Dictionary with asset details
            maintenance_history: List of maintenance log dictionaries
            prediction_data: AI prediction results
            output_path: Path to save PDF
            
        Returns:
            Boolean indicating success
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.hexColor("#0ea5e9"),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.black,
                spaceBefore=12,
                spaceAfter=6,
                borderPadding=4,
                backColor=colors.hexColor("#e0f2fe")
            )
            
            # Health score color coding
            health_score = asset_data.get('health_score', 0)
            if health_score >= 85:
                health_color = colors.hexColor("#16a34a")  # Green
            elif health_score >= 60:
                health_color = colors.hexColor("#f59e0b")  # Orange
            elif health_score >= 30:
                health_color = colors.hexColor("#dc2626")  # Red
            else:
                health_color = colors.hexColor("#7f1d1d")  # Dark red
            
            normal_style = styles['Normal']
            
            elements = []

            # 1. Header
            elements.append(Paragraph("AgriTech Asset Management", title_style))
            elements.append(Paragraph("Farm Equipment Integrity & Maintenance Report", styles['Heading2']))
            elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 20))

            # 2. Asset Overview
            elements.append(Paragraph("Asset Information", header_style))
            asset_info = [
                ["Field", "Value"],
                ["Asset ID", asset_data.get('asset_id', 'N/A')],
                ["Asset Name", asset_data.get('asset_name', 'N/A')],
                ["Type", asset_data.get('asset_type', 'N/A')],
                ["Manufacturer", asset_data.get('manufacturer', 'N/A')],
                ["Model", asset_data.get('model', 'N/A')],
                ["Purchase Date", asset_data.get('purchase_date', 'N/A')],
                ["Total Runtime", f"{asset_data.get('total_runtime_hours', 0):.1f} hours"],
                ["Status", asset_data.get('status', 'N/A')]
            ]
            
            asset_table = Table(asset_info, colWidths=[150, 350])
            asset_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#0ea5e9")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(asset_table)
            elements.append(Spacer(1, 20))

            # 3. Health Score Section
            elements.append(Paragraph("Current Health Assessment", header_style))
            
            health_info = [
                ["Metric", "Value", "Status"],
                ["Health Score", f"{health_score:.1f}/100", ""],
                ["Last Maintenance", asset_data.get('last_maintenance_date', 'Never'), ""],
                ["Next Maintenance Due", asset_data.get('next_maintenance_due', 'Not Scheduled'), ""]
            ]
            
            health_table = Table(health_info, colWidths=[150, 200, 150])
            health_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#0ea5e9")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (1, 1), colors.whitesmoke),
                ('BACKGROUND', (1, 1), (1, 1), health_color),
                ('TEXTCOLOR', (1, 1), (1, 1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(health_table)
            elements.append(Spacer(1, 20))

            # 4. AI Failure Prediction
            if prediction_data:
                elements.append(Paragraph("AI-Powered Failure Prediction", header_style))
                
                urgency_colors = {
                    'LOW': colors.hexColor("#16a34a"),
                    'MEDIUM': colors.hexColor("#f59e0b"),
                    'HIGH': colors.hexColor("#dc2626"),
                    'CRITICAL': colors.hexColor("#7f1d1d")
                }
                
                urgency = prediction_data.get('urgency', 'MEDIUM')
                urgency_color = urgency_colors.get(urgency, colors.grey)
                
                pred_info = [
                    ["Prediction Metric", "Value"],
                    ["Days to Predicted Failure", f"{prediction_data.get('days_to_failure', 'N/A')} days"],
                    ["Confidence Level", f"{prediction_data.get('confidence', 0)}%"],
                    ["Urgency", urgency]
                ]
                
                pred_table = Table(pred_info, colWidths=[200, 300])
                pred_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#0ea5e9")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('BACKGROUND', (1, 3), (1, 3), urgency_color),
                    ('TEXTCOLOR', (1, 3), (1, 3), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                elements.append(pred_table)
                elements.append(Spacer(1, 12))
                
                # Risk Factors
                elements.append(Paragraph("Identified Risk Factors:", ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold', fontSize=11)))
                risk_factors = prediction_data.get('risk_factors', [])
                for idx, factor in enumerate(risk_factors, 1):
                    elements.append(Paragraph(f"{idx}. {factor}", normal_style))
                elements.append(Spacer(1, 12))
                
                # Recommendations
                elements.append(Paragraph("Recommended Actions:", ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold', fontSize=11)))
                recommendations = prediction_data.get('recommendations', [])
                for idx, rec in enumerate(recommendations, 1):
                    elements.append(Paragraph(f"• {rec}", normal_style))
                elements.append(Spacer(1, 20))

            # 5. Maintenance History
            elements.append(Paragraph("Recent Maintenance History", header_style))
            
            if maintenance_history and len(maintenance_history) > 0:
                maint_data = [["Date", "Type", "Description", "Cost"]]
                
                for log in maintenance_history[:10]:  # Last 10 entries
                    maint_data.append([
                        log.get('completed_date', log.get('scheduled_date', 'N/A'))[:10],
                        log.get('maintenance_type', 'N/A'),
                        log.get('description', 'N/A')[:40] + '...' if len(log.get('description', '')) > 40 else log.get('description', 'N/A'),
                        f"₹{log.get('cost', 0):.2f}"
                    ])
                
                maint_table = Table(maint_data, colWidths=[80, 80, 220, 80])
                maint_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#0ea5e9")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                elements.append(maint_table)
            else:
                elements.append(Paragraph("No maintenance records found.", normal_style))
            
            elements.append(Spacer(1, 20))

            # 6. Summary & Conclusion
            elements.append(Paragraph("Summary & Recommendations", header_style))
            
            if health_score >= 85:
                summary = "Your asset is in excellent condition. Continue with routine maintenance schedule."
            elif health_score >= 60:
                summary = "Your asset shows moderate wear. Increased monitoring and preventive maintenance recommended."
            elif health_score >= 30:
                summary = "⚠️ Your asset requires immediate attention. Schedule comprehensive inspection and repairs."
            else:
                summary = "🔴 CRITICAL: Your asset is at high risk of failure. Immediate professional service required."
            
            elements.append(Paragraph(summary, ParagraphStyle('Summary', parent=normal_style, fontSize=11, textColor=health_color, fontName='Helvetica-Bold')))
            elements.append(Spacer(1, 30))

            # 7. Footer
            footer_text = "Disclaimer: This report is generated using AI prediction models and historical data. Actual asset condition may vary. Professional inspection recommended for critical decisions."
            elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))

            doc.build(elements)
            logger.info(f"Asset integrity report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate asset integrity report: {str(e)}")
            return False

