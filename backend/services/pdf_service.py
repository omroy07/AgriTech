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
    def generate_outbreak_report(outbreak_data, output_path):
        """
        Generates an outbreak alert PDF with preventative measures.
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.hexColor("#dc2626"),
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
                backColor=colors.hexColor("#fee2e2")
            )
            
            warning_style = ParagraphStyle(
                'WarningStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.hexColor("#dc2626"),
                spaceBefore=6,
                spaceAfter=6
            )
            
            normal_style = styles['Normal']
            
            elements = []
            
            # 1. Header
            elements.append(Paragraph("🚨 AgriTech Disease Outbreak Alert", title_style))
            elements.append(Paragraph(f"Emergency Action Report", styles['Heading2']))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 20))
            
            # 2. Outbreak Details
            zone = outbreak_data.get('zone', {})
            alert = outbreak_data.get('alert', {})
            
            elements.append(Paragraph("Outbreak Information", header_style))
            
            outbreak_info = [
                ["Field", "Details"],
                ["Zone ID", zone.get('zone_id', 'N/A')],
                ["Disease", zone.get('disease_name', 'N/A')],
                ["Affected Crop", zone.get('crop_affected', 'N/A')],
                ["Risk Level", zone.get('risk_level', 'N/A').upper()],
                ["Severity", zone.get('severity_level', 'N/A')],
                ["Distance from Farm", f"{outbreak_data.get('distance_km', 0):.1f} km"],
                ["Incident Count", str(zone.get('incident_count', 0))],
                ["Affected Area", f"{zone.get('total_affected_area', 0):.1f} hectares"]
            ]
            
            t = Table(outbreak_info, colWidths=[150, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#dc2626")),
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
            
            # 3. Warning Message
            elements.append(Paragraph("⚠️ Urgent Action Required", warning_style))
            elements.append(Paragraph(
                f"This outbreak has been detected within {outbreak_data.get('distance_km', 0):.1f} km "
                f"of your farm location. Immediate preventative measures are strongly recommended.",
                normal_style
            ))
            elements.append(Spacer(1, 20))
            
            # 4. AI-Generated Recommendations
            elements.append(Paragraph("Preventative Measures & Recommendations", header_style))
            
            recommendations = outbreak_data.get('recommendations', 'Consult local agricultural expert.')
            
            # Clean up and format recommendations
            cleaned_recs = recommendations.replace("**", "").replace("##", "")
            lines = cleaned_recs.split('\n')
            
            for line in lines:
                if line.strip():
                    if line.startswith('- ') or line.startswith('* '):
                        elements.append(Paragraph(f"• {line[2:]}", normal_style))
                    elif line.startswith(('#', '1.', '2.', '3.', '4.', '5.')):
                        # Section header
                        header_text = line.lstrip('#1234567890. ')
                        elements.append(Spacer(1, 8))
                        elements.append(Paragraph(header_text, ParagraphStyle(
                            'SubHeader',
                            parent=styles['Heading3'],
                            fontSize=12,
                            textColor=colors.hexColor("#991b1b"),
                            spaceBefore=6,
                            spaceAfter=6
                        )))
                    else:
                        elements.append(Paragraph(line, normal_style))
                    elements.append(Spacer(1, 4))
            
            # 5. Contact Information
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Emergency Contacts", header_style))
            elements.append(Paragraph(
                "• Local Agricultural Extension Office<br/>"
                "• Crop Protection Helpline: 1800-XXX-XXXX<br/>"
                "• AgriTech Support: support@agritech.com",
                normal_style
            ))
            
            # 6. Footer
            elements.append(Spacer(1, 30))
            footer_text = (
                "Disclaimer: This is an AI-generated outbreak alert based on reported incidents. "
                "Please consult with local agricultural experts and authorities for verification "
                "and detailed guidance. Act promptly to protect your crops."
            )
            elements.append(Paragraph(
                footer_text,
                ParagraphStyle(
                    'Footer',
                    parent=normal_style,
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=TA_CENTER
                )
            ))
            
            doc.build(elements)
            return True
        except Exception as e:
            logger.error(f"Failed to generate outbreak PDF: {str(e)}")
            return False
