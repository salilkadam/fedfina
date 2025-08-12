"""
Email Service for sending PDF reports
"""
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from datetime import datetime
from config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with PDF attachments"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.from_email = settings.smtp_from_email

    async def send_conversation_report(
        self,
        to_email: str,
        conversation_id: str,
        pdf_bytes: bytes,
        metadata: Dict[str, Any],
        account_id: str = None
    ) -> Dict[str, Any]:
        """
        Send a conversation report via email
        
        Args:
            to_email: Recipient email address
            conversation_id: The conversation ID
            pdf_bytes: PDF file bytes
            metadata: Additional metadata about the conversation
            account_id: The account ID for tracking
            
        Returns:
            Dict containing the email sending result
        """
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"Loan Application Analysis Report - {account_id or 'Customer'}"
            
            # Create email body
            body = self._create_email_body(conversation_id, metadata, account_id)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach PDF
            pdf_attachment = MIMEBase('application', 'pdf')
            pdf_attachment.set_payload(pdf_bytes)
            encoders.encode_base64(pdf_attachment)
            pdf_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename=conversation_report_{conversation_id}.pdf'
            )
            msg.attach(pdf_attachment)
            
            # Send email
            # Configure SMTP connection based on port
            if self.smtp_port == 465:
                # SSL connection for port 465
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=True,  # Use SSL from the start
                    timeout=30.0
                ) as smtp:
                    await smtp.login(self.smtp_username, self.smtp_password)
                    await smtp.send_message(msg)
            else:
                # STARTTLS connection for port 587
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    timeout=30.0
                ) as smtp:
                    await smtp.connect()
                    await smtp.starttls()
                    await smtp.login(self.smtp_username, self.smtp_password)
                    await smtp.send_message(msg)
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {to_email}",
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                "status": "error",
                "error": f"Email sending failed: {str(e)}"
            }

    def _create_email_body(
        self,
        conversation_id: str,
        metadata: Dict[str, Any],
        account_id: str = None
    ) -> str:
        """Create the email body HTML content with business summary"""
        
        # Extract business summary from parsed data
        from models.openai_response_models import OpenAIStructuredResponse
        
        parsed_summary = metadata.get('parsed_summary')
        customer_name = account_id or 'Customer'
        business_name = 'Not specified'
        executive_summary = 'Analysis completed successfully.'
        
        if parsed_summary:
            try:
                if isinstance(parsed_summary, OpenAIStructuredResponse):
                    # Handle Pydantic model
                    if parsed_summary.customer_info:
                        customer_name = parsed_summary.customer_info.name or customer_name
                        business_name = parsed_summary.customer_info.business_name or business_name
                    
                    if parsed_summary.executive_summary:
                        executive_summary = parsed_summary.executive_summary.overview or executive_summary
                elif isinstance(parsed_summary, dict):
                    # Handle dictionary (fallback)
                    customer_info = parsed_summary.get('customer_info', {})
                    customer_name = customer_info.get('name', customer_name)
                    business_name = customer_info.get('business_name', business_name)
                    
                    exec_summary_data = parsed_summary.get('executive_summary', {})
                    if exec_summary_data:
                        executive_summary = exec_summary_data.get('overview', executive_summary)
            except Exception as e:
                logger.warning(f"Error extracting summary data for email: {e}")
                # Use defaults
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .content {{ padding: 20px; }}
                .metadata {{ background-color: #f1f3f4; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 12px; color: #666; }}
                .highlight {{ color: #007bff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Conversation Analysis Report</h2>
                <p>Your conversation analysis report is ready for review.</p>
            </div>
            
            <div class="content">
                <h3>Customer Information</h3>
                <ul>
                    <li><strong>Customer Name:</strong> <span class="highlight">{customer_name}</span></li>
                    <li><strong>Business Name:</strong> {business_name}</li>
                    <li><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                </ul>
                
                <div class="metadata">
                    <h4>Executive Summary</h4>
                    <p style="margin: 10px 0; line-height: 1.6;">{executive_summary}</p>
                </div>
                
                <p><strong>The attached PDF report contains:</strong></p>
                <ul>
                    <li>Detailed income breakdown with calculations</li>
                    <li>Comprehensive expense analysis</li>
                    <li>Loan disbursement requirements and repayment capacity</li>
                    <li>Risk assessment and recommendations</li>
                    <li>Complete conversation transcript</li>
                </ul>
                
                <p style="margin-top: 20px;"><em>Please review the attached PDF for complete financial details and analysis.</em></p>
            </div>
            
            <div class="footer">
                <p>This report was generated automatically by the FedFina Postprocess API.</p>
                <p>If you have any questions, please contact support.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body

    async def send_simple_report(
        self,
        to_email: str,
        conversation_id: str,
        pdf_bytes: bytes,
        summary: str
    ) -> Dict[str, Any]:
        """
        Send a simple conversation report via email
        
        Args:
            to_email: Recipient email address
            conversation_id: The conversation ID
            pdf_bytes: PDF file bytes
            summary: Brief summary of the conversation
            
        Returns:
            Dict containing the email sending result
        """
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"Loan Application Analysis Report - {account_id or 'Customer'}"
            
            # Create simple email body
            body = f"""
            <html>
            <body>
                <h2>Conversation Report</h2>
                <p>Your conversation analysis report is ready.</p>
                
                <h3>Summary</h3>
                <p>{summary}</p>
                
                <p>The attached PDF contains the complete conversation transcript and analysis.</p>
                
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach PDF
            pdf_attachment = MIMEBase('application', 'pdf')
            pdf_attachment.set_payload(pdf_bytes)
            encoders.encode_base64(pdf_attachment)
            pdf_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename=conversation_report_{conversation_id}.pdf'
            )
            msg.attach(pdf_attachment)
            
            # Send email
            # Configure SMTP connection based on port
            if self.smtp_port == 465:
                # SSL connection for port 465
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=True,  # Use SSL from the start
                    timeout=30.0
                ) as smtp:
                    await smtp.login(self.smtp_username, self.smtp_password)
                    await smtp.send_message(msg)
            else:
                # STARTTLS connection for port 587
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    timeout=30.0
                ) as smtp:
                    await smtp.connect()
                    await smtp.starttls()
                    await smtp.login(self.smtp_username, self.smtp_password)
                    await smtp.send_message(msg)
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {to_email}",
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending simple email: {e}")
            return {
                "status": "error",
                "error": f"Email sending failed: {str(e)}"
            }

    async def test_email_connection(self) -> Dict[str, Any]:
        """
        Test email service connection
        
        Returns:
            Dict containing the test result
        """
        try:
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=(self.smtp_port != 465),  # True for TLS (587), False for SSL (465)
                timeout=10.0
            ) as smtp:
                await smtp.connect()
                await smtp.login(self.smtp_username, self.smtp_password)
                await smtp.quit()
            
            return {
                "status": "success",
                "message": "Email service connection successful"
            }
            
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return {
                "status": "error",
                "error": f"Email connection failed: {str(e)}"
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check email service health
        
        Returns:
            Health status dictionary
        """
        try:
            # Test SMTP connection
            connection_result = await self.test_email_connection()
            
            if connection_result.get("status") == "success":
                return {
                    "status": "healthy",
                    "message": "Email service working correctly"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Email service error: {connection_result.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Email service health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Email service error: {str(e)}"
            }

    async def validate_email_address(self, email: str) -> Dict[str, Any]:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            import re
            
            # Basic email validation regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if re.match(email_pattern, email):
                return {
                    "status": "success",
                    "valid": True,
                    "message": "Email address format is valid"
                }
            else:
                return {
                    "status": "error",
                    "valid": False,
                    "message": "Email address format is invalid"
                }
                
        except Exception as e:
            logger.error(f"Email validation failed: {e}")
            return {
                "status": "error",
                "valid": False,
                "error": f"Email validation failed: {str(e)}"
            }
