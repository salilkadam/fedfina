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
    """Service for sending emails with download links"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.from_email = settings.smtp_from_email
        self.bcc_email = settings.smtp_use_cc

    async def send_conversation_report(
        self,
        to_email: str,
        conversation_id: str,
        account_id: str,
        files: Dict[str, str],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a conversation report via email with download links
        
        Args:
            to_email: Recipient email address
            conversation_id: The conversation ID
            account_id: The account ID for file organization
            files: Dictionary containing file URLs
            metadata: Additional metadata about the conversation
            
        Returns:
            Dict containing the email sending result
        """
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"Conversation Analysis Report - {account_id or 'Customer'}"
            
            # Add BCC if configured
            if self.bcc_email:
                msg['Bcc'] = self.bcc_email
                logger.info(f"Adding BCC to: {self.bcc_email}")
            
            # Create email body with download links
            body = self._create_email_body_with_links(conversation_id, account_id, files, metadata)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email using synchronous SMTP in executor
            import smtplib
            import ssl
            import asyncio
            
            def send_email_sync():
                """Synchronous email sending function"""
                if self.smtp_port == 465:
                    # SSL connection for port 465
                    context = ssl.create_default_context()
                    smtp = smtplib.SMTP_SSL(
                        self.smtp_host,
                        self.smtp_port,
                        context=context,
                        timeout=30.0
                    )
                    smtp.login(self.smtp_username, self.smtp_password)
                    smtp.send_message(msg)
                    smtp.quit()
                else:
                    # STARTTLS connection for port 587
                    smtp = smtplib.SMTP(
                        self.smtp_host,
                        self.smtp_port,
                        timeout=30.0
                    )
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(self.smtp_username, self.smtp_password)
                    smtp.send_message(msg)
                    smtp.quit()
            
            # Run synchronous SMTP in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, send_email_sync)
            
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

    def _create_email_body_with_links(
        self,
        conversation_id: str,
        account_id: str,
        files: Dict[str, str],
        metadata: Dict[str, Any]
    ) -> str:
        """Create the email body HTML content with download links"""
        
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
        
        # Generate secure download links using tokens
        base_url = f"https://fedfina.bionicaisolutions.com/api/v1/download/secure"
        
        # Import the token generation function
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import generate_download_token
        
        # Create download links for each file type
        download_links = {}
        
        if 'transcript' in files:
            token = generate_download_token(conversation_id, account_id, 'transcript')
            download_links['transcript'] = f"{base_url}/{token}"
        
        if 'pdf' in files or 'report' in files:
            token = generate_download_token(conversation_id, account_id, 'report')
            download_links['report'] = f"{base_url}/{token}"
        
        if 'audio' in files:
            token = generate_download_token(conversation_id, account_id, 'audio')
            download_links['audio'] = f"{base_url}/{token}"
        
        # Create the download links HTML
        download_links_html = ""
        if download_links:
            download_links_html = """
            <div class="download-section">
                <h3>Download Your Files</h3>
                <p>Click on the links below to download your conversation files:</p>
                <div class="download-links">
            """
            
            if 'transcript' in download_links:
                download_links_html += f"""
                    <div class="download-item">
                        <a href="{download_links['transcript']}" class="download-button">
                            📄 Download Transcript (TXT)
                        </a>
                        <p class="download-description">Complete conversation transcript in text format</p>
                    </div>
                """
            
            if 'report' in download_links:
                download_links_html += f"""
                    <div class="download-item">
                        <a href="{download_links['report']}" class="download-button">
                            📊 Download Report (PDF)
                        </a>
                        <p class="download-description">Detailed analysis report with financial insights</p>
                    </div>
                """
            
            if 'audio' in download_links:
                download_links_html += f"""
                    <div class="download-item">
                        <a href="{download_links['audio']}" class="download-button">
                            🎵 Download Audio (MP3)
                        </a>
                        <p class="download-description">Original conversation audio recording</p>
                    </div>
                """
            
            download_links_html += """
                </div>
                <div class="download-note">
                    <p><strong>Security Note:</strong> These links are secure and will expire after 24 hours or after first use. No authentication required.</p>
                </div>
            </div>
            """
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metadata {{ background-color: #f1f3f4; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 12px; color: #666; text-align: center; }}
                .highlight {{ color: #007bff; font-weight: bold; }}
                .download-section {{ background-color: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .download-links {{ display: flex; flex-direction: column; gap: 15px; }}
                .download-item {{ text-align: center; }}
                .download-button {{ 
                    display: inline-block; 
                    background-color: #007bff; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    font-weight: bold;
                    transition: background-color 0.3s;
                }}
                .download-button:hover {{ background-color: #0056b3; }}
                .download-description {{ margin-top: 5px; font-size: 14px; color: #666; }}
                .download-note {{ 
                    background-color: #fff3cd; 
                    border: 1px solid #ffeaa7; 
                    padding: 10px; 
                    border-radius: 3px; 
                    margin-top: 15px;
                    font-size: 12px;
                }}
                .file-info {{ 
                    background-color: #d4edda; 
                    border: 1px solid #c3e6cb; 
                    padding: 10px; 
                    border-radius: 3px; 
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🎉 Conversation Analysis Complete!</h2>
                <p>Your conversation has been processed and analyzed successfully.</p>
            </div>
            
            <div class="content">
                <h3>Customer Information</h3>
                <ul>
                    <li><strong>Customer Name:</strong> <span class="highlight">{customer_name}</span></li>
                    <li><strong>Business Name:</strong> {business_name}</li>
                    <li><strong>Conversation ID:</strong> {conversation_id}</li>
                    <li><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                </ul>
                
                <div class="metadata">
                    <h4>Executive Summary</h4>
                    <p style="margin: 10px 0; line-height: 1.6;">{executive_summary}</p>
                </div>
                
                <div class="file-info">
                    <h4>Generated Files</h4>
                    <p>The following files have been created for your conversation:</p>
                    <ul>
                        <li><strong>Transcript:</strong> Complete conversation in text format</li>
                        <li><strong>Report:</strong> Detailed PDF analysis with financial insights</li>
                        <li><strong>Audio:</strong> Original conversation recording</li>
                    </ul>
                </div>
                
                {download_links_html}
                
                <div class="metadata">
                    <h4>What's Included in Your Report</h4>
                    <ul>
                        <li>Detailed income breakdown with calculations</li>
                        <li>Comprehensive expense analysis</li>
                        <li>Loan disbursement requirements and repayment capacity</li>
                        <li>Risk assessment and recommendations</li>
                        <li>Complete conversation transcript</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>This report was generated automatically by the FedFina Postprocess API.</p>
                <p>If you have any questions or need assistance, please contact our support team.</p>
                <p><small>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</small></p>
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
            
            # Add BCC if configured
            if self.bcc_email:
                msg['Bcc'] = self.bcc_email
                logger.info(f"Adding BCC to: {self.bcc_email}")
            
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
            # Configure SMTP connection based on port
            if self.smtp_port == 465:
                # SSL connection for port 465
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=True,  # Use SSL from the start
                    timeout=10.0
                ) as smtp:
                    await smtp.login(self.smtp_username, self.smtp_password)
            else:
                # STARTTLS connection for port 587
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    timeout=10.0
                ) as smtp:
                    await smtp.connect()
                    await smtp.starttls()
                    await smtp.login(self.smtp_username, self.smtp_password)
            
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
