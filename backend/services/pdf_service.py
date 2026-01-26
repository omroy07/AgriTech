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
