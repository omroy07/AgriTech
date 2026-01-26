"""
PDF Report Generation Service
Generates professional loan eligibility reports for farmers
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.platypus import PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
import re


class LoanReportPDFGenerator:
    """Generates professional PDF reports for loan eligibility assessments"""
    
    def __init__(self, output_dir='reports'):
        """
        Initialize PDF generator
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#424242'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#2E7D32'),
            borderWidth=0,
            borderPadding=5
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Info box style
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=13,
            leftIndent=10,
            rightIndent=10,
            spaceBefore=5,
            spaceAfter=5
        ))
    
    def _add_header(self, canvas, doc):
        """Add header to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#2E7D32'))
        canvas.drawString(inch, 10.5*inch, "AgriTech - Agricultural Loan Report")
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(7.5*inch, 10.5*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.line(inch, 10.4*inch, 7.5*inch, 10.4*inch)
        canvas.restoreState()
    
    def _add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(4.25*inch, 0.5*inch, f"Page {doc.page}")
        canvas.drawCentredString(4.25*inch, 0.35*inch, "Confidential - For Banking and Financial Institution Use Only")
        canvas.restoreState()
    
    def _parse_markdown_content(self, content):
        """Parse markdown-style content and extract sections"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check for section headers (## or **)
            if line.startswith('##') or (line.startswith('**') and line.endswith('**')):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.replace('##', '').replace('**', '').strip()
                current_content = []
            elif line and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _format_bullet_points(self, text):
        """Format bullet points from markdown to reportlab"""
        formatted_text = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle bullet points (-, *, •)
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                line = '• ' + line[1:].strip()
            
            # Bold text handling (**text** to <b>text</b>)
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            
            formatted_text.append(line)
        
        return '<br/>'.join(formatted_text)
    
    def generate_report(self, farmer_data, assessment_result, farmer_email):
        """
        Generate a professional PDF report
        
        Args:
            farmer_data: Dictionary containing farmer application data
            assessment_result: AI-generated assessment text
            farmer_email: Email address of the farmer
        
        Returns:
            str: Path to generated PDF file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        farmer_name = farmer_data.get('name', 'Unknown')
        safe_name = re.sub(r'[^\w\s-]', '', farmer_name).strip().replace(' ', '_')
        filename = f"loan_report_{safe_name}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=1.2*inch,
            bottomMargin=0.8*inch
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("Agricultural Loan Eligibility Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report info box
        report_info = f"""
        <b>Report Number:</b> AGR-{timestamp}<br/>
        <b>Generated Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Applicant:</b> {farmer_data.get('name', 'N/A')}<br/>
        <b>Email:</b> {farmer_email}
        """
        
        info_table_data = [[Paragraph(report_info, self.styles['InfoBox'])]]
        info_table = Table(info_table_data, colWidths=[6.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F5E9')),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#2E7D32')),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Application Details Section
        story.append(Paragraph("Application Details", self.styles['CustomSubtitle']))
        
        # Create application details table
        app_details = []
        for key, value in farmer_data.items():
            if key not in ['assessment', 'email']:
                display_key = key.replace('_', ' ').title()
                display_value = str(value) if value else 'N/A'
                app_details.append([
                    Paragraph(f"<b>{display_key}:</b>", self.styles['CustomBody']),
                    Paragraph(display_value, self.styles['CustomBody'])
                ])
        
        if app_details:
            details_table = Table(app_details, colWidths=[2.5*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(details_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Assessment Results Section
        story.append(Paragraph("Loan Eligibility Assessment", self.styles['CustomSubtitle']))
        
        # Parse the assessment result
        sections = self._parse_markdown_content(assessment_result)
        
        # If sections were found, display them nicely
        if sections:
            for section_title, section_content in sections.items():
                story.append(Paragraph(section_title, self.styles['SectionHeader']))
                
                formatted_content = self._format_bullet_points(section_content)
                story.append(Paragraph(formatted_content, self.styles['CustomBody']))
                story.append(Spacer(1, 0.15*inch))
        else:
            # If no sections found, display as plain text
            formatted_content = self._format_bullet_points(assessment_result)
            story.append(Paragraph(formatted_content, self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Disclaimer
        disclaimer = """
        <b>DISCLAIMER:</b> This report is generated based on the information provided and serves as an 
        indicative assessment only. Actual loan approval is subject to verification of documents, 
        credit history check, and the lending institution's policies. Please consult with your bank 
        or financial institution for final loan approval.
        """
        
        disclaimer_table = Table([[Paragraph(disclaimer, self.styles['InfoBox'])]], colWidths=[6.5*inch])
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF3E0')),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#FF9800')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(disclaimer_table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=self._add_header, onLaterPages=self._add_header)
        
        print(f"✓ PDF Report generated: {filepath}")
        return filepath


def generate_loan_report(farmer_data, assessment_result, farmer_email):
    """
    Convenience function to generate a loan report
    
    Args:
        farmer_data: Dictionary containing farmer application data
        assessment_result: AI-generated assessment text
        farmer_email: Email address of the farmer
    
    Returns:
        str: Path to generated PDF file
    """
    generator = LoanReportPDFGenerator()
    return generator.generate_report(farmer_data, assessment_result, farmer_email)
