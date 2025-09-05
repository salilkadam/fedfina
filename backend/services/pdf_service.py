"""
PDF Service for generating professional reports with Unicode support
"""
import logging
import io
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config import Settings
from models.openai_response_models import OpenAIStructuredResponse

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF reports"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.styles = getSampleStyleSheet()
        self._register_unicode_fonts()
        self._setup_custom_styles()

    def _register_unicode_fonts(self):
        """Register Unicode-compatible fonts for better symbol support"""
        try:
            # Try to register DejaVu fonts which have good Unicode coverage including Rupee symbol
            # These fonts are commonly available on most systems
            import os
            from reportlab.lib.fonts import addMapping
            
            # Try to find DejaVu fonts in common locations
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/',  # Ubuntu/Debian
                '/System/Library/Fonts/',  # macOS
                '/Windows/Fonts/',  # Windows
                '/usr/share/fonts/TTF/',  # Arch Linux
                '/usr/share/fonts/truetype/',  # General Linux
            ]
            
            dejavu_sans_found = False
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    # Try DejaVu Sans
                    dejavu_sans_path = os.path.join(font_path, 'DejaVuSans.ttf')
                    dejavu_sans_bold_path = os.path.join(font_path, 'DejaVuSans-Bold.ttf')
                    
                    if os.path.exists(dejavu_sans_path):
                        try:
                            pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_sans_path))
                            if os.path.exists(dejavu_sans_bold_path):
                                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_sans_bold_path))
                            addMapping('DejaVuSans', 0, 0, 'DejaVuSans')
                            addMapping('DejaVuSans', 1, 0, 'DejaVuSans-Bold')
                            dejavu_sans_found = True
                            logger.info("Successfully registered DejaVu Sans fonts for Unicode support")
                            break
                        except Exception as e:
                            logger.warning(f"Failed to register DejaVu Sans font from {dejavu_sans_path}: {e}")
                            continue
            
            if not dejavu_sans_found:
                # Fallback: Use Helvetica with manual Rupee symbol replacement
                logger.warning("DejaVu fonts not found, will use Helvetica with Rupee symbol fallback")
                self.use_unicode_fonts = False
            else:
                self.use_unicode_fonts = True
                
        except Exception as e:
            logger.error(f"Error registering Unicode fonts: {e}")
            self.use_unicode_fonts = False

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Choose font family based on Unicode support
        font_family = 'DejaVuSans' if self.use_unicode_fonts else 'Helvetica'
        font_family_bold = 'DejaVuSans-Bold' if self.use_unicode_fonts else 'Helvetica-Bold'
        
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName=font_family_bold,
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Custom heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontName=font_family_bold,
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Custom body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontName=font_family,
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Custom metadata style
        self.styles.add(ParagraphStyle(
            name='CustomMetadata',
            parent=self.styles['Normal'],
            fontName=font_family,
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT,
            textColor=colors.grey
        ))

    def _format_currency_text(self, text: str) -> str:
        """Format currency symbols in text for better PDF display"""
        if not text:
            return text
            
        if self.use_unicode_fonts:
            # DejaVu fonts support the Rupee symbol properly
            return text
        else:
            # Fallback: Replace Rupee symbol with "Rs." for better compatibility
            text = text.replace('₹', 'Rs. ')
            # Also handle other potential currency formatting issues
            text = text.replace('Rs.  ', 'Rs. ')  # Remove double spaces
            return text

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
            
            # Get parsed summary from metadata if available
            parsed_summary = metadata.get('parsed_summary')
            
            # Add header
            story.extend(self._create_header(conversation_id, metadata))
            
            # Add summary section
            story.extend(self._create_summary_section(summary, parsed_summary))
            
            # Add conversation quality assessment
            story.extend(self._create_conversation_quality_section(parsed_summary))
            
            # Add summary table
            story.extend(self._create_summary_table(parsed_summary, metadata))
            
            # Add income section
            story.extend(self._create_income_section(summary, parsed_summary))
            
            # Add expense section
            story.extend(self._create_expense_section(summary, parsed_summary))
            
            # Add loan section
            story.extend(self._create_loan_section(summary, parsed_summary))
            
            # Add risks section
            story.extend(self._create_risks_section(summary, transcript, parsed_summary))
            
            # Add opportunities section
            story.extend(self._create_opportunities_section(summary, transcript, parsed_summary))
            
            # Add recommendations section
            story.extend(self._create_recommendations_section(parsed_summary))
            
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
        
        # Try to extract customer info from parsed summary if available
        parsed_summary = metadata.get('parsed_summary')
        customer_name = 'Unknown'
        interview_date = 'Not specified'
        business_name = 'Not specified'
        
        if parsed_summary and isinstance(parsed_summary, dict):
            try:
                customer_info = parsed_summary.get('customer_info', {})
                customer_name = customer_info.get('name', metadata.get('account_id', 'Unknown'))
                interview_date = customer_info.get('interview_date', 'Not specified')
                business_name = customer_info.get('business_name', 'Not specified')
            except Exception as e:
                logger.error(f"Error extracting customer info from JSON: {e}")
                customer_name = metadata.get('account_id', 'Unknown')
        else:
            customer_name = metadata.get('account_id', 'Unknown')
        
        # Title with Customer Name
        title = Paragraph(
            f"Conversation Report: {customer_name}",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Customer Information Section
        if business_name != 'Not specified':
            business_para = Paragraph(
                f"<b>Business Name:</b> {business_name}",
                self.styles['CustomBody']
            )
            elements.append(business_para)
        
        # Interview Date/Time
        interview_para = Paragraph(
            f"<b>Interview Date/Time:</b> {interview_date}",
            self.styles['CustomBody']
        )
        elements.append(interview_para)
        
        # Report Generated Date
        timestamp = Paragraph(
            f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            self.styles['CustomBody']
        )
        elements.append(timestamp)
        
        # Conversation ID
        conv_id = Paragraph(
            f"<b>Conversation ID:</b> {conversation_id}",
            self.styles['CustomBody']
        )
        elements.append(conv_id)
        
        # Participants (extracted from transcript or JSON)
        if parsed_summary and isinstance(parsed_summary, dict):
            participants = self._extract_participants_from_json(parsed_summary, metadata.get('transcript', ''))
        else:
            participants = self._extract_participants(metadata.get('transcript', ''))
        
        if participants:
            participants_text = Paragraph(
                f"<b>Participants:</b> {participants}",
                self.styles['CustomBody']
            )
            elements.append(participants_text)
        
        elements.append(Spacer(1, 20))
        return elements

    def _extract_participants(self, transcript: str) -> str:
        """Extract participant names from transcript"""
        try:
            participants = set()
            lines = transcript.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('AI:') or line.startswith('User:'):
                    # Extract speaker name if available
                    if ':' in line:
                        speaker_part = line.split(':', 1)[0]
                        if speaker_part == 'AI':
                            participants.add('AI Assistant')
                        elif speaker_part == 'User':
                            # Try to extract actual name from the message
                            message_part = line.split(':', 1)[1] if ':' in line else ''
                            # Look for common name patterns
                            if 'मैं' in message_part or 'I am' in message_part:
                                # Extract name after "मैं" or "I am"
                                import re
                                name_match = re.search(r'(?:मैं|I am)\s+([A-Za-z\s]+)', message_part)
                                if name_match:
                                    participants.add(name_match.group(1).strip())
                                else:
                                    participants.add('Customer')
                            else:
                                participants.add('Customer')
            
            return ', '.join(sorted(participants)) if participants else 'AI Assistant, Customer'
            
        except Exception as e:
            logger.error(f"Error extracting participants: {e}")
            return 'AI Assistant, Customer'

    def _extract_participants_from_json(self, parsed_summary: dict, transcript: str) -> str:
        """Extract participant names from JSON data or fallback to transcript"""
        try:
            # Try to get customer name from JSON
            customer_info = parsed_summary.get('customer_info', {})
            customer_name = customer_info.get('name', 'Customer')
            
            # Check for additional speakers beyond AI and main customer
            risks = parsed_summary.get('risks', {})
            multiple_speakers = risks.get('multiple_speakers', '')
            
            # Only include additional speakers if they exist as a risk factor
            if (multiple_speakers and 
                multiple_speakers != "No specific information provided" and
                multiple_speakers.lower().startswith("yes")):
                # Extract the speaker names from the response
                if ":" in multiple_speakers:
                    additional_names = multiple_speakers.split(":", 1)[1].strip()
                    return f"AI Assistant, {customer_name}, {additional_names}"
                else:
                    return f"AI Assistant, {customer_name}, Additional Speakers"
            else:
                return f"AI Assistant, {customer_name}"
                
        except Exception as e:
            logger.error(f"Error extracting participants from JSON: {e}")
            # Fallback to transcript extraction
            return self._extract_participants(transcript)

    def _extract_income_info_from_json(self, parsed_summary: dict) -> str:
        """Extract income information from JSON data"""
        try:
            income_summary = parsed_summary.get('income_summary', {})
            
            # Build income information
            content_parts = []
            
            # Add summary
            summary = income_summary.get('summary', '')
            if summary and summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {summary}")
            
            # Add details as bullet points
            details = income_summary.get('details', [])
            if details and details != ["No specific information provided"]:
                content_parts.append("<b>Details:</b>")
                for detail in details:
                    formatted_detail = self._format_currency_text(detail)
                    content_parts.append(formatted_detail)
            
            # Add total monthly income
            total_income = income_summary.get('total_monthly_income', '')
            if total_income and total_income != "No specific information provided":
                formatted_total = self._format_currency_text(total_income)
                content_parts.append(f"<b>Total Monthly Income:</b> {formatted_total}")
            
            # Add seasonal variations
            seasonal = income_summary.get('seasonal_variations', '')
            if seasonal and seasonal != "No specific information provided":
                content_parts.append(f"<b>Seasonal Variations:</b> {seasonal}")
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Income information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting income info from JSON: {e}")
            return "Income information could not be extracted."

    def _extract_income_info_from_pydantic(self, parsed_summary: OpenAIStructuredResponse) -> str:
        """Extract income information from Pydantic model"""
        try:
            if not parsed_summary.income_summary:
                return "Income information not available in the conversation."
                
            income_summary = parsed_summary.income_summary
            
            # Build income information
            content_parts = []
            
            # Add summary
            if income_summary.summary and income_summary.summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {income_summary.summary}")
            
            # Add details as bullet points
            if income_summary.details and income_summary.details != ["No specific information provided"]:
                content_parts.append("<b>Details:</b>")
                for detail in income_summary.details:
                    formatted_detail = self._format_currency_text(detail)
                    content_parts.append(formatted_detail)
            
            # Add total monthly income
            if income_summary.total_monthly_income and income_summary.total_monthly_income != "No specific information provided":
                formatted_total = self._format_currency_text(income_summary.total_monthly_income)
                content_parts.append(f"<b>Total Monthly Income:</b> {formatted_total}")
            
            # Add seasonal variations
            if income_summary.seasonal_variations and income_summary.seasonal_variations != "No specific information provided":
                content_parts.append(f"<b>Seasonal Variations:</b> {income_summary.seasonal_variations}")
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Income information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting income info from Pydantic model: {e}")
            return "Income information could not be extracted."

    def _extract_expense_info_from_pydantic(self, parsed_summary: OpenAIStructuredResponse) -> str:
        """Extract expense information from Pydantic model"""
        try:
            expense_summary = parsed_summary.expense_summary
            
            # Build expense information
            content_parts = []
            
            # Add summary
            if expense_summary.summary and expense_summary.summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {expense_summary.summary}")
            
            # Add business expenses
            if expense_summary.business_expenses and expense_summary.business_expenses != ["No specific information provided"]:
                content_parts.append("<b>Business Expenses:</b>")
                for expense in expense_summary.business_expenses:
                    formatted_expense = self._format_currency_text(expense)
                    content_parts.append(formatted_expense)
            
            # Add personal expenses
            if expense_summary.personal_expenses and expense_summary.personal_expenses != ["No specific information provided"]:
                content_parts.append("<b>Personal Expenses:</b>")
                for expense in expense_summary.personal_expenses:
                    formatted_expense = self._format_currency_text(expense)
                    content_parts.append(formatted_expense)
            
            # Add total monthly expenses
            if expense_summary.total_monthly_expenses and expense_summary.total_monthly_expenses != "No specific information provided":
                formatted_total = self._format_currency_text(expense_summary.total_monthly_expenses)
                content_parts.append(f"<b>Total Monthly Expenses:</b> {formatted_total}")
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Expense information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting expense info from Pydantic model: {e}")
            return "Expense information could not be extracted."

    def _extract_expense_info_from_json(self, parsed_summary: dict) -> str:
        """Extract expense information from JSON data"""
        try:
            expense_summary = parsed_summary.get('expense_summary', {})
            
            # Build expense information
            content_parts = []
            
            # Add summary
            summary = expense_summary.get('summary', '')
            if summary and summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {summary}")
            
            # Add business expenses
            business_expenses = expense_summary.get('business_expenses', [])
            if business_expenses and business_expenses != ["No specific information provided"]:
                content_parts.append("<b>Business Expenses:</b>")
                for expense in business_expenses:
                    formatted_expense = self._format_currency_text(expense)
                    content_parts.append(formatted_expense)
            
            # Add personal expenses
            personal_expenses = expense_summary.get('personal_expenses', [])
            if personal_expenses and personal_expenses != ["No specific information provided"]:
                content_parts.append("<b>Personal Expenses:</b>")
                for expense in personal_expenses:
                    formatted_expense = self._format_currency_text(expense)
                    content_parts.append(formatted_expense)
            
            # Add total monthly expenses
            total_expenses = expense_summary.get('total_monthly_expenses', '')
            if total_expenses and total_expenses != "No specific information provided":
                formatted_total = self._format_currency_text(total_expenses)
                content_parts.append(f"<b>Total Monthly Expenses:</b> {formatted_total}")
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Expense information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting expense info from JSON: {e}")
            return "Expense information could not be extracted."

    def _extract_loan_info_from_pydantic(self, parsed_summary: OpenAIStructuredResponse) -> str:
        """Extract loan disbursement information from Pydantic model"""
        try:
            loan_summary = parsed_summary.loan_disbursement_summary
            
            # Build loan information
            content_parts = []
            
            # Add summary
            if loan_summary.summary and loan_summary.summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {loan_summary.summary}")
            
            # Add requested amount
            if loan_summary.requested_amount and loan_summary.requested_amount != "No specific information provided":
                formatted_amount = self._format_currency_text(loan_summary.requested_amount)
                content_parts.append(f"<b>Requested Amount:</b> {formatted_amount}")
            
            # Add purposes
            if loan_summary.purposes and loan_summary.purposes != ["No specific information provided"]:
                content_parts.append("<b>Purposes:</b>")
                for purpose in loan_summary.purposes:
                    formatted_purpose = self._format_currency_text(purpose)
                    content_parts.append(formatted_purpose)
            
            # Add repayment plan
            if loan_summary.repayment_plan and loan_summary.repayment_plan != "No specific information provided":
                formatted_repayment = self._format_currency_text(loan_summary.repayment_plan)
                content_parts.append(f"<b>Repayment Plan:</b> {formatted_repayment}")
            
            # Add timeline
            if loan_summary.timeline and loan_summary.timeline != "No specific information provided":
                content_parts.append(f"<b>Timeline:</b> {loan_summary.timeline}")
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Loan disbursement information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting loan info from Pydantic model: {e}")
            return "Loan disbursement information could not be extracted."

    def _extract_loan_info_from_json(self, parsed_summary: dict) -> str:
        """Extract loan information from JSON data"""
        try:
            loan_summary = parsed_summary.get('loan_disbursement_summary', {})
            
            # Build loan information
            content_parts = []
            
            # Add summary
            summary = loan_summary.get('summary', '')
            if summary and summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {summary}")
            
            # Add requested amount
            requested_amount = loan_summary.get('requested_amount', '')
            if requested_amount and requested_amount != "No specific information provided":
                formatted_amount = self._format_currency_text(requested_amount)
                content_parts.append(f"<b>Requested Amount:</b> {formatted_amount}")
            
            # Add purposes as bullet points
            purposes = loan_summary.get('purposes', [])
            if purposes and purposes != ["No specific information provided"]:
                content_parts.append("<b>Purposes:</b>")
                for purpose in purposes:
                    formatted_purpose = self._format_currency_text(purpose)
                    content_parts.append(formatted_purpose)
            
            # Add repayment plan
            repayment_plan = loan_summary.get('repayment_plan', '')
            if repayment_plan and repayment_plan != "No specific information provided":
                formatted_repayment = self._format_currency_text(repayment_plan)
                content_parts.append(f"<b>Repayment Plan:</b> {formatted_repayment}")
            
            # Add timeline
            timeline = loan_summary.get('timeline', '')
            if timeline and timeline != "No specific information provided":
                content_parts.append(f"<b>Timeline:</b> {timeline}")
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Loan disbursement information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting loan info from JSON: {e}")
            return "Loan information could not be extracted."

    def _extract_risks_info_from_pydantic(self, parsed_summary: OpenAIStructuredResponse, transcript: str = "") -> str:
        """Extract risks information from Pydantic model"""
        try:
            risks = parsed_summary.risks
            
            # Build risks information
            content_parts = []
            
            # Add summary
            if risks.summary and risks.summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {risks.summary}")
            
            # Add multiple speakers risk
            if risks.multiple_speakers and risks.multiple_speakers != "No":
                content_parts.append(f"<b>Multiple Speakers Risk:</b> {risks.multiple_speakers}")
            
            # Add risks details
            if hasattr(risks, 'details') and risks.details and risks.details != ["No specific information provided"]:
                for risk in risks.details:
                    content_parts.append(risk)
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "No significant risks identified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting risks info from Pydantic model: {e}")
            return "Risk information could not be extracted."

    def _extract_risks_info_from_json(self, parsed_summary: dict, transcript: str) -> str:
        """Extract risk information from JSON data"""
        try:
            risks = parsed_summary.get('risks', {})
            
            # Build risks information
            content_parts = []
            
            # Add summary
            summary = risks.get('summary', '')
            if summary and summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {summary}")
            
            # Add multiple speakers risk (only if additional speakers beyond AI and customer)
            multiple_speakers = risks.get('multiple_speakers', '')
            if (multiple_speakers and 
                multiple_speakers != "No specific information provided" and
                multiple_speakers.lower().startswith("yes")):
                content_parts.append(f"<b>Multiple Speakers Risk:</b> {multiple_speakers}")
            # If it's "No" or not provided, don't add as a risk
            
            # Add risks details
            risks_details = risks.get('details', [])
            if risks_details and risks_details != ["No specific information provided"]:
                for risk in risks_details:
                    content_parts.append(risk)
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "No specific risks identified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting risks info from JSON: {e}")
            return "Risk information could not be extracted."

    def _create_summary_section(self, summary: str, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the summary section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Summary",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Try to use parsed data first (Pydantic model or dict)
        if parsed_summary:
            try:
                if isinstance(parsed_summary, OpenAIStructuredResponse):
                    # Use Pydantic model
                    if parsed_summary.executive_summary:
                        exec_summary = parsed_summary.executive_summary.overview
                        if exec_summary and exec_summary != "No specific information provided":
                            summary_content = exec_summary
                        else:
                            summary_content = summary
                    else:
                        summary_content = summary
                elif isinstance(parsed_summary, dict):
                    # Fallback to dict access
                    exec_summary = parsed_summary.get('executive_summary', {}).get('overview', '')
                    if exec_summary and exec_summary != "No specific information provided":
                        summary_content = exec_summary
                    else:
                        summary_content = summary
                else:
                    summary_content = summary
            except Exception as e:
                logger.error(f"Error extracting executive summary from parsed data: {e}")
                summary_content = summary
        else:
            # Fallback to regex extraction for backward compatibility
            import re
            
            # First try to extract from JSON-like structure in the raw text
            # Look for the executive summary overview in the JSON structure
            exec_summary_start = summary.find('"overview":')
            if exec_summary_start != -1:
                # Find the start of the actual content (after the quote)
                content_start = summary.find('"', exec_summary_start + len('"overview":'))
                if content_start != -1:
                    content_start += 1  # Skip the opening quote
                    # Find the end of the content (closing quote, but not escaped quotes)
                    content_end = content_start
                    while content_end < len(summary):
                        if summary[content_end] == '"' and (content_end == 0 or summary[content_end-1] != '\\'):
                            break
                        content_end += 1
                    
                    if content_end < len(summary):
                        exec_summary = summary[content_start:content_end].strip()
                        # Clean up any escaped characters
                        exec_summary = exec_summary.replace('\\"', '"').replace('\\n', '\n')
                        if exec_summary and len(exec_summary) > 50:  # Ensure it's substantial
                            summary_content = exec_summary
                        else:
                            summary_content = "This is a business loan interview analysis. Please refer to the detailed sections below for specific financial information and loan requirements."
                    else:
                        summary_content = "This is a business loan interview analysis. Please refer to the detailed sections below for specific financial information and loan requirements."
                else:
                    summary_content = "This is a business loan interview analysis. Please refer to the detailed sections below for specific financial information and loan requirements."
            else:
                # Try traditional section-based extraction
                exec_summary_match = re.search(r'EXECUTIVE SUMMARY:\s*(.*?)(?=\n\n|\n[A-Z]|$)', summary, re.DOTALL | re.IGNORECASE)
                
                if exec_summary_match:
                    exec_summary = exec_summary_match.group(1).strip()
                    if exec_summary and exec_summary != "No specific information provided":
                        summary_content = exec_summary
                    else:
                        # If no proper executive summary found, create a generic one
                        summary_content = "This is a business loan interview analysis. Please refer to the detailed sections below for specific financial information and loan requirements."
                else:
                    # Last resort: create a generic executive summary
                    summary_content = "This is a business loan interview analysis. Please refer to the detailed sections below for specific financial information and loan requirements."
        
        # Summary content
        summary_para = Paragraph(
            summary_content,
            self.styles['CustomBody']
        )
        elements.append(summary_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_summary_table(self, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None, metadata: Dict[str, Any] = None) -> List:
        """Create a summary table with key information"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Key Information Summary",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Prepare table data
        table_data = []
        
        try:
            if parsed_summary and isinstance(parsed_summary, OpenAIStructuredResponse):
                # Extract data from Pydantic model
                customer_name = parsed_summary.customer_info.name if parsed_summary.customer_info else "Not specified"
                business_name = parsed_summary.customer_info.business_name if parsed_summary.customer_info else "Not specified"
                interview_date = parsed_summary.customer_info.interview_date if parsed_summary.customer_info else "Not specified"
                total_income = parsed_summary.income_summary.total_monthly_income if parsed_summary.income_summary else "Not specified"
                requested_amount = parsed_summary.loan_disbursement_summary.requested_amount if parsed_summary.loan_disbursement_summary else "Not specified"
                repayment_plan = parsed_summary.loan_disbursement_summary.repayment_plan if parsed_summary.loan_disbursement_summary else "Not specified"
                multiple_speakers = parsed_summary.risks.multiple_speakers if parsed_summary.risks else "No"
                
            elif parsed_summary and isinstance(parsed_summary, dict):
                # Extract data from dict
                customer_info = parsed_summary.get('customer_info', {})
                income_info = parsed_summary.get('income_summary', {})
                loan_info = parsed_summary.get('loan_disbursement_summary', {})
                risks_info = parsed_summary.get('risks', {})
                
                customer_name = customer_info.get('name', 'Not specified')
                business_name = customer_info.get('business_name', 'Not specified')
                interview_date = customer_info.get('interview_date', 'Not specified')
                total_income = income_info.get('total_monthly_income', 'Not specified')
                requested_amount = loan_info.get('requested_amount', 'Not specified')
                repayment_plan = loan_info.get('repayment_plan', 'Not specified')
                multiple_speakers = risks_info.get('multiple_speakers', 'No')
                
            else:
                # Fallback values
                customer_name = metadata.get('account_id', 'Not specified') if metadata else 'Not specified'
                business_name = "Not specified"
                interview_date = "Not specified"
                total_income = "Not specified"
                requested_amount = "Not specified"
                repayment_plan = "Not specified"
                multiple_speakers = "No"
            
            # Extract opportunities information
            opportunities_summary = "Not specified"
            if parsed_summary and isinstance(parsed_summary, OpenAIStructuredResponse):
                if parsed_summary.opportunities and parsed_summary.opportunities.summary:
                    opportunities_summary = parsed_summary.opportunities.summary
            elif parsed_summary and isinstance(parsed_summary, dict):
                opportunities_info = parsed_summary.get('opportunities', {})
                opportunities_summary = opportunities_info.get('summary', 'Not specified')
            
            # Build table data
            table_data = [
                ["Field", "Information"],
                ["Customer Name", customer_name],
                ["Business Name", business_name],
                ["Interview Date", interview_date],
                ["Total Monthly Income", total_income],
                ["Requested Loan Amount", requested_amount],
                ["Proposed Repayment", repayment_plan],
                ["Key Opportunities", opportunities_summary[:100] + "..." if len(opportunities_summary) > 100 else opportunities_summary],
                ["Multiple Speakers Risk", multiple_speakers]
            ]
            
        except Exception as e:
            logger.error(f"Error creating summary table: {e}")
            table_data = [
                ["Field", "Information"],
                ["Error", "Unable to extract summary information"]
            ]
        
        # Create table
        table = Table(table_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Alternating row colors
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
            ('BACKGROUND', (0, 6), (-1, 6), colors.lightgrey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        return elements

    def _create_income_section(self, summary: str, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the income summary section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Income Summary and Details",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Try to use parsed data first (Pydantic model or dict)
        if parsed_summary:
            if isinstance(parsed_summary, OpenAIStructuredResponse):
                income_info = self._extract_income_info_from_pydantic(parsed_summary)
            elif isinstance(parsed_summary, dict):
                income_info = self._extract_income_info_from_json(parsed_summary)
            else:
                income_info = self._extract_income_info(summary)
        else:
            # Fallback to regex extraction
            income_info = self._extract_income_info(summary)
        
        income_para = Paragraph(
            income_info,
            self.styles['CustomBody']
        )
        elements.append(income_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_expense_section(self, summary: str, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the expense summary section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Expense Summary and Details",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Try to use parsed data first (Pydantic model or dict)
        if parsed_summary:
            if isinstance(parsed_summary, OpenAIStructuredResponse):
                expense_info = self._extract_expense_info_from_pydantic(parsed_summary)
            elif isinstance(parsed_summary, dict):
                expense_info = self._extract_expense_info_from_json(parsed_summary)
            else:
                expense_info = self._extract_expense_info(summary)
        else:
            # Fallback to regex extraction
            expense_info = self._extract_expense_info(summary)
        
        expense_para = Paragraph(
            expense_info,
            self.styles['CustomBody']
        )
        elements.append(expense_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_loan_section(self, summary: str, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the loan disbursement summary section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Loan Disbursement Summary and Details",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Try to use parsed data first (Pydantic model or dict)
        if parsed_summary:
            if isinstance(parsed_summary, OpenAIStructuredResponse):
                loan_info = self._extract_loan_info_from_pydantic(parsed_summary)
            elif isinstance(parsed_summary, dict):
                loan_info = self._extract_loan_info_from_json(parsed_summary)
            else:
                loan_info = self._extract_loan_info(summary)
        else:
            # Fallback to regex extraction
            loan_info = self._extract_loan_info(summary)
        
        loan_para = Paragraph(
            loan_info,
            self.styles['CustomBody']
        )
        elements.append(loan_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_risks_section(self, summary: str, transcript: str, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the risks section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Risks",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Try to use parsed data first (Pydantic model or dict)
        if parsed_summary:
            if isinstance(parsed_summary, OpenAIStructuredResponse):
                risks_info = self._extract_risks_info_from_pydantic(parsed_summary, transcript)
            elif isinstance(parsed_summary, dict):
                risks_info = self._extract_risks_info_from_json(parsed_summary, transcript)
            else:
                risks_info = self._extract_risks_info(summary, transcript)
        else:
            # Fallback to regex extraction
            risks_info = self._extract_risks_info(summary, transcript)
        
        risks_para = Paragraph(
            risks_info,
            self.styles['CustomBody']
        )
        elements.append(risks_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_opportunities_section(self, summary: str, transcript: str, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the opportunities section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Opportunities",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Try to use parsed data first (Pydantic model or dict)
        if parsed_summary:
            if isinstance(parsed_summary, OpenAIStructuredResponse):
                opportunities_info = self._extract_opportunities_info_from_pydantic(parsed_summary, transcript)
            elif isinstance(parsed_summary, dict):
                opportunities_info = self._extract_opportunities_info_from_json(parsed_summary, transcript)
            else:
                opportunities_info = self._extract_opportunities_info(summary, transcript)
        else:
            # Fallback to regex extraction
            opportunities_info = self._extract_opportunities_info(summary, transcript)
        
        opportunities_para = Paragraph(
            opportunities_info,
            self.styles['CustomBody']
        )
        elements.append(opportunities_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_recommendations_section(self, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the recommendations section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Recommendations",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        # Extract recommendations from parsed summary
        recommendations_content = self._extract_recommendations_from_parsed_summary(parsed_summary)
        
        recommendations_para = Paragraph(
            recommendations_content,
            self.styles['CustomBody']
        )
        elements.append(recommendations_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def _extract_recommendations_from_parsed_summary(self, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> str:
        """Extract recommendations from parsed summary"""
        try:
            if parsed_summary:
                if isinstance(parsed_summary, dict):
                    recommendations = parsed_summary.get('recommendations', {})
                elif hasattr(parsed_summary, 'recommendations') and parsed_summary.recommendations:
                    # Handle Pydantic model
                    rec_obj = parsed_summary.recommendations
                    recommendations = {
                        'loan_recommendation': getattr(rec_obj, 'loan_recommendation', 'No recommendation provided'),
                        'growth_recommendations': getattr(rec_obj, 'growth_recommendations', 'No recommendation provided'),
                        'financial_management_recommendations': getattr(rec_obj, 'financial_management_recommendations', 'No recommendation provided'),
                        'general_recommendations': getattr(rec_obj, 'general_recommendations', 'No recommendation provided')
                    }
                else:
                    recommendations = {}
                
                # Build recommendations content
                content_parts = []
                
                # Loan recommendations
                loan_rec = recommendations.get('loan_recommendation', 'No recommendation provided')
                if loan_rec and loan_rec != "No recommendation provided":
                    content_parts.append(f"<b>Loan Recommendation:</b> {loan_rec}")
                
                # Growth recommendations
                growth_rec = recommendations.get('growth_recommendations', 'No recommendation provided')
                if growth_rec and growth_rec != "No recommendation provided":
                    content_parts.append(f"<b>Growth Recommendations:</b> {growth_rec}")
                
                # Financial management recommendations
                financial_rec = recommendations.get('financial_management_recommendations', 'No recommendation provided')
                if financial_rec and financial_rec != "No recommendation provided":
                    content_parts.append(f"<b>Financial Management Recommendations:</b> {financial_rec}")
                
                # General recommendations
                general_rec = recommendations.get('general_recommendations', 'No recommendation provided')
                if general_rec and general_rec != "No recommendation provided":
                    content_parts.append(f"<b>General Recommendations:</b> {general_rec}")
                
                if content_parts:
                    return "<br/><br/>".join(content_parts)
                else:
                    return "No specific recommendations available based on the conversation analysis."
            else:
                return "No recommendations data available."
                
        except Exception as e:
            logger.error(f"Error extracting recommendations from parsed summary: {e}")
            return "Error occurred while extracting recommendations."

    def _generate_recommendations(self, summary: str, transcript: str, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> str:
        """Generate recommendations based on the analysis"""
        try:
            recommendations = []
            
            # Extract key information for recommendations
            income_info = None
            expense_info = None
            loan_info = None
            risks_info = None
            opportunities_info = None
            
            if parsed_summary and isinstance(parsed_summary, OpenAIStructuredResponse):
                income_info = parsed_summary.income_summary
                expense_info = parsed_summary.expense_summary
                loan_info = parsed_summary.loan_disbursement_summary
                risks_info = parsed_summary.risks
                opportunities_info = parsed_summary.opportunities
            elif parsed_summary and isinstance(parsed_summary, dict):
                income_info = parsed_summary.get('income_summary', {})
                expense_info = parsed_summary.get('expense_summary', {})
                loan_info = parsed_summary.get('loan_disbursement_summary', {})
                risks_info = parsed_summary.get('risks', {})
                opportunities_info = parsed_summary.get('opportunities', {})
            
            # Generate loan recommendations
            if loan_info:
                requested_amount = None
                if isinstance(loan_info, dict):
                    requested_amount = loan_info.get('requested_amount', '')
                else:
                    requested_amount = loan_info.requested_amount if loan_info else ''
                
                if requested_amount and requested_amount != "No specific information provided":
                    recommendations.append("<b>Loan Recommendation:</b>")
                    recommendations.append("• Consider the requested loan amount based on business cash flow analysis")
                    recommendations.append("• Review repayment capacity against current income and expenses")
                    recommendations.append("• Assess collateral requirements and risk mitigation strategies")
            
            # Generate risk-based recommendations
            if risks_info:
                multiple_speakers = None
                if isinstance(risks_info, dict):
                    multiple_speakers = risks_info.get('multiple_speakers', 'No')
                else:
                    multiple_speakers = risks_info.multiple_speakers if risks_info else 'No'
                
                if multiple_speakers and multiple_speakers != "No":
                    recommendations.append("<b>Verification Recommendations:</b>")
                    recommendations.append("• Conduct additional verification due to multiple speakers in conversation")
                    recommendations.append("• Verify primary applicant's identity and business ownership")
                    recommendations.append("• Cross-reference information provided by all speakers")
            
            # Generate opportunity-based recommendations
            if opportunities_info:
                if isinstance(opportunities_info, dict):
                    has_opportunities = opportunities_info.get('summary') and opportunities_info.get('summary') != "No specific information provided"
                else:
                    has_opportunities = opportunities_info.summary if opportunities_info else False
                
                if has_opportunities:
                    recommendations.append("<b>Growth Recommendations:</b>")
                    recommendations.append("• Leverage identified business strengths for loan approval")
                    recommendations.append("• Consider expansion opportunities in loan utilization plan")
                    recommendations.append("• Develop strategies to capitalize on market opportunities")
            
            # Generate financial recommendations
            if income_info and expense_info:
                recommendations.append("<b>Financial Management Recommendations:</b>")
                recommendations.append("• Maintain detailed financial records for future loan applications")
                recommendations.append("• Consider diversifying income sources to reduce risk")
                recommendations.append("• Implement cost control measures to improve profitability")
            
            # General recommendations
            recommendations.append("<b>General Recommendations:</b>")
            recommendations.append("• Conduct thorough due diligence before loan disbursement")
            recommendations.append("• Establish clear loan terms and repayment schedules")
            recommendations.append("• Monitor business performance post-disbursement")
            recommendations.append("• Provide ongoing support and guidance to the borrower")
            
            if recommendations:
                return "<br/><br/>".join(recommendations)
            else:
                return "Recommendations will be generated based on detailed analysis of the conversation."
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return "Unable to generate specific recommendations at this time."

    def _extract_income_info(self, summary: str) -> str:
        """Extract income information from summary"""
        try:
            # Look for the INCOME SUMMARY section
            import re
            income_match = re.search(r'INCOME SUMMARY:\s*(.*?)(?=\n\n|\n[A-Z]|$)', summary, re.DOTALL | re.IGNORECASE)
            
            if income_match:
                income_content = income_match.group(1).strip()
                if income_content and income_content != "No specific information provided":
                    return income_content
                else:
                    return "Income information not clearly specified in the conversation."
            else:
                # Fallback to pattern matching
                income_patterns = [
                    r'income[:\s]*₹?([0-9,]+)',
                    r'earning[:\s]*₹?([0-9,]+)',
                    r'revenue[:\s]*₹?([0-9,]+)',
                    r'generates[:\s]*₹?([0-9,]+)'
                ]
                
                for pattern in income_patterns:
                    match = re.search(pattern, summary, re.IGNORECASE)
                    if match:
                        amount = match.group(1)
                        return f"Monthly Income: ₹{amount}\n\nAdditional income details extracted from the conversation analysis."
                
                return "Income information not clearly specified in the conversation."
            
        except Exception as e:
            logger.error(f"Error extracting income info: {e}")
            return "Income information could not be extracted."

    def _extract_expense_info(self, summary: str) -> str:
        """Extract expense information from summary"""
        try:
            # Look for the EXPENSE SUMMARY section
            import re
            expense_match = re.search(r'EXPENSE SUMMARY:\s*(.*?)(?=\n\n|\n[A-Z]|$)', summary, re.DOTALL | re.IGNORECASE)
            
            if expense_match:
                expense_content = expense_match.group(1).strip()
                if expense_content and expense_content != "No specific information provided":
                    return expense_content
                else:
                    return "Expense information not clearly specified in the conversation."
            else:
                # Fallback to pattern matching
                expense_patterns = [
                    r'expenses[:\s]*₹?([0-9,]+)',
                    r'costs[:\s]*₹?([0-9,]+)',
                    r'expenditure[:\s]*₹?([0-9,]+)',
                    r'rent[:\s]*₹?([0-9,]+)',
                    r'salary[:\s]*₹?([0-9,]+)'
                ]
                
                for pattern in expense_patterns:
                    match = re.search(pattern, summary, re.IGNORECASE)
                    if match:
                        amount = match.group(1)
                        return f"Monthly Expenses: ₹{amount}\n\nExpense breakdown extracted from the conversation analysis."
                
                return "Expense information not clearly specified in the conversation."
            
        except Exception as e:
            logger.error(f"Error extracting expense info: {e}")
            return "Expense information could not be extracted."

    def _extract_loan_info(self, summary: str) -> str:
        """Extract loan information from summary"""
        try:
            # Look for the LOAN DISBURSEMENT SUMMARY section
            import re
            loan_match = re.search(r'LOAN DISBURSEMENT SUMMARY:\s*(.*?)(?=\n\n|\n[A-Z]|$)', summary, re.DOTALL | re.IGNORECASE)
            
            if loan_match:
                loan_content = loan_match.group(1).strip()
                if loan_content and loan_content != "No specific information provided":
                    return loan_content
                else:
                    return "Loan disbursement information not clearly specified in the conversation."
            else:
                # Fallback to pattern matching
                loan_patterns = [
                    r'loan[:\s]*₹?([0-9,]+)',
                    r'disbursement[:\s]*₹?([0-9,]+)',
                    r'borrowing[:\s]*₹?([0-9,]+)',
                    r'amount[:\s]*₹?([0-9,]+)'
                ]
                
                for pattern in loan_patterns:
                    match = re.search(pattern, summary, re.IGNORECASE)
                    if match:
                        amount = match.group(1)
                        return f"Loan Amount: ₹{amount}\n\nLoan disbursement details extracted from the conversation analysis."
                
                return "Loan disbursement information not clearly specified in the conversation."
            
        except Exception as e:
            logger.error(f"Error extracting loan info: {e}")
            return "Loan information could not be extracted."

    def _extract_risks_info(self, summary: str, transcript: str) -> str:
        """Extract risk information from summary and transcript"""
        try:
            # Look for the RISKS section
            import re
            risks_match = re.search(r'RISKS:\s*(.*?)(?=\n\n|\n[A-Z]|$)', summary, re.DOTALL | re.IGNORECASE)
            
            if risks_match:
                risks_content = risks_match.group(1).strip()
                if risks_content and risks_content != "No specific information provided":
                    return risks_content
                else:
                    return "No specific risks identified in the conversation."
            else:
                # Fallback to risk detection
                risks = []
                
                # Check for additional speakers beyond AI and Customer
                speakers = set([line.split(':')[0] for line in transcript.split('\n') if ':' in line])
                expected_speakers = {'AI', 'User', 'Assistant', 'Customer'}
                additional_speakers = speakers - expected_speakers
                if additional_speakers:
                    risks.append(f"Additional speakers detected beyond AI and customer: {', '.join(additional_speakers)}")
                elif len(speakers) > 2:
                    # Only flag if there are clearly more than just AI and one customer
                    unique_non_ai = [s for s in speakers if s.lower() not in ['ai', 'assistant']]
                    if len(unique_non_ai) > 1:
                        risks.append("Multiple customer speakers identified in conversation")
                
                # Look for risk-related keywords in summary
                risk_keywords = ['risk', 'concern', 'issue', 'problem', 'inconsistent', 'unclear', 'missing']
                for keyword in risk_keywords:
                    if keyword.lower() in summary.lower():
                        risks.append(f"Potential {keyword} identified in conversation")
                
                # Check for financial inconsistencies
                if 'inconsistent' in summary.lower() or 'discrepancy' in summary.lower():
                    risks.append("Financial inconsistencies detected")
                
                if risks:
                    return "\n".join(risks)
                else:
                    return "No specific risks identified in the conversation."
            
        except Exception as e:
            logger.error(f"Error extracting risks info: {e}")
            return "Risk information could not be extracted."

    def _extract_opportunities_info_from_pydantic(self, parsed_summary: OpenAIStructuredResponse, transcript: str = "") -> str:
        """Extract opportunities information from Pydantic model"""
        try:
            if not parsed_summary.opportunities:
                return "Opportunities information not available in the conversation."
                
            opportunities = parsed_summary.opportunities
            
            # Build opportunities information
            content_parts = []
            
            # Add summary
            if opportunities.summary and opportunities.summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {opportunities.summary}")
            
            # Add opportunities details
            if hasattr(opportunities, 'details') and opportunities.details and opportunities.details != ["No specific information provided"]:
                for opportunity in opportunities.details:
                    content_parts.append(opportunity)
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Opportunities information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting opportunities info from Pydantic model: {e}")
            return "Opportunities information could not be extracted."

    def _extract_opportunities_info_from_json(self, parsed_summary: dict, transcript: str) -> str:
        """Extract opportunities information from JSON data"""
        try:
            opportunities = parsed_summary.get('opportunities', {})
            
            # Build opportunities information
            content_parts = []
            
            # Add summary
            summary = opportunities.get('summary', '')
            if summary and summary != "No specific information provided":
                content_parts.append(f"<b>Overview:</b> {summary}")
            
            # Add opportunities details
            opportunities_details = opportunities.get('details', [])
            if opportunities_details and opportunities_details != ["No specific information provided"]:
                for opportunity in opportunities_details:
                    content_parts.append(opportunity)
            
            if content_parts:
                return "<br/><br/>".join(content_parts)
            else:
                return "Opportunities information not clearly specified in the conversation."
                
        except Exception as e:
            logger.error(f"Error extracting opportunities info from JSON: {e}")
            return "Opportunities information could not be extracted."

    def _extract_opportunities_info(self, summary: str, transcript: str) -> str:
        """Extract opportunities information from summary and transcript"""
        try:
            # Look for the OPPORTUNITIES section
            import re
            opportunities_match = re.search(r'OPPORTUNITIES:\s*(.*?)(?=\n\n|\n[A-Z]|$)', summary, re.DOTALL | re.IGNORECASE)
            
            if opportunities_match:
                opportunities_content = opportunities_match.group(1).strip()
                if opportunities_content and opportunities_content != "No specific information provided":
                    return opportunities_content
                else:
                    return "No specific opportunities identified in the conversation."
            else:
                # Fallback to opportunity detection
                opportunities = []
                
                # Look for positive keywords in summary
                positive_keywords = ['strong', 'good', 'excellent', 'opportunity', 'potential', 'growth', 'advantage', 'strength', 'positive']
                for keyword in positive_keywords:
                    if keyword.lower() in summary.lower():
                        opportunities.append(f"Positive {keyword} identified in conversation")
                
                # Check for business strengths mentioned
                strength_keywords = ['experience', 'location', 'customer', 'quality', 'service', 'reputation']
                for keyword in strength_keywords:
                    if keyword.lower() in summary.lower():
                        opportunities.append(f"Business strength in {keyword} identified")
                
                if opportunities:
                    return "\n".join(opportunities)
                else:
                    return "No specific opportunities identified in the conversation."
            
        except Exception as e:
            logger.error(f"Error extracting opportunities info: {e}")
            return "Opportunities information could not be extracted."

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

    def _create_conversation_quality_section(self, parsed_summary: Union[OpenAIStructuredResponse, dict, None] = None) -> List:
        """Create the conversation quality assessment section"""
        elements = []
        
        # Section title
        title = Paragraph(
            "Conversation Quality Assessment",
            self.styles['CustomHeading']
        )
        elements.append(title)
        
        try:
            if parsed_summary:
                if isinstance(parsed_summary, dict):
                    quality_info = parsed_summary.get('conversation_quality', {})
                elif hasattr(parsed_summary, 'conversation_quality') and parsed_summary.conversation_quality:
                    # Handle Pydantic model
                    quality_obj = parsed_summary.conversation_quality
                    quality_info = {
                        'completeness': getattr(quality_obj, 'completeness', 'Not assessed'),
                        'financial_information_available': getattr(quality_obj, 'financial_information_available', 'Not assessed'),
                        'recommendation': getattr(quality_obj, 'recommendation', 'No recommendation provided')
                    }
                else:
                    quality_info = {}
                
                # Build quality assessment content
                content_parts = []
                
                # Completeness
                completeness = quality_info.get('completeness', 'Not assessed')
                content_parts.append(f"<b>Conversation Completeness:</b> {completeness}")
                
                # Financial information availability
                financial_info = quality_info.get('financial_information_available', 'Not assessed')
                content_parts.append(f"<b>Financial Information Available:</b> {financial_info}")
                
                # Recommendation
                recommendation = quality_info.get('recommendation', 'No recommendation provided')
                content_parts.append(f"<b>Recommendation:</b> {recommendation}")
                
                # Add warning if conversation is incomplete
                if completeness.lower() in ['incomplete', 'partial']:
                    content_parts.append("<br/><b>⚠️ WARNING:</b> This conversation appears to be incomplete. The financial analysis below may contain limited or no information.")
                
                if financial_info.lower() == 'no':
                    content_parts.append("<br/><b>⚠️ NOTE:</b> This conversation did not contain sufficient financial information for a complete loan assessment.")
                
                # Create the content paragraph
                if content_parts:
                    content = "<br/><br/>".join(content_parts)
                    content_para = Paragraph(content, self.styles['CustomBody'])
                    elements.append(content_para)
                else:
                    # Fallback if no quality info available
                    fallback_content = """
                    <b>Conversation Quality Assessment:</b> Not available<br/>
                    <b>Note:</b> This report was generated without quality assessment data.
                    """
                    fallback_para = Paragraph(fallback_content, self.styles['CustomBody'])
                    elements.append(fallback_para)
            else:
                # No parsed summary available
                fallback_content = """
                <b>Conversation Quality Assessment:</b> Not available<br/>
                <b>Note:</b> This report was generated without structured analysis data.
                """
                fallback_para = Paragraph(fallback_content, self.styles['CustomBody'])
                elements.append(fallback_para)
            
            elements.append(Spacer(1, 20))
            return elements
            
        except Exception as e:
            logger.error(f"Error creating conversation quality section: {e}")
            # Fallback content
            fallback_content = """
            <b>Conversation Quality Assessment:</b> Error occurred during assessment<br/>
            <b>Note:</b> Please review the conversation manually for completeness.
            """
            fallback_para = Paragraph(fallback_content, self.styles['CustomBody'])
            elements.append(fallback_para)
            elements.append(Spacer(1, 20))
            return elements

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
