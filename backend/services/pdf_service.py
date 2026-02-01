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
    def generate_insurance_policy_bond(policy_data, output_path):
        """
        Generates a professional insurance policy bond PDF.
        
        Args:
            policy_data: Dictionary containing policy details
            output_path: Path to save the PDF
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=26,
                textColor=colors.hexColor("#1e40af"),
                alignment=TA_CENTER,
                spaceAfter=10
            )
            
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.hexColor("#1e40af"),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.black,
                spaceBefore=12,
                spaceAfter=6,
                backColor=colors.hexColor("#dbeafe")
            )

            normal_style = styles['Normal']
            bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')
            
            elements = []

            # Header
            elements.append(Paragraph("AgriTech Insurance Services", title_style))
            elements.append(Paragraph("Agricultural Insurance Policy Bond", subtitle_style))
            elements.append(Spacer(1, 10))
            
            # Policy number and date box
            info_box = [
                ["Policy Number:", policy_data.get('policy_number', 'N/A')],
                ["Issue Date:", policy_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))],
                ["Status:", policy_data.get('status', 'ACTIVE')]
            ]
            
            t = Table(info_box, colWidths=[120, 380])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.hexColor("#f0f9ff")),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 2, colors.hexColor("#1e40af"))
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Policy Holder Details
            elements.append(Paragraph("Policy Holder Information", header_style))
            holder_info = [
                ["Field", "Details"],
                ["Farmer Name", policy_data.get('farmer_name', 'N/A')],
                ["Farmer ID", str(policy_data.get('user_id', 'N/A'))],
                ["Contact", policy_data.get('contact', 'N/A')],
                ["Farm Location", policy_data.get('farm_location', 'N/A')],
                ["Farm Size", f"{policy_data.get('farm_size_acres', 'N/A')} acres"]
            ]
            
            t = Table(holder_info, colWidths=[150, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#1e40af")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Coverage Details
            elements.append(Paragraph("Coverage Details", header_style))
            coverage_info = [
                ["Item", "Details"],
                ["Crop Type", policy_data.get('crop_type', 'N/A').upper()],
                ["Coverage Amount", f"₹{policy_data.get('coverage_amount', 'N/A'):,.2f}"],
                ["Premium Amount", f"₹{policy_data.get('premium_amount', 'N/A'):,.2f}"],
                ["Coverage Period", f"{policy_data.get('start_date', 'N/A')} to {policy_data.get('end_date', 'N/A')}"]
            ]
            
            t = Table(coverage_info, colWidths=[150, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#1e40af")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(asset_table)
            elements.append(Spacer(1, 20))

            # Risk Assessment
            elements.append(Paragraph("Risk Assessment", header_style))
            risk_info = [
                ["Metric", "Value"],
                ["Agri-Risk Score (ARS)", f"{policy_data.get('ars_score_at_issuance', 'N/A'):.1f}"],
                ["Risk Category", policy_data.get('risk_category', 'N/A')],
                ["Risk Multiplier", f"{policy_data.get('risk_multiplier', 1.0):.2f}x"],
                ["Premium Rate", f"{policy_data.get('base_rate', 'N/A')}% of coverage"]
            ]
            
            t = Table(risk_info, colWidths=[150, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.hexColor("#1e40af")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Terms and Conditions
            elements.append(Paragraph("Terms and Conditions", header_style))
            
            terms = [
                "This policy covers crop losses due to natural disasters including drought, flood, pest infestation, and extreme weather events.",
                "Claims must be submitted within 7 days of the incident with proper evidence documentation.",
                "The insured amount will be paid after verification of the claim by our assessment team.",
                "This policy is valid only for the specified coverage period and cannot be transferred.",
                "Premium payments must be completed before the coverage start date.",
                "All claims are subject to AI-powered verification and manual review if necessary.",
                "The policy holder must maintain accurate records of farming activities and crop yields."
            ]
            
            for i, term in enumerate(terms, 1):
                elements.append(Paragraph(f"{i}. {term}", normal_style))
                elements.append(Spacer(1, 8))
            
            elements.append(Spacer(1, 20))

            # Signatures
            elements.append(Paragraph("Authorized Signatures", header_style))
            elements.append(Spacer(1, 30))
            
            signature_table = [
                ["_________________________", "_________________________"],
                ["Policy Holder Signature", "Insurer Signature"],
                ["", ""],
                ["Date: ___________", "Date: ___________"]
            ]
            
            t = Table(signature_table, colWidths=[250, 250])
            t.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('TOPPADDING', (0, 0), (-1, -1), 10)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 30))

            # Footer / Disclaimer
            footer_text = """
            <para align=center fontSize=8 textColor=grey>
            This is a digitally generated insurance policy bond by AgriTech Insurance Services.<br/>
            For queries or claims, contact: insurance@agritech.com | Helpline: 1800-XXX-XXXX<br/>
            Registration No: IRDA/AGR/2024/12345 | Valid until {}<br/>
            <b>Important:</b> Please retain this document for future reference and claim processing.
            </para>
            """.format(policy_data.get('end_date', 'N/A'))
            
            elements.append(Paragraph(footer_text, normal_style))

            doc.build(elements)
            logger.info(f"Asset integrity report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate insurance policy PDF: {str(e)}")
            return False

