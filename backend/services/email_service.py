"""
Email Service for sending PDF reports using Postfix SMTP relay
"""
import logging
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
from config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with download links using Postfix SMTP relay"""

    def __init__(self, settings: Settings):
        # Use Postfix SMTP relay configuration
        self.smtp_host = "postfix-relay.email-server-prod.svc.cluster.local"
        self.smtp_port = 25
        self.from_email = "info@bionicaisolutions.com"
        self.settings = settings

        # Rate limiting configuration from settings
        self.rate_limit_calls_per_minute = getattr(settings, 'smtp_rate_limit_per_minute', 30)
        self.rate_limit_last_called = [0.0]

        logger.info(f"Email service initialized with Postfix relay: {self.smtp_host}:{self.smtp_port}")

    def rate_limit(self, func):
        """Decorator to implement rate limiting"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - self.rate_limit_last_called[0]
            left_to_wait = 60.0 / self.rate_limit_calls_per_minute - elapsed
            if left_to_wait > 0:
                logger.info(f"Rate limiting: waiting {left_to_wait:.2f} seconds")
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            self.rate_limit_last_called[0] = time.time()
            return ret
        return wrapper

    def validate_email_address(self, email: str) -> bool:
        """Validate email address format"""
        try:
            import re
            # Basic email validation regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, email):
                # Additional validation for common issues
                if '..' in email or email.startswith('.') or email.endswith('.'):
                    return False
                return True
            return False
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            return False

    def send_email_with_retry(self, msg: MIMEMultipart, max_retries: int = 3) -> Dict[str, Any]:
        """Send email with retry mechanism and exponential backoff"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to send email (attempt {attempt + 1}/{max_retries})")

                # Connect to Postfix SMTP relay (no authentication required)
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30.0)
                server.send_message(msg)
                server.quit()

                logger.info("Email sent successfully")
                return {
                    "status": "success",
                    "message": "Email sent successfully",
                    "attempts": attempt + 1
                }

            except smtplib.SMTPException as e:
                logger.warning(f"SMTP error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to send email after {max_retries} attempts")
                    return {
                        "status": "error",
                        "error": f"SMTP error: {str(e)}",
                        "attempts": attempt + 1
                    }
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Unexpected error sending email: {e}")
                return {
                    "status": "error",
                    "error": f"Unexpected error: {str(e)}",
                    "attempts": attempt + 1
                }

        return {
            "status": "error",
            "error": "Maximum retries exceeded",
            "attempts": max_retries
        }

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
            # Check if email sending is disabled for testing
            if self.settings.disable_email_sending:
                logger.info(f"Email sending disabled for testing. Would send to: {to_email}")
                return {
                    "status": "success",
                    "message": "Email sending disabled for testing",
                    "to_email": to_email,
                    "conversation_id": conversation_id,
                    "account_id": account_id
                }

            # Validate email address
            if not self.validate_email_address(to_email):
                logger.error(f"Invalid email address: {to_email}")
                return {
                    "status": "error",
                    "error": f"Invalid email address: {to_email}",
                    "conversation_id": conversation_id
                }

            logger.info(f"Sending conversation report to {to_email} for conversation {conversation_id}")

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"Conversation Analysis Report - {account_id or 'Customer'}"

            # Create email body with download links
            body = self._create_email_body_with_links(conversation_id, account_id, files, metadata)
            msg.attach(MIMEText(body, 'html'))

            # Apply rate limiting and send email
            rate_limited_send = self.rate_limit(self.send_email_with_retry)
            result = rate_limited_send(msg)

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Email sent successfully to {to_email}",
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat(),
                    "attempts": result.get("attempts", 1)
                }
            else:
                return {
                    "status": "error",
                    "error": result["error"],
                    "conversation_id": conversation_id,
                    "attempts": result.get("attempts", 0)
                }

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                "status": "error",
                "error": f"Email sending failed: {str(e)}",
                "conversation_id": conversation_id
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
                    <p><strong>Security Note:</strong> These links are secure and will expire after 24 hours or after 10 downloads. No authentication required.</p>
                </div>
            </div>
            """
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; 
                    color: #1f2937; 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background-color: #f9fafb;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px 20px; 
                    border-radius: 12px 12px 0 0; 
                    text-align: center; 
                    margin-bottom: 0;
                }}
                .content {{ 
                    padding: 30px 20px; 
                    background-color: white; 
                    border-radius: 0 0 12px 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                }}
                .metadata {{ 
                    background-color: #f3f4f6; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 20px 0; 
                    border-left: 4px solid #3b82f6;
                }}
                .footer {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    font-size: 12px; 
                    color: #6b7280; 
                    text-align: center; 
                    margin-top: 20px;
                    border: 1px solid #e5e7eb;
                }}
                .highlight {{ color: #3b82f6; font-weight: 600; }}
                .download-section {{ 
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                    padding: 25px; 
                    border-radius: 12px; 
                    margin: 25px 0; 
                    border: 1px solid #93c5fd;
                }}
                .download-links {{ display: flex; flex-direction: column; gap: 15px; }}
                .download-item {{ text-align: center; }}
                .download-button {{ 
                    display: inline-block; 
                    background-color: #2563eb; 
                    color: #ffffff; 
                    padding: 15px 30px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    font-weight: 600;
                    font-size: 16px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    border: 2px solid #1d4ed8;
                    transition: all 0.3s ease;
                }}
                .download-button:hover {{ 
                    background-color: #1d4ed8; 
                    transform: translateY(-1px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }}
                .download-description {{ margin-top: 5px; font-size: 14px; color: #666; }}
                .download-note {{ 
                    background-color: #fef3c7; 
                    border: 1px solid #f59e0b; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin-top: 20px;
                    font-size: 13px;
                    color: #92400e;
                }}
                .file-info {{ 
                    background-color: #d1fae5; 
                    border: 1px solid #10b981; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 15px 0;
                    color: #065f46;
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
        account_id: str,
        pdf_bytes: bytes,
        summary: str
    ) -> Dict[str, Any]:
        """
        Send a simple conversation report via email with PDF attachment

        Args:
            to_email: Recipient email address
            conversation_id: The conversation ID
            account_id: The account ID
            pdf_bytes: PDF file bytes
            summary: Brief summary of the conversation

        Returns:
            Dict containing the email sending result
        """
        try:
            # Check if email sending is disabled for testing
            if self.settings.disable_email_sending:
                logger.info(f"Email sending disabled for testing. Would send to: {to_email}")
                return {
                    "status": "success",
                    "message": "Email sending disabled for testing",
                    "to_email": to_email,
                    "conversation_id": conversation_id
                }

            # Validate email address
            if not self.validate_email_address(to_email):
                logger.error(f"Invalid email address: {to_email}")
                return {
                    "status": "error",
                    "error": f"Invalid email address: {to_email}",
                    "conversation_id": conversation_id
                }

            logger.info(f"Sending simple report to {to_email} for conversation {conversation_id}")

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

            # Apply rate limiting and send email
            rate_limited_send = self.rate_limit(self.send_email_with_retry)
            result = rate_limited_send(msg)

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": f"Email sent successfully to {to_email}",
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat(),
                    "attempts": result.get("attempts", 1)
                }
            else:
                return {
                    "status": "error",
                    "error": result["error"],
                    "conversation_id": conversation_id,
                    "attempts": result.get("attempts", 0)
                }

        except Exception as e:
            logger.error(f"Error sending simple email: {e}")
            return {
                "status": "error",
                "error": f"Email sending failed: {str(e)}",
                "conversation_id": conversation_id
            }

    def test_email_connection(self) -> Dict[str, Any]:
        """
        Test email service connection to Postfix relay

        Returns:
            Dict containing the test result
        """
        try:
            logger.info("Testing connection to Postfix SMTP relay...")

            # Test connection to Postfix SMTP relay (no authentication required)
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10.0)
            server.quit()

            logger.info("Email service connection test successful")
            return {
                "status": "success",
                "message": "Email service connection successful",
                "relay_host": self.smtp_host,
                "relay_port": self.smtp_port
            }

        except smtplib.SMTPException as e:
            logger.error(f"SMTP connection test failed: {e}")
            return {
                "status": "error",
                "error": f"SMTP connection failed: {str(e)}",
                "relay_host": self.smtp_host,
                "relay_port": self.smtp_port
            }
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return {
                "status": "error",
                "error": f"Email connection failed: {str(e)}",
                "relay_host": self.smtp_host,
                "relay_port": self.smtp_port
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Check email service health

        Returns:
            Health status dictionary
        """
        try:
            # Test SMTP connection
            connection_result = self.test_email_connection()

            if connection_result.get("status") == "success":
                return {
                    "status": "healthy",
                    "message": "Email service working correctly",
                    "relay_host": self.smtp_host,
                    "relay_port": self.smtp_port,
                    "rate_limit": f"{self.rate_limit_calls_per_minute} calls/minute",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Email service error: {connection_result.get('error')}",
                    "relay_host": self.smtp_host,
                    "relay_port": self.smtp_port,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Email service health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Email service error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get email service metrics

        Returns:
            Dict containing service metrics
        """
        return {
            "service": "Postfix SMTP Relay",
            "relay_host": self.smtp_host,
            "relay_port": self.smtp_port,
            "from_email": self.from_email,
            "rate_limit_calls_per_minute": self.rate_limit_calls_per_minute,
            "last_rate_limit_check": datetime.fromtimestamp(self.rate_limit_last_called[0]).isoformat() if self.rate_limit_last_called[0] > 0 else None,
            "timestamp": datetime.now().isoformat()
        }
