"""
PDF Generation Service for conversation reports
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TranscriptMessage(BaseModel):
    timestamp: str
    speaker: str
    content: str
    messageId: str
    metadata: Optional[Dict[str, Any]] = None

class KeyFactor(BaseModel):
    category: str
    points: List[str]

class RiskFactor(BaseModel):
    risk_type: str
    description: str
    severity: str

class ThirdPartyIntervention(BaseModel):
    speaker: str
    questions_answered: List[str]
    risk_level: str

class ThirdPartyInterventionSummary(BaseModel):
    detected: bool
    speakers: List[str]
    intervention_details: List[ThirdPartyIntervention]

class ConversationSummary(BaseModel):
    topic: str
    sentiment: str
    resolution: str
    keywords: Optional[List[str]] = None
    intent: Optional[str] = None
    summary: str
    key_factors: Optional[List[KeyFactor]] = None
    risk_factors: Optional[List[RiskFactor]] = None
    third_party_intervention: Optional[ThirdPartyInterventionSummary] = None
    recommendations: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    follow_up_required: bool = False

class PDFService:
    def __init__(self):
        self.storage_path = os.getenv("PDF_STORAGE_PATH", "./pdf_reports")
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Ensure the PDF storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def create_pdf_filename(self, conversation_id: str, account_id: str) -> str:
        """Generate a unique filename for the PDF"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_account_id = account_id.replace(" ", "_").replace("/", "_")
        filename = f"conversation_report_{safe_account_id}_{conversation_id}_{timestamp}.pdf"
        return os.path.join(self.storage_path, filename)
    
    def create_custom_styles(self):
        """Create custom styles for the PDF"""
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        # Section style
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.darkgreen
        )
        
        # Body style
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Highlight style
        highlight_style = ParagraphStyle(
            'CustomHighlight',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        )
        
        return {
            'title': title_style,
            'subtitle': subtitle_style,
            'section': section_style,
            'body': body_style,
            'highlight': highlight_style
        }
    
    async def generate_conversation_report(self, 
                                         conversation_id: str,
                                         account_id: str,
                                         email_id: str,
                                         transcript: List[TranscriptMessage],
                                         summary: ConversationSummary,
                                         metadata: Dict[str, Any]) -> str:
        """Generate a comprehensive PDF report for the conversation"""
        try:
            # Create filename and document
            filename = self.create_pdf_filename(conversation_id, account_id)
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = self.create_custom_styles()
            
            # Check for third-party intervention
            speakers = set(msg.speaker for msg in transcript)
            third_party_intervention = len(speakers) > 2  # More than user and agent
            
            # Build the story (content)
            story = []
            
            # Title page
            story.append(Paragraph(f"Report for {account_id}", styles['title']))
            story.append(Spacer(1, 20))
            
            # Report metadata
            metadata_data = [
                ['Report Generated:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ['Conversation ID:', conversation_id],
                ['Account ID:', account_id],
                ['User Email:', email_id],
                ['Duration:', f"{metadata.get('duration', 0)} seconds"]
            ]
            
            # Add third-party intervention flag if needed
            if third_party_intervention:
                metadata_data.append(['Third Party Intervention:', 'YES'])
            else:
                metadata_data.append(['Third Party Intervention:', 'NO'])
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
            
            # Define table style
            table_style = [
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
            
            # Add bold red styling for third-party intervention if present
            if third_party_intervention:
                # Find the row index for third-party intervention
                for i, row in enumerate(metadata_data):
                    if row[0] == 'Third Party Intervention:':
                        table_style.extend([
                            ('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'),
                            ('TEXTCOLOR', (0, i), (-1, i), colors.red),
                            ('FONTSIZE', (0, i), (-1, i), 11)
                        ])
                        break
            
            metadata_table.setStyle(TableStyle(table_style))
            
            story.append(metadata_table)
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['subtitle']))
            story.append(Paragraph(f"<b>Topic:</b> {summary.topic}", styles['body']))
            story.append(Paragraph(f"<b>Sentiment:</b> {summary.sentiment.title()}", styles['body']))
            story.append(Paragraph(f"<b>Intent:</b> {summary.intent}", styles['body']))
            story.append(Paragraph(f"<b>Resolution:</b> {summary.resolution}", styles['body']))
            story.append(Spacer(1, 10))
            
            # Detailed Summary
            story.append(Paragraph("Detailed Summary", styles['section']))
            story.append(Paragraph(summary.summary, styles['body']))
            story.append(Spacer(1, 10))
            
            # Key Factors
            if summary.key_factors:
                story.append(Paragraph("Key Business Factors", styles['section']))
                for factor in summary.key_factors:
                    story.append(Paragraph(f"<b>{factor.category}:</b>", styles['body']))
                    for point in factor.points:
                        story.append(Paragraph(f"• {point}", styles['body']))
                    story.append(Spacer(1, 5))
                story.append(Spacer(1, 10))
            
            # Risk Assessment
            if summary.risk_factors:
                story.append(Paragraph("Risk Assessment", styles['section']))
                for risk in summary.risk_factors:
                    risk_color = colors.red if risk.severity == "High" else colors.orange if risk.severity == "Medium" else colors.green
                    story.append(Paragraph(f"<b>{risk.risk_type} ({risk.severity}):</b> {risk.description}", 
                                         ParagraphStyle('RiskStyle', parent=styles['body'], textColor=risk_color)))
                story.append(Spacer(1, 10))
            
            # Third-Party Intervention
            if summary.third_party_intervention and summary.third_party_intervention.detected:
                story.append(Paragraph("⚠️ Third-Party Intervention Detected", styles['highlight']))
                story.append(Paragraph("The following third-party speakers were identified:", styles['body']))
                for speaker in summary.third_party_intervention.speakers:
                    story.append(Paragraph(f"• {speaker}", styles['body']))
                
                if summary.third_party_intervention.intervention_details:
                    story.append(Paragraph("Intervention Details:", styles['body']))
                    for detail in summary.third_party_intervention.intervention_details:
                        story.append(Paragraph(f"<b>{detail.speaker} (Risk Level: {detail.risk_level}):</b>", 
                                             ParagraphStyle('InterventionStyle', parent=styles['body'], textColor=colors.red)))
                        for question in detail.questions_answered:
                            story.append(Paragraph(f"  - Answered: {question}", 
                                                 ParagraphStyle('InterventionDetailStyle', parent=styles['body'], textColor=colors.red)))
                story.append(Spacer(1, 10))
            
            # Recommendations
            if summary.recommendations:
                story.append(Paragraph("Recommendations", styles['section']))
                for i, rec in enumerate(summary.recommendations, 1):
                    story.append(Paragraph(f"{i}. {rec}", styles['body']))
                story.append(Spacer(1, 10))
            
            # Action Items
            if summary.action_items:
                story.append(Paragraph("Action Items", styles['section']))
                for i, item in enumerate(summary.action_items, 1):
                    story.append(Paragraph(f"{i}. {item}", styles['body']))
                story.append(Spacer(1, 10))
            
            # Follow-up Required
            if summary.follow_up_required:
                story.append(Paragraph("⚠️ Follow-up Required", styles['highlight']))
                story.append(Paragraph("This conversation requires follow-up action.", styles['body']))
                story.append(Spacer(1, 10))
            
            # Build the PDF
            doc.build(story)
            
            logger.info(f"PDF report generated successfully: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise Exception(f"Failed to generate PDF report: {str(e)}")
    
    def get_pdf_file_size(self, filename: str) -> int:
        """Get the size of the generated PDF file"""
        try:
            return os.path.getsize(filename)
        except OSError:
            return 0
    
    def cleanup_old_reports(self, max_age_days: int = 30):
        """Clean up old PDF reports"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(self.storage_path, filename)
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old report: {filename}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {str(e)}") 