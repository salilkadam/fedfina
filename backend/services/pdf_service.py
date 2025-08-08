"""
PDF Service for generating professional reports
"""
import logging
import io
from datetime import datetime
from typing import Dict, Any, Optional, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config import Settings

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF reports"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Custom heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Custom body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Custom metadata style
        self.styles.add(ParagraphStyle(
            name='CustomMetadata',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT,
            textColor=colors.grey
        ))

    async def generate_conversation_report(
        self,
        conversation_id: str,
        transcript: str,
        summary: str,
        metadata: Dict[str, Any],
        account_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive PDF report for a conversation
        
        Args:
            conversation_id: The conversation ID
            transcript: The full conversation transcript
            summary: The AI-generated summary
            metadata: Additional metadata about the conversation
            account_id: The account ID for tracking
            
        Returns:
            Dict containing the PDF bytes and metadata
        """
        try:
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the story (content)
            story = []
            
            # Add header
            story.extend(self._create_header(conversation_id, metadata))
            
            # Add summary section
            story.extend(self._create_summary_section(summary))
            
            # Add transcript section
            story.extend(self._create_transcript_section(transcript))
            
            # Add metadata section
            story.extend(self._create_metadata_section(metadata))
            
            # Build the PDF
            doc.build(story)
            
            # Get the PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return {
                "status": "success",
                "pdf_bytes": pdf_bytes,
                "file_size": len(pdf_bytes),
                "filename": f"conversation_report_{conversation_id}.pdf"
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return {
                "status": "error",
                "error": f"PDF generation failed: {str(e)}"
            }

    def _create_header(self, conversation_id: str, metadata: Dict[str, Any]) -> List:
        """Create the report header"""
        elements = []
        
        # Title
        title = Paragraph(
            f"Conversation Analysis Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Conversation ID
        conv_id = Paragraph(
            f"<b>Conversation ID:</b> {conversation_id}",
            self.styles['CustomBody']
        )
        elements.append(conv_id)
        
        # Generation timestamp
        timestamp = Paragraph(
            f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            self.styles['CustomBody']
        )
        elements.append(timestamp)
        
        # Account ID if provided
        if metadata.get('account_id'):
            account_info = Paragraph(
                f"<b>Account ID:</b> {metadata.get('account_id')}",
                self.styles['CustomBody']
            )
            elements.append(account_info)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_summary_section(self, summary: str) -> List:
        """Create the summary section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Executive Summary",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Summary content
        summary_para = Paragraph(
            summary,
            self.styles['CustomBody']
        )
        elements.append(summary_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_transcript_section(self, transcript: str) -> List:
        """Create the transcript section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Full Conversation Transcript",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Split transcript into paragraphs for better formatting
        lines = transcript.split('\n')
        for line in lines:
            if line.strip():
                # Format speaker labels
                if line.startswith('AI:') or line.startswith('User:'):
                    speaker_para = Paragraph(
                        f"<b>{line}</b>",
                        self.styles['CustomBody']
                    )
                    elements.append(speaker_para)
                else:
                    # Regular message
                    message_para = Paragraph(
                        line,
                        self.styles['CustomBody']
                    )
                    elements.append(message_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_metadata_section(self, metadata: Dict[str, Any]) -> List:
        """Create the metadata section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Report Metadata",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Create metadata table
        metadata_data = []
        
        # Add key metadata fields
        if metadata.get('conversation_id'):
            metadata_data.append(['Conversation ID', metadata['conversation_id']])
        
        if metadata.get('account_id'):
            metadata_data.append(['Account ID', metadata['account_id']])
        
        if metadata.get('transcript_length'):
            metadata_data.append(['Transcript Length', f"{metadata['transcript_length']} characters"])
        
        if metadata.get('summary_length'):
            metadata_data.append(['Summary Length', f"{metadata['summary_length']} characters"])
        
        if metadata.get('processing_time'):
            metadata_data.append(['Processing Time', f"{metadata['processing_time']} seconds"])
        
        if metadata.get('ai_model'):
            metadata_data.append(['AI Model', metadata['ai_model']])
        
        if metadata.get('tokens_used'):
            metadata_data.append(['Tokens Used', str(metadata['tokens_used'])])
        
        # Create table
        if metadata_data:
            table = Table(metadata_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 20))
        return elements

    async def generate_simple_report(
        self,
        conversation_id: str,
        transcript: str,
        summary: str
    ) -> Dict[str, Any]:
        """
        Generate a simple PDF report with basic formatting
        
        Args:
            conversation_id: The conversation ID
            transcript: The conversation transcript
            summary: The AI-generated summary
            
        Returns:
            Dict containing the PDF bytes and metadata
        """
        try:
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the story
            story = []
            
            # Title
            title = Paragraph(
                f"Conversation Report - {conversation_id}",
                self.styles['CustomTitle']
            )
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Summary
            summary_title = Paragraph("Summary", self.styles['CustomHeading'])
            story.append(summary_title)
            
            summary_para = Paragraph(summary, self.styles['CustomBody'])
            story.append(summary_para)
            story.append(Spacer(1, 20))
            
            # Transcript
            transcript_title = Paragraph("Transcript", self.styles['CustomHeading'])
            story.append(transcript_title)
            
            transcript_para = Paragraph(transcript, self.styles['CustomBody'])
            story.append(transcript_para)
            
            # Build the PDF
            doc.build(story)
            
            # Get the PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return {
                "status": "success",
                "pdf_bytes": pdf_bytes,
                "file_size": len(pdf_bytes),
                "filename": f"simple_report_{conversation_id}.pdf"
            }
            
        except Exception as e:
            logger.error(f"Error generating simple PDF report: {e}")
            return {
                "status": "error",
                "error": f"Simple PDF generation failed: {str(e)}"
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check PDF service health
        
        Returns:
            Health status dictionary
        """
        try:
            # Test PDF generation with minimal content
            test_result = await self.generate_simple_report(
                conversation_id="test_conv_123",
                transcript="AI: Hello\nUser: Hi\nAI: How are you?\nUser: Good",
                summary="This is a test conversation summary."
            )
            
            if test_result.get("status") == "success":
                return {
                    "status": "healthy",
                    "message": "PDF service working correctly",
                    "test_file_size": test_result.get("file_size", 0)
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"PDF generation test failed: {test_result.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"PDF service health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"PDF service error: {str(e)}"
            }
